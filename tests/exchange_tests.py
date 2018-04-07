

import unittest
import json
from unittest.mock import patch, Mock, PropertyMock, MagicMock, call
from simulators.exchange import ExchangeSimulator


class TestExchangeSimulator(unittest.TestCase):
    def setUp(self):
        match = Mock()

        self.e = ExchangeSimulator([], match)

    def test_buy(self):
        self.assertEqual(self.e.balance_quote, 1000)
        self.e.buy(1, 0.5, 1000)
        self.assertEqual(self.e.balance_quote, 500)
        self.assertEqual(self.e.bids, [[1, 0.5, 1000]])


    def test_sell(self):
        self.assertEqual(self.e.balance_base, 0.1)
        self.e.sell(1, 0.05, 1000)
        self.assertEqual(self.e.balance_base, 0.05)
        self.assertEqual(self.e.asks, [[1, 0.05, 1000]])


    def test_bid_cancel(self):
        self.assertEqual(self.e.balance_quote, 1000)
        self.e.buy(1, 0.5, 1000)
        self.assertEqual(self.e.balance_quote, 500)
        self.e.cancel_order(1)
        self.assertEqual(self.e.balance_quote, 1000)
        self.assertEqual(self.e.bids, [])


    def test_ask_cancel(self):
        self.assertEqual(self.e.balance_base, 0.1)
        self.e.sell(1, 0.05, 1000)
        self.assertEqual(self.e.balance_base, 0.05)
        self.e.cancel_order(1)
        self.assertEqual(self.e.balance_base, 0.1)
        self.assertEqual(self.e.asks, [])


    def test_bid_execute(self):
        self.e.buy(1, 0.5, 1000)
        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "1000.00",
                "quantity": "0.05",
                "side": "sell",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.assertEqual(self.e.balance_quote, 500)
        self.assertEqual(self.e.bids, [])
        self.assertEqual(self.e.balance_base, 0.6)


    def test_sell_execute(self):
        self.e.sell(1, 0.05, 1000)
        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "1000.00",
                "quantity": "0.05",
                "side": "buy",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.assertEqual(self.e.balance_quote, 1050)
        self.assertEqual(self.e.asks, [])
        self.assertEqual(self.e.balance_base, 0.05)

        def test_bid_execute(self):
            self.e.buy(1, 0.5, 1000)
            self.e.datasource_callback([None, json.loads("""{
              "jsonrpc": "2.0",
              "method": "updateTrades",
              "params": {
                "data": [
                  {
                    "id": 1,
                    "price": "1000.00",
                    "quantity": "0.05",
                    "side": "sell",
                    "timestamp": "2017-11-24T19:22:40.715Z"
                  }
                ],
                "symbol": "BTCUSD"
              }
            }""")])

            self.assertEqual(self.e.balance_quote, 500)
            self.assertEqual(self.e.bids, [])
            self.assertEqual(self.e.balance_base, 0.6)


    def test_bid_not_execute(self):
        self.e.buy(1, 0.5, 1000)
        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "1000.00",
                "quantity": "0.05",
                "side": "buy",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "1001.00",
                "quantity": "0.05",
                "side": "sell",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.assertEqual(self.e.balance_quote, 500)
        self.assertEqual(len(self.e.bids), 1)
        self.assertEqual(self.e.balance_base, 0.1)


    def test_ask_not_execute(self):
        self.e.sell(1, 0.05, 1000)
        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "1000.00",
                "quantity": "0.05",
                "side": "sell",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.e.datasource_callback([None, json.loads("""{
          "jsonrpc": "2.0",
          "method": "updateTrades",
          "params": {
            "data": [
              {
                "id": 1,
                "price": "999.00",
                "quantity": "0.05",
                "side": "buy",
                "timestamp": "2017-11-24T19:22:40.715Z"
              }
            ],
            "symbol": "BTCUSD"
          }
        }""")])

        self.assertEqual(self.e.balance_quote, 1000)
        self.assertEqual(len(self.e.asks), 1)
        self.assertEqual(self.e.balance_base, 0.05)

if __name__ == "__main__":
    unittest.main()