class LiveAPIPrice:

    def __init__(self, api_ob):
        self.instrument = api_ob['instrument']
        self.ask = float(api_ob['asks'][0]['price'])
        self.bid = float(api_ob['bids'][0]['price'])

    def __repr__(self):
        return f"LiveAPIPrice(): {self.instrument}, bid: {self.bid}, ask: {self.ask}"