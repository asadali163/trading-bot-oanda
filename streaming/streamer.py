import json
import threading 
import time
from api.stream_prices import PriceStreamer

def load_settings():
    with open('./bot/settings.json', 'r') as f:
        return json.loads(f.read())


def run_streamer():
    settings = load_settings()

    shared_prices = {}
    shared_prices_events = {}
    shared_prices_locks = threading.Lock()

    for p in settings['pairs']:
        shared_prices[p] = {}
        shared_prices_events[p] = threading.Event()


    threads = []

    prices_stream_t = PriceStreamer(shared_prices, shared_prices_locks, shared_prices_events)
    prices_stream_t.daemon = True
    threads.append(prices_stream_t)
    prices_stream_t.start()

    # for t in threads:
    #     t.join()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Keyboard Interrupted")
        # for e in shared_prices_events:
        #     e.set()
        # for t in threads:
        #     t.join()

    print("All Done")