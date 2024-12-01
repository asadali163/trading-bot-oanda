import pandas as pd
import os.path
from infrastructure.instrument_collection import instrumentCollection as ic

class MAResult:
    def __init__(self, df_trades, pairName, ma_l, ma_s, granularity):
        self.df_trades = df_trades
        self.pairName = pairName
        self.ma_l = ma_l
        self.ma_s = ma_s
        self.granularity = granularity
        self.result = self.get_result_obj()

    def __repr__(self):
        return str(self.result)

    def get_result_obj(self):
        return dict(
            pair = self.pairName,
            num_trades = self.df_trades.shape[0],
            total_gain = int(self.df_trades.GAIN.sum()),
            mean_gain = int(self.df_trades.GAIN.mean()),
            max_gain = int(self.df_trades.GAIN.max()),
            min_gain = int(self.df_trades.GAIN.min()),
            ma_l = self.ma_l,
            ma_s = self.ma_s,
            cross = f"{self.ma_s}-{self.ma_l}",
            granularity = self.granularity
        )



BUY = 1
SELL = -1
NONE = 0
get_ma_col = lambda x : f"MA_{x}"
add_cross = lambda x: f"{x.ma_s}-{x.ma_l}"

def is_trade(row):
    if row["DELTA"] > 0 and row["DELTA_PREV"] < 0:
        return BUY
    elif row["DELTA"] < 0 and row["DELTA_PREV"] > 0:
        return SELL
    else:
        return NONE
    
def append_df_to_file(df, filename):
    if os.path.isfile(filename):
        fd = pd.read_pickle(filename)
        df = pd.concat([fd, df])

    df.reset_index(inplace=True, drop=True)
    df.to_pickle(filename)
    print(filename, df.shape)
    print(df.tail(2))


def get_fullname(filepath, filename):
    return f"{filepath}/{filename}.pkl"

def process_macro(result_list, filename):
    rl = [x.result for x in result_list]
    df = pd.DataFrame.from_dict(rl)
    append_df_to_file(filename=filename,df=df)

def process_trades(result_list, filename):
    df = pd.concat([x.df_trades for x in result_list])
    append_df_to_file(df, filename=filename)

def process_results(results_list, filename):
    process_macro(result_list=results_list, filename=get_fullname(filename, 'ma_res'))
    process_trades(result_list=results_list, filename=get_fullname(filename, 'ma_trades'))
    # rl = [x.result for x in results_list]
    # df = pd.DataFrame.from_dict(rl)
    # print(df)
    # print(results_list[0].df_trades.head())

def get_trades(df_analysis, instruments, granularity):
    df_trades = df_analysis[df_analysis['TRADE'] != NONE].copy()
    df_trades['DIFF'] = df_trades.mid_c.diff().shift(-1)
    df_trades.fillna(0, inplace=True)
    df_trades['GAIN'] = (df_trades['DIFF'] / instruments.pipLocation) * df_trades['TRADE']
    df_trades['pair'] = instruments.name
    df_trades['granularity'] = granularity
    df_trades['CUM_GAIN'] = df_trades['GAIN'].cumsum()

    return df_trades

def asses_pair(df, long_col, short_col, instrument, granularity):
    df_analysis = df.copy()
    df_analysis["DELTA"] = df_analysis[short_col] - df_analysis[long_col]
    df_analysis["DELTA_PREV"] = df_analysis["DELTA"].shift(1)
    df_analysis["TRADE"] = df_analysis.apply(is_trade, axis=1)
    # print(instrument.name, short_col, long_col)
    df_trades =  get_trades(df_analysis, instrument, granularity=granularity)
    df_trades['ma_l'] = long_col
    df_trades['ma_s'] = short_col
    df_trades['cross'] = df_trades.apply(add_cross, axis=1)
    return MAResult(df_trades=df_trades, pairName=instrument.name, ma_l=long_col, ma_s=short_col, granularity=granularity)



def load_price_data(pair, granularity, ma_list):
    df = pd.read_pickle(f"./data/{pair}_{granularity}.pkl")
    for ma in ma_list:
        df[get_ma_col(ma)] = df.mid_c.rolling(window=ma).mean()
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)

    return df

def analyze_pair(instrument, granularity, ma_long, ma_short, filename):
    ma_list = set(ma_long + ma_short)
    results_list = []

    price_data = load_price_data(pair=instrument.name,granularity=granularity, ma_list=ma_list)
    
    for long in ma_long:
        for short in ma_short:
            if long <= short:
                continue

            result = asses_pair(price_data, get_ma_col(long), get_ma_col(short), instrument, granularity=granularity)
            # print(result)

            results_list.append(result)
    
    process_results(results_list=results_list, filename=filename)

def run_ma_sim(curr_list = ["EUR", "USD"],
               granularity=["H4"],
               ma_long=[20,50,100,200],
               ma_short=[5,10,20],
               filename='./data'):
    ic.LoadInstruments("./Data")
    instruments = ic.instruments_dict
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}_{p2}"
                if pair in instruments.keys():
                    analyze_pair(instrument=instruments[pair], granularity=g, ma_long=ma_long, ma_short=ma_short, filename=filename)
