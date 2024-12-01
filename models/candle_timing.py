import datetime as dt
from dateutil import parser as ps

class CandleTiming:
    def __init__(self, last_time):
        # Initialize last_time (assuming it is a timestamp string)
        self.last_time = last_time
        self.is_ready = False

    def __repr__(self):
        return f"last candle: {dt.datetime.strftime(ps.isoparse(self.last_time), '%Y-%m-%dT%H:%M:%S.%fZ')} is_ready: {self.is_ready}"
