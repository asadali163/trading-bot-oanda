OANDA_URL = "https://api-fxpractice.oanda.com/v3"
API_KEY = "83408b92cdfee022ba7a5afac8696138-969e18ef786964fa39f81a43f94c0ac3"
ID = "101-004-30368907-001"

FINNHUB_API_KEY = "ct0tp61r01qkcukbibv0ct0tp61r01qkcukbibvg"

curr_list = ["EUR", "USD", "JPY", "GBP", "AUD", "XAU", "CHF", "CAD", "NZD"]
granularities = ["M15", "M30", "H1"]

CANDLE_COUNT = 4000

INCREMENTS = {
    "M1": 1 * CANDLE_COUNT,
    "M5": 5 * CANDLE_COUNT,
    "M15": 15 * CANDLE_COUNT,
    "M30": 30 * CANDLE_COUNT,
    "H1": 60 * CANDLE_COUNT,
    "H4": 240 * CANDLE_COUNT,
    "D": 1440 * CANDLE_COUNT,
}

SECURE_HEADER = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

BUY = 1
SELL = -1
NONE = 0