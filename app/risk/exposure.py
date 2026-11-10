from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import UUID

from app.risk.config import GuardianConfig
from app.risk.models import RiskRequest, RuleResult


class ExposureManager:
    """Single-process atomic exposure reservations. Use a DB transaction for multi-worker deployments."""

    def __init__(self, config: GuardianConfig, whitelist: set[str] | None = None):
        self.config = config
        self._per_market: dict[str, Decimal] = {}
        self._total = Decimal("0")
        self._whitelist = frozenset(whitelist or set())
        self._reservations: dict[UUID, tuple[str, Decimal]] = {}
        self._lock = asyncio.Lock()

    def check_whitelist(self, market_id: str) -> RuleResult:
        if not self._whitelist:
            return RuleResult(rule_id="R-WHITELIST-01", outcome="FAIL", reason="market whitelist is empty; default deny")
        if market_id not in self._whitelist:
            return RuleResult(rule_id="R-WHITELIST-01", outcome="FAIL", reason="market is not allow-listed")
        return RuleResult(rule_id="R-WHITELIST-01", outcome="PASS", reason="market allow-listed")

    async def reserve(self, req: RiskRequest) -> tuple[bool, UUID | None, list[RuleResult]]:
        async with self._lock:
            if req.request_id in self._reservations:
                return False, None, [RuleResult(rule_id="R-IDEMPOTENCY-01", outcome="FAIL", reason="request already reserved")]
            current_market = self._per_market.get(req.market_id, Decimal("0"))
            next_market = current_market + req.size_usd
            next_total = self._total + req.size_usd
            results = [
                RuleResult(rule_id="R-EXPOSURE-01", outcome="FAIL" if next_market > self.config.max_exposure_per_market_usd else "PASS", reason="per-market exposure limit exceeded" if next_market > self.config.max_exposure_per_market_usd else "per-market exposure within limit", params={"current": str(current_market), "requested": str(req.size_usd), "limit": str(self.config.max_exposure_per_market_usd)}),
                RuleResult(rule_id="R-EXPOSURE-02", outcome="FAIL" if next_total > self.config.max_total_exposure_usd else "PASS", reason="total exposure limit exceeded" if next_total > self.config.max_total_exposure_usd else "total exposure within limit", params={"current": str(self._total), "requested": str(req.size_usd), "limit": str(self.config.max_total_exposure_usd)}),
                self.check_whitelist(req.market_id),
            ]
            if any(item.outcome == "FAIL" for item in results):
                return False, None, results
            reservation_id = req.request_id
            self._reservations[reservation_id] = (req.market_id, req.size_usd)
            self._per_market[req.market_id] = next_market
            self._total = next_total
            return True, reservation_id, results

    async def release(self, reservation_id: UUID) -> bool:
        async with self._lock:
            reservation = self._reservations.pop(reservation_id, None)
            if reservation is None:
                return False
            market_id, size = reservation
            remaining = self._per_market.get(market_id, Decimal("0")) - size
            if remaining > 0:
                self._per_market[market_id] = remaining
            else:
                self._per_market.pop(market_id, None)
            self._total -= size
            return True

    async def snapshot(self) -> dict[str, object]:
        async with self._lock:
            return {"total_usd": str(self._total), "per_market_usd": {key: str(value) for key, value in self._per_market.items()}, "active_reservations": len(self._reservations)}
