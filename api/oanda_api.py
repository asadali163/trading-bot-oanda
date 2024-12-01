import requests
from constants.defs import API_KEY, OANDA_URL, ID, BUY, SELL, NONE, SECURE_HEADER
from dateutil import parser
import json
from datetime import datetime as dt
from infrastructure.instrument_collection import instrumentCollection as ic
from models.open_trades import OpenTrade
from models.api_price import ApiPrice


class OandaAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SECURE_HEADER)

    def make_request(self,url,  verb='get', code=200, params=None, data=None, headers=None):
        full_url = f"{OANDA_URL}/{url}"
        
        if data is not None:
            data = json.dumps(data)

        try:
            response = None
            if verb == 'get':
                response = self.session.get(full_url, params=params)

            if verb == 'post':
                response = self.session.post(full_url, data=data)

            if verb == 'put':
                response = self.session.put(full_url)

            if response is None:
                return False, {"Error": "Verb not found"}  
            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()
                     
        except Exception as e:
            return False, {"Exception": str(e)}


    def get_account_ep(self, ep, data_type):
        url = f"accounts/{ID}/{ep}"
        success, response = self.make_request(url)
        if success:
            return response
        else:
            print("Error: ", response)
            return None
        
    def get_account_summary(self):
        return self.get_account_ep("summary", "accounts")
    
    def get_account_instruments(self):
        return self.get_account_ep("instruments", "accounts")
    
    def get_instrument_candles(self, pair_name,granularity='H1', count=500, price="MBA", from_date=None, to_date=None):
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity=granularity,
            price = price
        )
        if from_date is not None and to_date is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params['from'] = from_date.strftime(date_format)
            params['to'] = to_date.strftime(date_format)
        else:
            params['count'] = count

        # print("Params are: ", params)
        

        success, response = self.make_request(url, params=params)
        # print("Response is: ", response)
        if success:
            return response
        else:
            print("Error: in the file ", response)
            return None
        
    def get_recent_candles(self, pair_name, granularity):
        df = self.get_instrument_candles(pair_name, granularity=granularity, count=5)
        # print("DF is : ", df['candles'][-1]['time'])
        if df is not None:
            return df['candles'][-1]['time']
        else:
            return None

    ############### Placing Order #################   
    def place_order(self, pair_name:str, 
                    units:float, 
                    direction: int, 
                    stop_loss:float=None, 
                    take_profit:float=None):
        url = f'accounts/{ID}/orders'
        instrument = ic.instruments_dict[pair_name]
        units = round(units, instrument.tradeUnitsPrecision)
        
        if direction == SELL:
            units = units * -1
        
        data = dict(
            order = dict(
                units = str(units),
                instrument = pair_name,
                timeInForce = "FOK",
                type = "MARKET",
                positionFill = "DEFAULT"
            )
        )

        if stop_loss is not None:
            sld = round(stop_loss, instrument.displayPrecision)
            data['order']['stopLossOnFill'] = dict(
                price = str(sld)
            )

        if take_profit is not None:
            tpd = round(take_profit, instrument.displayPrecision)
            data['order']['takeProfitOnFill'] = dict(
                price = str(tpd)
            )          


        success, response = self.make_request(url, verb='post', data=data, code=201)

        if success and 'orderFillTransaction' in response.keys():
            print("Successfully placed an order")
            # print(response)
            return response['orderFillTransaction']['id']
        else:
            print("Error: ", response)
            return None
        
    ######### Closing Order #########
    def close_order(self, order_id):
        url = f'accounts/{ID}/trades/{order_id}/close'
        success, response = self.make_request(url, verb='put', code=200)
        if success:
            print("Successfully closed the order")
            return True
        else:
            print("Error: ", response)
            return False
       
    ######### Get All Open Trades #########
    def get_open_trades(self):
        url = f'accounts/{ID}/openTrades'
        success, response = self.make_request(url, code=200, verb='get')
        if success and 'trades' in response.keys():
            return [OpenTrade(trade) for trade in response['trades']]
        else:
            print("Error: ", response)
            return None
        
    ######## Get Single Trade ########
    def get_single_trade(self, trade_id):
        url = f'accounts/{ID}/trades/{trade_id}'
        success, response = self.make_request(url, code=200, verb='get')
        if success and 'trade' in response.keys():
            return OpenTrade(response['trade'])
        else:
            print("Error: ", response)
            return None

    ########### Get Prices ##########
    def get_prices(self, instrument_list):
        url = f"accounts/{ID}/pricing"

        params = dict(
            instruments = ','.join(instrument_list)
        )

        ok, response = self.make_request(url, params=params)

        if ok == True and 'prices' in response.keys():
            return [ApiPrice(x) for x in response['prices']]

        return None