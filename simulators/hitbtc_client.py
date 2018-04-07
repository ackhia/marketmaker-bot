

import asyncio
import websockets
import json
import logging

class HitBtcClient:
    @classmethod
    async def create(cls):
        self = HitBtcClient()
        self.ws = await websockets.connect('ws://127.0.0.1:8765')
        return self

    async def new_order(self, id, side, price, quantity):
        await self.ws.send(json.dumps({
              "method": "newOrder",
              "params": {
                "clientOrderId": id,
                "symbol": "BTCUSD",
                "side": side,
                "price": price,
                "quantity": quantity
              },
              "id": -1
            }))

        response = await self.ws.recv()
        return response

    async def cancel_order(self, id):
        await self.ws.send(json.dumps({
            "method": "cancelOrder",
            "params": {
                "clientOrderId": id,
            },
            "id": -1
        }))

        response = await self.ws.recv()
        return response


    async def close_connection(self):
        await self.ws.close()


    async def get_orders(self):
        await self.ws.send(json.dumps({
            "method": "getOrders",
            "params": {
                "clientOrderId": id,
            },
            "id": -1
        }))

async def main():
    client = await HitBtcClient.create()
    print(await client.new_order("1", "buy", 8000, 0.01))
    print(await client.new_order("2", "sell", 9000, 0.01))
    print(await client.cancel_order("1"))
    await client.close_connection()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

