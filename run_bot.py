from bot.bot import Bot
from infrastructure.instrument_collection import instrumentCollection

if __name__ == '__main__':
    instrumentCollection.LoadInstruments('./data')
    print("Running Bot")
    bot = Bot()
    bot.run()