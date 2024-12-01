from api.oanda_api import OandaAPI
from models.trade_decision import TradeDecision
from bot.trade_risk_calculator import get_trade_units


def is_trade_open(pair, api:OandaAPI):
    open_trades = api.get_open_trades()
    for trade in open_trades:
        if trade.instrument == pair:
            return trade
    return None


def place_trade(trade_decision: TradeDecision, api:OandaAPI, log_message, log_error, trade_risk):
    ot = is_trade_open(trade_decision.pair, api)

    if ot is not None:
        log_message(f"Failed to place trade {trade_decision}, already open {ot}", trade_decision.pair)
        return None
    
    trade_units = get_trade_units(api, trade_decision.pair, trade_decision.signal, trade_decision.loss,
                                  trade_risk, log_message)
    
    trade_id = api.place_order(trade_decision.pair, trade_units, trade_decision.signal,
                               trade_decision.sl, trade_decision.tp)
    
    print("Trade id is : ", trade_id)
    
    if trade_id is None:
        log_error(f"Error Placing Order {trade_decision}")
        log_message(f"Error Placing Order {trade_decision}", trade_decision.pair)

    else:
        log_message(f"Placed Order {trade_decision}", trade_decision.pair)
        # return trade_id
    