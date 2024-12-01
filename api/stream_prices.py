import json
import constants.defs as defs
import requests
from models.live_api_price import LiveAPIPrice
import threading 
from infrastructure.log_wrapper import LogWrapper

class PriceStreamer(threading.Thread):

    def __init__(self, shared_prices, price_lock: threading.Lock, price_events):
        super().__init__()
        self.pair_list = shared_prices.keys()
        self.price_lock = price_lock
        self.shared_prices = shared_prices
        self.price_events = price_events
        self.log = LogWrapper("Price Streamer")
        print("Pairs list is : ", self.pair_list)

    def run(self):

        base_url = 'https://stream-fxpractice.oanda.com/v3'

        params = dict(
            instruments=','.join(self.pair_list),
        )

        url = f'{base_url}/accounts/{defs.ID}/pricing/stream'

        response = requests.get(url, headers=defs.SECURE_HEADER, params=params, stream=True)

        for price in response.iter_lines():
            if price:
                decoded_prices = json.loads(price.decode('utf-8'))
                if 'type' in decoded_prices.keys() and decoded_prices['type'] == 'PRICE':
                    print(LiveAPIPrice(decoded_prices))


