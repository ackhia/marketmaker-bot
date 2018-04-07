

class Match:
    def __init__(self):
        pass

    def set_exchange(self, exchange):
        self.exchange = exchange

    def bid_executed(self, id):
        print("{} bid executed".format(id))
        self.exchange.update_balances()

    def ask_executed(self, id):
        print("{} ask executed".format(id))
        self.exchange.update_balances()

    def get_bid_price(self):
        bids = self.exchange.get_bids()
        if len(bids) > 0:
            return float(bids[0]["price"])

        return 0

    def get_ask_price(self):
        asks = self.exchange.get_asks()
        if len(asks) > 0:
            return float(asks[0]["price"])

        return 0

    def cancel_bids(self):
        kills = []
        for b in self.exchange.get_bids():
            self.exchange.cancel_order(b["clientOrderId"])
            kills.append(b["clientOrderId"])

        return kills

    def cancel_asks(self):
        kills = []
        for a in self.exchange.get_asks():
            self.exchange.cancel_order(a["clientOrderId"])
            kills.append(a["clientOrderId"])

        return kills

    def cancel_rogue_orders(self, bid, ask, kills):
        bids = self.exchange.get_bids()
        asks = self.exchange.get_asks()

        for b in bids:
            if float(b["price"]) != bid and b["clientOrderId"] not in kills:
                print("Killing rogue bid {}".format(b["clientOrderId"]))
                self.exchange.cancel_order(b["clientOrderId"])
                kills.append(b["clientOrderId"])

        for a in asks:
            if float(a["price"]) != ask and a["clientOrderId"] not in kills:
                print("Killing rogue ask {}".format(a["clientOrderId"]))
                self.exchange.cancel_order(a["clientOrderId"])
                kills.append(a["clientOrderId"])

        if len(bids) > 1:
            for b in bids[1:]:
                if b["clientOrderId"] not in kills:
                    print("Killing rogue bid {}".format(b["clientOrderId"]))
                    self.exchange.cancel_order(b["clientOrderId"])

        if len(asks) > 1:
            for a in asks[1:]:
                if a["clientOrderId"] not in kills:
                    print("Killing rogue ask {}".format(a["clientOrderId"]))
                    self.exchange.cancel_order(a["clientOrderId"])


    def update_price(self, bid, ask):
        #print("{} {} {:.3}".format(bid, ask, ask - bid))
        min_order_size = 10
        target_order_size = 40
        min_spread = 0.000005

        if ask - bid < min_spread:
            print("Spread too small {}".format(ask - bid))
            return

        if self.exchange.balance_quote is None or self.exchange.balance_base is None:
            print("Waiting for balances")
            return

        current_bid = self.get_bid_price()
        balance_quote = self.exchange.balance_quote / ask
        balance_quote += current_bid

        current_ask = self.get_ask_price()
        balance_base = self.exchange.balance_base
        balance_base += current_ask
        total_balance = balance_quote + balance_base
        target_balance_base = total_balance / 2

        if balance_base > 0:
            order_size_bid = target_balance_base / balance_base * target_order_size
        else:
            order_size_bid = target_balance_base

        if balance_quote > 0:
            order_size_ask = target_balance_base / balance_quote * target_order_size
        else:
            order_size_ask = target_balance_base

        order_size_bid = min(order_size_bid, balance_quote, target_balance_base)
        order_size_ask = min(order_size_ask, balance_base, target_balance_base)

        #print("Balance quote (usd) {} balance base (btc) {} total {}".format(balance_quote, balance_base, balance_quote + balance_base))

        kills = []

        if order_size_bid > min_order_size:
            if bid != current_bid:
                print("Cancelling bids")
                kills.extend(self.cancel_bids())

                print("Placing bid for {} size {}".format(bid, order_size_bid))
                self.exchange.buy(order_size_bid, bid)


        if order_size_ask > min_order_size:
            if ask != current_ask:
                print("Cancelling all asks")
                kills.extend(self.cancel_asks())

                print("Placing ask at {} for {}".format(ask, order_size_ask))
                self.exchange.sell(order_size_ask, ask)

        self.cancel_rogue_orders(bid, ask, kills)
