

from exchange import ExchangeSimulator
import asyncio
import websockets
import json

class HitBtcServer:
    def __init__(self):
        self.exchange = ExchangeSimulator()
        self.methods = {"login": self.__login,
                        "newOrder": self.__new_order,
                        "cancelOrder": self.__cancel_order,
                        "getOrders": self.__get_orders}

    async def __on_connection(self, websocket, path):
        try:
            while websocket.open:
                request = await websocket.recv()
                json_request = json.loads(request)

                if "method" in json_request:
                    response = await self.methods[json_request["method"]](json_request)
                else:
                    response = self.__get_error_response("You must specify a method")

                await websocket.send(response)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def __login(self, request):
        return self.__get_success_response()


    async def __new_order(self, request):
        params = request["params"]
        id = params["clientOrderId"]
        quantity = float(params["quantity"])
        price = float(params["price"])
        side = params["side"]

        result = False

        if side == "buy":
            result = self.exchange.buy(id, quantity, price)
        elif side == "sell":
            result = self.exchange.sell(id, quantity, price)

        if result:
            return self.__get_success_response()
        return self.__get_error_response("Order failed")

    async def __cancel_order(self, request):
        params = request["params"]
        id = params["clientOrderId"]
        self.exchange.cancel_order(id)
        return self.__get_success_response()


    async def __get_orders(self, request):
        orders = []

        for o in self.exchange.buy_orders:
            orders.append("id": o["id"])

        self.exchange.cancel_order(id)
        return self.__get_success_response()


    def __get_error_response(self, message):
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": 20001,
                    "message": message,
                    "description": ""
                },
                "id": -1
            })

    def __get_success_response(self):
        return json.dumps({
            "jsonrpc": "2.0",
            "result": True,
            "id": -1
        })

    def start(self):
        start_server = websockets.serve(self.__on_connection, 'localhost', 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    HitBtcServer().start()



