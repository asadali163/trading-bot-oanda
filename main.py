from api.oanda_api import OandaAPI
from infrastructure.instrument_collection import instrumentCollection
# from exploration.plotting import CandlePlot
from simulation.ma_cross import run_ma_sim
# from constants.helper_fn import get_data
from infrastructure.collect import get_data
from constants.defs import curr_list, granularities
from dateutil import parser
from models.candle_timing import CandleTiming
from streaming.streamer import run_streamer


if __name__ == '__main__':
    api = OandaAPI()
    instrumentCollection.LoadInstruments('./data')
    # stream_prices(['USD_JPY', 'EUR_USD'])

    run_streamer()

    # dd = api.get_recent_candles("USD_JPY", "M5")
    # print(dd)
    # print(CandleTiming(dd['time']))








    # id = api.place_order('USD_JPY', 100, -1, take_profit=150.000)
    # print("Trade id is : ", id)

    # pairs = ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CHF']
    # i = 1
    # for pair in pairs:
    #     api.place_order(pair, 100, direction=i)
    #     i = -i

    # res = api.get_open_trades()
    # api.place_order("USD_JPY", 100, direction=1)
    # print(api.get_single_trade(117))
    # [api.close_order(i.id[0]) for i in api.get_open_trades()]




    # dfr = "2020-01-01T00:00:00Z"
    # dto = "2024-11-23T00:00:00Z"
    # instrumentCollection.create_data_file(api, pair_name="USD_JPY", granularity="M1", count=1000, price="MBA", from_date=dfr, to_date=dto)

    # data = api.get_instrument_candles("EUR_USD")
    # instrumentCollection.create_data_file(api, pair_name="EUR_USD", granularity="H1", count=500)

    # get_data(instrumentCollection, api, curr_list, granularities, 1000)


    # instrumentCollection.CreateFile(api.get_account_instruments(), "./data")
    # instrumentCollection.LoadInstruments("./data")
    # instrumentCollection.printInstruments()
    # cp = CandlePlot()
    # run_ma_sim(curr_list=curr_list, granularity=granularities, ma_long=[20, 50, 100, 200], ma_short=[5, 10, 20], filename='./data')
    # test_method()

