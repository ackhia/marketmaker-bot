

from data_source import csv_datasource
from logic import match
import datetime


class ExchangeSimulator:
    def __init__(self, datasource, logic):
        self.bids = []
        self.asks = []
        self.balance_quote = 1000
        self.balance_base = 0.1
        self.callback = None
        self.datasource = datasource
        self.logic = logic
        self.first_best_ask = None
        logic.set_exchange(self)


    def buy(self, id, amount, price):
        if self.balance_quote >= amount * price:
            self.balance_quote -= amount * price
            self.bids.append([id, amount, price])
            return True
        return False


    def sell(self, id, amount, price):
        if self.balance_base >= amount:
            self.balance_base -= amount
            self.asks.append([id, amount, price])
            return True
        return False


    def cancel_order(self, id, executed = False):
        updated_buy_orders = []
        updated_sell_orders = []

        for o in self.bids:
            if o[0] == id:
                if not executed:
                    self.balance_quote += o[1] * o[2]
            else:
                updated_buy_orders.append(o)

        for o in self.asks:
            if o[0] == id:
                if not executed:
                    self.balance_base += o[1]
            else:
                updated_sell_orders.append(o)

        self.bids = updated_buy_orders
        self.asks = updated_sell_orders


    def update_price(self, bid, ask):
        for b in self.bids:
            if b[2] >= ask:
                self.balance_base += b[1]
                self.cancel_order(b[0], True)
                self.logic.bid_executed(b[0])

        for s in self.asks:
            if s[2] <= bid:
                self.balance_quote += s[1] * s[2]
                self.cancel_order(s[0], True)
                self.logic.ask_executed(s[0])

        self.last_best_ask = ask
        self.logic.update_price(bid, ask)
        if self.first_best_ask is None:
            self.first_best_ask = ask


        #print(bid, ask, self.bids, self.asks)

    def execute_trade(self, side, price):
        if side == "sell":
            for b in self.bids:
                if b[2] >= price:
                    self.balance_base += b[1]
                    self.cancel_order(b[0], True)
                    self.logic.bid_executed(b[0])
        elif side == "buy":
            for s in self.asks:
                if s[2] <= price:
                    self.balance_quote += s[1] * s[2]
                    self.cancel_order(s[0], True)
                    self.logic.ask_executed(s[0])


    def datasource_callback(self, x):
        if "method" in x[1]:
            if x[1]["method"] == "ticker":
                current_bid = float(x[1]["params"]["bid"])
                current_ask = float(x[1]["params"]["ask"])
                self.update_price(current_bid, current_ask)

            elif x[1]["method"] == "updateTrades":
                data = x[1]["params"]["data"]
                for d in data:
                    self.execute_trade(d["side"], float(d["price"]))


    def get_account_balance_quote(self):
        balance = self.balance_quote
        balance += self.balance_base * self.last_best_ask

        for b in self.bids:
            balance += b[1] * self.last_best_ask

        for a in self.asks:
            balance += a[1] * self.last_best_ask

        return balance

    def __parse_datetime(self, str_date_time):
        return datetime.strptime(str_date_time.split(".")[0], "%Y-%m-%d %H:%M:%S")


    def start(self):
        self.datasource.subscribe(self.datasource_callback)


if __name__ == "__main__":
    """def callback(order, order_type):
        print(order, order_type)

    e = ExchangeSimulator()
    e.register_callback(callback)
    e.sell("12", 0.05, 10000)
    e.buy("10", 0.1, 6000)
    e.cancel_order("12")
    e.update_price(5954)
    print(e.balance_base, e.balance_quote)
    e.sell("11", 0.05, 7000)
    e.update_price(7524)
    print(e.balance_base, e.balance_quote)
    e.update_price(8252)"""

    logic = match.Match()
    ds = csv_datasource.CsvDatasource("../data/btcusd.csv")
    e = ExchangeSimulator(ds, logic)
    starting_balance_base = e.balance_base
    starting_balance_quote = e.balance_quote
    e.start()
    print("Starting balance: {}".format((e.first_best_ask * starting_balance_base) + starting_balance_quote))
    print("Balance: {}".format(e.get_account_balance_quote()))
    print("Buy and hold: {}".format((e.last_best_ask * starting_balance_base) + starting_balance_quote))