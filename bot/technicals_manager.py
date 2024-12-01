import pandas as pd

from dateutil import parser

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

from api.oanda_api import OandaAPI
from models.trade_settings import TradeSettings
from constants.defs import BUY, SELL, NONE
from technicals.indicators import BollingerBands
from models.trade_decision import TradeDecision


def apply_signal(row, trade_settings: TradeSettings):
    if row.SPREAD <= trade_settings.maxspread and row.GAIN >= trade_settings.mingain:
        if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
            return SELL
        elif row.mid_c < row.BB_DOWN and row.mid_o > row.BB_DOWN:
            return BUY
    return NONE

def apply_SL(row, trade_settings: TradeSettings):
    if row.SIGNAL == BUY:
        return row.mid_c - (row.GAIN / trade_settings.riskreward)
    elif row.SIGNAL == SELL:
        return row.mid_c + (row.GAIN / trade_settings.riskreward)
    return 0.0


def apply_TP(row):
    
    if row.SIGNAL == BUY:
        return row.mid_c + row.GAIN
    elif row.SIGNAL == SELL:
        return row.mid_c - row.GAIN
    return 0.0


def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):

    # df = pd.DataFrame(df)
    prices = ['mid', 'bid', 'ask']
    ohlc = ['o','h','l','c']
    final_data = []
    for _, candle in df.iterrows():
        # if candle['complete'] == False:
        #     continue
        new_dict = {}
        new_dict['time'] = parser.parse(candle['time'])
        # new_dict['time'] = candle['time']
        new_dict['volume'] = candle['volume']
        for p in prices:
            if p in candle.keys():
                for o in ohlc:
                    new_dict[f"{p}_{o}"] = float(candle[p][o])
            
        final_data.append(new_dict)
    df = pd.DataFrame.from_dict(final_data)    



    df.reset_index(inplace=True, drop=True)
    df['PAIR'] = pair
    df["SPREAD"] = df['ask_c'] - df['bid_c']

    df = BollingerBands(df, trade_settings.n_ma, trade_settings.n_std)
    # print(df.head(1))
    df['GAIN'] = abs(df.mid_c - df.BB_MA)
    df['SIGNAL'] = df.apply(apply_signal, axis=1, trade_settings=trade_settings)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['TP'] = df.apply(apply_TP, axis=1)
    df['LOSS'] = abs(df.mid_c - df.SL) 

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o','SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    log_message(f"\n Process Candles: {df[log_cols].tail()}", pair)

    return df.iloc[-1]

def fetch_candles(pair, row_count, candle_time, granularity, api:OandaAPI, log_message):
    df_temp = api.get_instrument_candles(pair, count = row_count, granularity = granularity)

    df = pd.DataFrame(df_temp['candles'])
    if df is None or df.shape[0] == 0:
        log_message(f"tech manager fetch_candles failed to fetch candles", pair)


    if df.iloc[-1]['time'] != candle_time:
        log_message(f"tech manager fetch_candles {df.iloc[-1]['time']} time mismatch", pair)

    return df

ADDROWS = 20
def get_trade_decision(candle_time, pair, granularity, api:OandaAPI, trade_settings: TradeSettings, log_message):

    max_rows = trade_settings.n_ma + ADDROWS

    log_message(f"get_trade_decision() max rows: {max_rows} for {pair} granularity: {granularity} candle_time: {candle_time}", pair)

    df = fetch_candles(pair, max_rows, candle_time, granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        if last_row.SIGNAL != NONE:
            return TradeDecision(last_row)

    return None