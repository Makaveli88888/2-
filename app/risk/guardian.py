from __future__ import annotations

import asyncio
from uuid import UUID

from app.risk.config import GuardianConfig
from app.risk.exposure import ExposureManager
from app.risk.models import RiskDecision, RiskOutcome, RiskRequest, RuleResult
from app.risk.portfolio import PortfolioLimits


class GuardianAngel:
    """Independent fail-closed gate. ALLOW is the only outcome accepted by PaperTrader."""

    def __init__(self, config: GuardianConfig | None = None, whitelist: set[str] | None = None, exposure: ExposureManager | None = None, portfolio: PortfolioLimits | None = None):
        self.config = config or GuardianConfig()
        self.exposure = exposure or ExposureManager(self.config, whitelist)
        self.portfolio = portfolio or PortfolioLimits(self.config)
        self._lock = asyncio.Lock()
        self._kill_switch = False
        self._kill_reason = ""

    async def engage_kill_switch(self, reason: str) -> None:
        async with self._lock:
            self._kill_switch = True
            self._kill_reason = reason[:500] or "unspecified"

    async def restore(self, *, authorized: bool = False) -> None:
        if not authorized:
            raise PermissionError("Guardian restore requires explicit authorized operator action")
        async with self._lock:
            self._kill_switch = False
            self._kill_reason = ""

    async def evaluate(self, req: RiskRequest) -> RiskDecision:
        results: list[RuleResult] = []
        reservation_id: UUID | None = None
        try:
            async with self._lock:
                killed, kill_reason = self._kill_switch, self._kill_reason
            results.append(RuleResult(rule_id="R-KILL-01", outcome="FAIL" if killed else "PASS", reason=f"kill switch engaged: {kill_reason}" if killed else "kill switch inactive"))
            paper_only = self.config.mode == "PAPER" and not self.config.allow_live_mode
            results.append(RuleResult(rule_id="R-MODE-01", outcome="PASS" if paper_only else "FAIL", reason="paper-only mode enforced" if paper_only else "non-PAPER mode or live authorization detected; execution disabled"))
            results.append(RuleResult(rule_id="R-CONFIDENCE-01", outcome="PASS" if req.confidence_calibrated >= self.config.min_confidence_calibrated else "FAIL", reason="confidence meets threshold" if req.confidence_calibrated >= self.config.min_confidence_calibrated else "calibrated confidence below minimum"))
            results.extend(await self.portfolio.evaluate())
            if req.orderbook_depth_usd is None:
                results.append(RuleResult(rule_id="R-LIQUIDITY-01", outcome="FAIL", reason="order-book depth unavailable; fail closed"))
            else:
                enough_depth = req.orderbook_depth_usd >= self.config.min_orderbook_depth_usd
                results.append(RuleResult(rule_id="R-LIQUIDITY-01", outcome="PASS" if enough_depth else "FAIL", reason="order-book depth sufficient" if enough_depth else "order-book depth below configured minimum"))
            if not any(item.outcome == "FAIL" for item in results):
                reserved, reservation_id, exposure_results = await self.exposure.reserve(req)
                results.extend(exposure_results)
                if not reserved:
                    reservation_id = None
            decision = RiskOutcome.ALLOW if reservation_id is not None and not any(item.outcome == "FAIL" for item in results) else RiskOutcome.DENY
            return RiskDecision(request_id=req.request_id, decision=decision, policy=self.config.policy, mode=self.config.mode, rule_results=tuple(results), reservation_id=reservation_id)
        except Exception:
            if reservation_id is not None:
                await self.exposure.release(reservation_id)
            # Never leak internal exception details into the decision surface.
            results.append(RuleResult(rule_id="R-ENGINE-FAILURE-01", outcome="FAIL", reason="risk engine failure; request denied"))
            return RiskDecision(request_id=req.request_id, decision=RiskOutcome.DENY, policy=self.config.policy, mode=self.config.mode, rule_results=tuple(results), reservation_id=None)

    async def release_reservation(self, reservation_id: UUID) -> bool:
        return await self.exposure.release(reservation_id)
