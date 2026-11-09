from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.risk.config import GuardianConfig
from app.risk.models import RuleResult


class PortfolioLimits:
    """In-memory PnL/rate guard for one process; production requires durable shared accounting."""

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._daily_pnl = Decimal("0")
        self._weekly_pnl = Decimal("0")
        self._day = datetime.now(timezone.utc).date()
        now = datetime.now(timezone.utc)
        self._week = (now.isocalendar().year, now.isocalendar().week)
        self._attempts: deque[datetime] = deque()
        self._lock = asyncio.Lock()

    def _roll_periods(self, now: datetime) -> None:
        if now.date() != self._day:
            self._day = now.date()
            self._daily_pnl = Decimal("0")
        iso = now.isocalendar()
        if (iso.year, iso.week) != self._week:
            self._week = (iso.year, iso.week)
            self._weekly_pnl = Decimal("0")

    async def evaluate(self) -> list[RuleResult]:
        async with self._lock:
            now = datetime.now(timezone.utc)
            self._roll_periods(now)
            cutoff = now - timedelta(minutes=1)
            while self._attempts and self._attempts[0] <= cutoff:
                self._attempts.popleft()
            over_limit = len(self._attempts) >= self.config.max_decisions_per_min
            rate = RuleResult(rule_id="R-RATE-01", outcome="FAIL" if over_limit else "PASS", reason="decision rate limit exceeded" if over_limit else "decision rate within limit")
            # Do not grow memory without bound during sustained over-limit traffic.
            if not over_limit:
                self._attempts.append(now)
            daily = RuleResult(rule_id="R-DRAWDOWN-01", outcome="FAIL" if self._daily_pnl <= -self.config.max_daily_drawdown_usd else "PASS", reason="daily drawdown limit reached" if self._daily_pnl <= -self.config.max_daily_drawdown_usd else "daily drawdown within limit", params={"pnl_usd": str(self._daily_pnl)})
            weekly = RuleResult(rule_id="R-DRAWDOWN-02", outcome="FAIL" if self._weekly_pnl <= -self.config.max_weekly_drawdown_usd else "PASS", reason="weekly drawdown limit reached" if self._weekly_pnl <= -self.config.max_weekly_drawdown_usd else "weekly drawdown within limit", params={"pnl_usd": str(self._weekly_pnl)})
            return [daily, weekly, rate]

    async def record_pnl(self, pnl: Decimal) -> None:
        if not pnl.is_finite():
            raise ValueError("PnL must be finite")
        async with self._lock:
            now = datetime.now(timezone.utc)
            self._roll_periods(now)
            self._daily_pnl += pnl
            self._weekly_pnl += pnl

    async def snapshot(self) -> dict[str, str]:
        async with self._lock:
            self._roll_periods(datetime.now(timezone.utc))
            return {"daily_pnl_usd": str(self._daily_pnl), "weekly_pnl_usd": str(self._weekly_pnl)}
