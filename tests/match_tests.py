

import unittest
from unittest.mock import patch, Mock, PropertyMock, MagicMock, call
from logic.match import Match

class TestMatch(unittest.TestCase):
    def setUp(self):
        self.match = Match()


    def create_exchange(self, balance_quote, balance_base, bids, asks):

        exchange = Mock()

        type(exchange).balance_quote = PropertyMock(return_value=balance_quote)
        type(exchange).balance_base = PropertyMock(return_value=balance_base)
        exchange.buy = MagicMock(return_value=True)
        exchange.sell = MagicMock(return_value=True)
        exchange.bids = bids
        exchange.asks = asks

        return exchange

    def test_update_price_create_bid(self):
        e = self.create_exchange(1000, 0, [], [])

        self.match.set_exchange(e)
        self.match.update_price(1000, 1005)
        e.buy.assert_called_once_with(1, 500 / 1005, 1000)
        e.sell.assert_not_called()

    def test_update_price_create_ask(self):
        e = self.create_exchange(0, 1, [], [])

        self.match.set_exchange(e)
        self.match.update_price(1000, 1005)
        e.buy.assert_not_called()
        e.sell.assert_called_once_with(1, 0.5, 1005)


    def test_update_price_create_both(self):
        e = self.create_exchange(1005, 1, [], [])

        self.match.set_exchange(e)
        self.match.update_price(1000, 1005)
        e.buy.assert_called_once_with(1, 0.05, 1000)
        e.sell.assert_called_once_with(2, 0.05, 1005)


    def test_update_price_cancel_recreate(self):
        e = self.create_exchange(1005, 1, [], [])

        self.match.set_exchange(e)
        self.match.update_price(1000, 1005)
        self.match.update_price(1004, 1008)
        e.buy.assert_has_calls([call(1, 0.05, 1000), call(3, 0.04992559523809524, 1004)])
        e.sell.assert_has_calls([call(2, 0.05, 1005), call(4, 0.05007462686567165, 1008)])
        self.assertEqual(e.cancel_order.call_count, 2)

    def test_update_price_execute_bid(self):
        e = self.create_exchange(1005, 1, [], [])
        self.match.set_exchange(e)

        self.assertEqual(self.match.current_bid, [0, None])
        self.match.update_price(1000, 1005)
        self.assertEqual(self.match.current_bid, [1, 1000])
        self.match.bid_executed(1)
        self.assertEqual(self.match.current_bid, [0, None])


    def test_update_price_execute_ask(self):
        e = self.create_exchange(1005, 1, [], [])
        self.match.set_exchange(e)

        self.assertEqual(self.match.current_ask, [0, None])
        self.match.update_price(1000, 1005)
        self.assertEqual(self.match.current_ask, [2, 1005])
        self.match.ask_executed(2)
        self.assertEqual(self.match.current_ask, [0, None])


    def test_update_price_execute_bid_recreate(self):
        e = self.create_exchange(1005, 1, [], [])
        self.match.set_exchange(e)

        self.assertEqual(self.match.current_bid, [0, None])
        self.match.update_price(1000, 1005)
        self.assertEqual(self.match.current_bid, [1, 1000])
        self.match.bid_executed(1)
        self.assertEqual(self.match.current_bid, [0, None])
        self.match.update_price(1000, 1006)
        self.assertEqual(self.match.current_bid, [3, 1000])


    def test_update_price_execute_ask_recreate(self):
        e = self.create_exchange(1005, 1, [], [])

        self.match.set_exchange(e)

        self.assertEqual(self.match.current_ask, [0, None])
        self.match.update_price(1000, 1005)
        self.assertEqual(self.match.current_ask, [2, 1005])
        self.match.ask_executed(2)
        self.assertEqual(self.match.current_ask, [0, None])
        self.match.update_price(1000, 1006)
        self.assertEqual(self.match.current_ask, [3, 1006])

if __name__ == "__main__":
    unittest.main()
    """t = Mock()
    t.test = MagicMock(return_value=3)
    #print(t.test())
    print(t.test.called)"""