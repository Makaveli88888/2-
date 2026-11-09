import asyncio
import unittest
from decimal import Decimal
from pydantic import ValidationError
from app.execution.order_executor import OrderExecutor
from app.execution.paper_trader import PaperTrader
from app.risk.config import GuardianConfig
from app.risk.guardian import GuardianAngel
from app.risk.models import RiskOutcome, RiskRequest

def request(*, size="10", market="market-1", confidence=0.9, depth="1000"):
    return RiskRequest(source="user", market_id=market, side="BUY", size_usd=Decimal(size), confidence_calibrated=confidence, orderbook_depth_usd=None if depth is None else Decimal(depth))

def config(**overrides):
    return GuardianConfig(**overrides)

class GuardianTests(unittest.IsolatedAsyncioTestCase):
    async def test_allow_requires_whitelist_and_all_checks(self):
        guard = GuardianAngel(config(), whitelist={"market-1"})
        decision = await guard.evaluate(request())
        self.assertEqual(decision.decision, RiskOutcome.ALLOW)
        self.assertIsNotNone(decision.reservation_id)

    async def test_empty_whitelist_denies_by_default(self):
        guard = GuardianAngel(config(), whitelist=set())
        decision = await guard.evaluate(request())
        self.assertEqual(decision.decision, RiskOutcome.DENY)
        self.assertTrue(any(r.rule_id == "R-WHITELIST-01" and r.outcome == "FAIL" for r in decision.rule_results))

    async def test_paper_mode_does_not_bypass_confidence_or_liquidity(self):
        guard = GuardianAngel(config(), whitelist={"market-1"})
        self.assertEqual((await guard.evaluate(request(confidence=0.1))).decision, RiskOutcome.DENY)
        self.assertEqual((await guard.evaluate(request(depth=None))).decision, RiskOutcome.DENY)

    async def test_kill_switch_and_authorized_restore(self):
        guard = GuardianAngel(config(), whitelist={"market-1"})
        await guard.engage_kill_switch("operator test")
        self.assertEqual((await guard.evaluate(request())).decision, RiskOutcome.DENY)
        with self.assertRaises(PermissionError):
            await guard.restore()
        await guard.restore(authorized=True)
        self.assertEqual((await guard.evaluate(request())).decision, RiskOutcome.ALLOW)

    async def test_exposure_reservation_is_atomic_under_concurrency(self):
        guard = GuardianAngel(config(max_exposure_per_market_usd=Decimal("50"), max_total_exposure_usd=Decimal("50")), whitelist={"market-1"})
        decisions = await asyncio.gather(*(guard.evaluate(request(size="40")) for _ in range(2)))
        self.assertEqual(sum(d.decision == RiskOutcome.ALLOW for d in decisions), 1)
        self.assertEqual((await guard.exposure.snapshot())["total_usd"], "40")

    async def test_drawdown_is_enforced(self):
        guard = GuardianAngel(config(max_daily_drawdown_usd=Decimal("5")), whitelist={"market-1"})
        await guard.portfolio.record_pnl(Decimal("-5"))
        self.assertEqual((await guard.evaluate(request())).decision, RiskOutcome.DENY)

    async def test_paper_trade_reserves_then_releases_exposure(self):
        guard = GuardianAngel(config(), whitelist={"market-1"})
        trader = PaperTrader(guard)
        trade = await trader.try_trade(request(), Decimal("0.5"))
        self.assertIsNotNone(trade)
        self.assertEqual((await guard.exposure.snapshot())["total_usd"], "10")
        self.assertTrue(await trader.close_trade(trade.trade_id, Decimal("2")))
        self.assertEqual((await guard.exposure.snapshot())["total_usd"], "0")
        self.assertEqual((await guard.portfolio.snapshot())["daily_pnl_usd"], "2")

    async def test_invalid_price_rejected(self):
        trader = PaperTrader(GuardianAngel(config(), whitelist={"market-1"}))
        with self.assertRaises(ValueError):
            await trader.try_trade(request(), Decimal("NaN"))

    async def test_order_executor_always_disabled(self):
        executor = OrderExecutor()
        with self.assertRaises(RuntimeError):
            await executor.place_order(symbol="TEST")
        with self.assertRaises(RuntimeError):
            await executor.cancel_order(order_id="123")

    async def test_non_paper_mode_is_denied(self):
        guard = GuardianAngel(config(mode="LIVE"), whitelist={"market-1"})
        self.assertEqual((await guard.evaluate(request())).decision, RiskOutcome.DENY)

    def test_non_finite_request_rejected(self):
        with self.assertRaises(ValidationError):
            request(size="NaN")

if __name__ == "__main__":
    unittest.main()
