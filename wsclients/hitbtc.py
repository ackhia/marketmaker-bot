
from websocket import create_connection, _exceptions
from json import loads, dumps
import time
import uuid

class HitBtc:
    def __init__(self, callback):
        self.id = "46235462"
        self.__connect()
        self.callback = callback
        self.bids = []
        self.asks = []
        self.balances = []

    def __recv(self):
        result = self.ws.recv()
        print("[IN] {}".format(result))
        return result

    def __send(self, msg):
        self.ws.send(msg)
        print("[OUT] {}".format(msg))


    def subscribe_ticker(self, pair):
        self.__send(dumps({
          "method": "subscribeTicker",
          "params": {
            "symbol": pair
          },
          "id": 123
        }))


    def subscribe_reports(self):
        self.__send(dumps({
          "method": "subscribeReports",
          "params": { }
        }))


    def __connect(self):
        self.ws = create_connection("wss://api.hitbtc.com/api/2/ws")
        self.__authenticate()


    def update_state(self, resp_json):
        if "result" in resp_json:
            result = resp_json["result"]
            if type(result) is dict and "side" in result:
                if result["status"] == "new":
                    if result["side"] == "buy":
                        self.bids.append(result)
                    elif result["side"] == "sell":
                        self.asks.append(result)
                elif result["status"] == "canceled":
                    if result["side"] == "buy":
                        self.bids = [b for b in self.bids if b["id"] != result["id"]]
                    elif result["side"] == "sell":
                        self.asks = [a for a in self.asks if a["id"] != result["id"]]
            elif type(result) is list and len(result) > 0 and type(result[0]) is dict and "available" in result[0]:
                self.balances = result
        if "method" in resp_json and resp_json["method"] == "report":
            params = resp_json["params"]
            if params["status"] == "filled":
                if params["side"] == "buy":
                    self.bids = [b for b in self.bids if b["id"] != params["id"]]
                elif params["side"] == "sell":
                    self.asks = [a for a in self.asks if a["id"] != params["id"]]

    def monitor(self, trades, ticker, pair):
        if ticker:
            self.subscribe_ticker(pair)

        if trades:
            self.subscribe_reports()

        while True:
            try:
                if self.ws is None:
                    self.__connect()

                    if ticker:
                        self.subscribe_ticker(pair)

                    if trades:
                        self.subscribe_reports()

                result = self.__recv()
                result_json = loads(result)
                self.update_state(result_json)
                self.callback(result_json)

            except Exception as e:
                print(e)
                self.ws = None
                time.sleep(1)
                raise

    def __authenticate(self):
        self.__send(dumps({
            "method": "login",
            "params": {
                "algo": "BASIC",
                "pKey": "<your pkey>",
                "sKey": "<your sKey>"
            }
        }))

    def buy(self, pair, price, quantity):
        client_order_id = uuid.uuid4().hex

        self.__send(dumps({
          "method": "newOrder",
          "params": {
            "clientOrderId": client_order_id,
            "symbol": pair,
            "side": "buy",
            "price": str(price),
            "quantity": str(quantity)
          },
          "id":client_order_id
        }))

        return client_order_id

    def sell(self, pair, price, quantity):
        client_order_id = uuid.uuid4().hex

        self.__send(dumps({
          "method": "newOrder",
          "params": {
            "clientOrderId": client_order_id,
            "symbol": pair,
            "side": "sell",
            "price": str(price),
            "quantity": str(quantity)
          },
          "id": client_order_id
        }))

        return client_order_id


    def cancel_order(self, client_order_id):
        id = uuid.uuid4().hex

        self.__send(dumps({
            "method": "cancelOrder",
            "params":
                {"clientOrderId": client_order_id},
            "id": id}))


    def update_balances(self):
        id = uuid.uuid4().hex
        self.__send(dumps({
            "method": "getTradingBalance",
            "params": {},
            "id": id}))
