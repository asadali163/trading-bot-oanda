import json
from models.instrument import Instrument
from constants.defs import CANDLE_COUNT, INCREMENTS
import pandas as pd
from dateutil import parser
import datetime as dt
import os

class InstrumentCollection():
    FILE_NAME = "instruments.json"
    API_KEYS = ["name", "type", "displayName", "pipLocation", "displayPrecision", "tradeUnitsPrecision", "marginRate"]

    def __init__(self):
        self.instruments_dict = {}

    def LoadInstruments(self, path):
        self.instruments_dict = {}
        fileName = f"{path}/{self.FILE_NAME}"
        with open(fileName, "r") as f:
            data = json.load(f)
            for key, value in data.items():
                self.instruments_dict[key] = Instrument.FromAPIObject(value)

    def CreateFile(self, data, path):
        instruments_dict = {}
        # print("Data: ", data)
        # print("Data: ", data)
        for i in data['instruments']:
            key = i['name']
            instruments_dict[key] = {k: i[k] for k in self.API_KEYS}

        fileName = f"{path}/{self.FILE_NAME}"
        with open(fileName, "w") as f:
            f.write(json.dumps(instruments_dict, indent=2))

    def printInstruments(self):
        [print(k, v) for k, v in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()))

    
    def __create_data_frame(self, data):
        if data is None:
            return None
        if len(data) == 0:
            return pd.DataFrame()
        
        prices = ['mid', 'bid', 'ask']
        ohlc = ['o','h','l','c']
        final_data = []
        for candle in data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle.keys():
                    for o in ohlc:
                        new_dict[f"{p}_{o}"] = float(candle[p][o])
            
            final_data.append(new_dict)
        df = pd.DataFrame.from_dict(final_data)
        return df
    
    def create_data_file(self,api, pair_name="EUR_USD", granularity="H1", count=500, from_date=None, to_date=None, price="MBA"):      
        try:
            time_step = INCREMENTS[granularity]

            end_date = parser.parse(to_date)
            from_date = parser.parse(from_date)

            candle_df = []

            to_date = from_date

            while to_date < end_date:
                to_date = from_date + dt.timedelta(minutes=time_step)
                if to_date > end_date:
                    to_date = end_date

                data = api.get_instrument_candles(pair_name, granularity=granularity, count=count, from_date=from_date, to_date=to_date, price=price)
                candles = self.__create_data_frame(data['candles'])

                from_date = to_date

                if candles is not None and candles.empty == False:
                    candle_df.append(candles)
                    print("Done")
                else:
                    print(f"Error: {pair_name} {granularity} {from_date} {to_date} -- No Candles")

            if len(candle_df) > 0:
                df = pd.concat(candle_df)
                print(f"Prices: {len(df)}")
                df.drop_duplicates(subset=['time'], inplace=True)
                df.sort_values(by=['time'], inplace=True)
                df.reset_index(drop=True, inplace=True) 
                df.to_pickle(f"./data/{pair_name}_{granularity}.pkl")
            
        except Exception as e:
            print("Error here is instrument collection: ", e)
        print("Successful")
            

instrumentCollection = InstrumentCollection()