from api.oanda_api import OandaAPI
from models.candle_timing import CandleTiming

class CandleManager:

    def __init__(self, api: OandaAPI, trade_settings, log_message, granularity):
        self.api = api
        self.trade_settings = trade_settings
        self.log_message = log_message
        self.granularity = granularity

        self.pair_list = list(self.trade_settings.keys())
        # print("Pair list is : ", self.pair_list)
        self.timings = {
            pair: CandleTiming(self.api.get_recent_candles(pair, self.granularity))
            for pair in self.pair_list
        }


        for k, v in self.timings.items():
            # print(f"Initial candle timing for {k}: {v}")
            self.log_message(f"Initial candle timing for {k}: {v}", k)

    def update_timings(self):
        triggered = []

        for pair in self.pair_list:
            current = self.api.get_recent_candles(pair, self.granularity)
            # print("Pair is : ", pair)
            if current is None:
                self.log_message("Unable to get candle", pair)
                continue
            self.timings[pair].is_ready = False
            if current > self.timings[pair].last_time:
                # print("Last time is : " , self.timings[pair].last_time, self.timings[pair].is_ready)
                self.timings[pair].is_ready = True
                self.timings[pair].last_time = current
                # print("Type of current is : ", type(current), "Type of time is : ", type(self.timings[pair].last_time))
                self.log_message(f"CandleManager() new candle:{self.timings[pair]}", pair)
                triggered.append(pair)

        return triggered

        