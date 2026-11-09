import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import httpx

from app.predictive.client import PolymarketDataClient
from app.predictive.engine import PredictiveConsensusEngine
from app.predictive.models import Market, OrderBook, decimal_value
from app.predictive.paper import PaperTradingEngine
from app.predictive.store import PredictiveStore


class ModelTests(unittest.TestCase):
    def test_market_parses_gamma_json_strings(self):
        market = Market.from_gamma({
            "id": 123, "question": "Will it happen?", "active": True,
            "closed": False, "volume24hr": "1000", "liquidityNum": "250",
            "outcomePrices": '["0.41", "0.59"]',
            "clobTokenIds": '["12345", "67890"]',
        })
        self.assertEqual(market.market_id, "123")
        self.assertEqual(market.outcome_prices, [Decimal("0.41"), Decimal("0.59")])
        self.assertEqual(market.token_ids, ["12345", "67890"])

    def test_decimal_rejects_nan_and_out_of_range(self):
        with self.assertRaises(ValueError):
            decimal_value("NaN")
        with self.assertRaises(ValueError):
            decimal_value("1.2", minimum=Decimal("0"), maximum=Decimal("1"))

    def test_orderbook_best_prices_ignore_input_order(self):
        book = OrderBook.from_clob({
            "bids": [{"price": "0.40", "size": "3"}, {"price": "0.45", "size": "2"}],
            "asks": [{"price": "0.60", "size": "1"}, {"price": "0.55", "size": "4"}],
        })
        self.assertEqual(book.best_bid, Decimal("0.45"))
        self.assertEqual(book.best_ask, Decimal("0.55"))


class PredictiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = PredictiveStore(str(Path(self.tmp.name) / "predictive.db"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_first_observation_is_not_falsely_bullish(self):
        market = Market("m1", "Question", "q", True, False, Decimal("1000"),
                        Decimal("500"), [Decimal("0.50")], ["111"])
        signals = PredictiveConsensusEngine(self.store).observe(market)
        self.assertEqual(signals[0]["direction"], "flat")
        self.assertIsNone(signals[0]["previous_probability"])
        self.assertFalse(signals[0]["is_calibrated"])

    def test_consensus_change_is_recorded_and_projected(self):
        engine = PredictiveConsensusEngine(self.store)
        first = Market("m1", "Question", "q", True, False, Decimal("1000"),
                       Decimal("500"), [Decimal("0.50")], ["111"])
        second = Market("m1", "Question", "q", True, False, Decimal("1000"),
                        Decimal("500"), [Decimal("0.60")], ["111"])
        engine.observe(first)
        signal = engine.observe(second)[0]
        self.assertEqual(signal["direction"], "up")
        self.assertEqual(signal["heuristic_projection"], "0.65")

    def test_paper_buy_fills_only_against_eligible_asks(self):
        book = OrderBook.from_clob({
            "bids": [{"price": "0.40", "size": "10"}],
            "asks": [{"price": "0.51", "size": "2"}, {"price": "0.55", "size": "5"}],
        })
        result = PaperTradingEngine(self.store, fee_bps=100).submit_limit(
            market_id="m1", token_id="12345", side="buy",
            limit_price="0.52", size="3", book=book)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["filled_size"], "2")
        self.assertEqual(result["mode"], "paper")
        self.assertTrue(result["record_hash"])

    def test_paper_order_rejects_invalid_side(self):
        book = OrderBook([], [])
        with self.assertRaises(ValueError):
            PaperTradingEngine(self.store).submit_limit(
                market_id="m1", token_id="123", side="short",
                limit_price="0.5", size="1", book=book)


class ClientTests(unittest.TestCase):
    def test_public_market_and_book_reads(self):
        def handler(request):
            if request.url.path == "/markets":
                return httpx.Response(200, json=[{
                    "id": "m1", "question": "Q", "active": True, "closed": False,
                    "volume24hr": "10", "liquidityNum": "20",
                    "outcomePrices": ["0.5", "0.5"], "clobTokenIds": ["123", "456"],
                }])
            if request.url.path == "/book":
                return httpx.Response(200, json={"bids": [], "asks": []})
            return httpx.Response(404)

        transport = httpx.MockTransport(handler)
        client = PolymarketDataClient(transport=transport)
        try:
            markets = client.list_markets(limit=1)
            self.assertEqual(markets[0].market_id, "m1")
            self.assertEqual(client.get_order_book("123").bids, [])
            with self.assertRaises(ValueError):
                client.get_order_book("not-a-token")
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
