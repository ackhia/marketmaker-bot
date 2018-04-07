

from logic import match
from wsclients.hitbtc import HitBtc
import uuid

class LiveExchange:
    def __init__(self, logic, pair):
        self.balance_quote = None
        self.balance_base = None
        self.callback = None
        self.client = HitBtc(self.datasource_callback)
        self.pair = "".join(pair).upper()
        self.base = pair[0].upper()
        self.quote = pair[1].upper()
        self.logic = logic
        logic.set_exchange(self)
        self.update_balances()


    def buy(self, amount, price):
        return self.client.buy(self.pair, price, amount)


    def sell(self, amount, price):
        return self.client.sell(self.pair, price, amount)


    def cancel_order(self, id):
        return self.client.cancel_order(id)


    def update_balances(self):
        self.client.update_balances()


    def calculate_balances(self):
        if len(self.client.balances) > 0:
            self.balance_quote = float(next(b for b in self.client.balances if b["currency"] == self.quote)["available"])
            self.balance_base = float(next(b for b in self.client.balances if b["currency"] == self.base)["available"])


    def get_bids(self):
        return self.client.bids


    def get_asks(self):
        return self.client.asks


    def datasource_callback(self, x):
        self.calculate_balances()

        if "method" in x:
            if x["method"] == "ticker":
                current_bid = float(x["params"]["bid"])
                current_ask = float(x["params"]["ask"])
                self.logic.update_price(current_bid, current_ask)

            elif x["method"] == "report":
                if x["params"]["status"] == "filled":
                    if x["params"]["side"] == "buy":
                        self.logic.bid_executed(x["params"]["clientOrderId"])
                    elif x["params"]["side"] == "sell":
                        self.logic.ask_executed(x["params"]["clientOrderId"])


    def start(self):
        self.client.monitor(True, True, self.pair)


if __name__ == "__main__":
    logic = match.Match()
    e = LiveExchange(logic, ["DOGE","USD"])
    e.start()
