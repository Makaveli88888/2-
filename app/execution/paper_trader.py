from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from app.risk.guardian import GuardianAngel
from app.risk.models import RiskOutcome, RiskRequest


class PaperTrade:
    def __init__(self, trade_id: UUID, request_id: UUID, reservation_id: UUID, market_id: str, side: str, size_usd: Decimal, price: Decimal):
        self.trade_id = trade_id
        self.request_id = request_id
        self.reservation_id = reservation_id
        self.market_id = market_id
        self.side = side
        self.size_usd = size_usd
        self.price = price
        self.pnl = Decimal("0")


class PaperTrader:
    def __init__(self, guard: GuardianAngel):
        self._guard = guard
        self._trades: list[PaperTrade] = []

    async def try_trade(self, req: RiskRequest, price: Decimal) -> PaperTrade | None:
        if not price.is_finite() or price <= 0:
            raise ValueError("Paper trade price must be finite and greater than zero")
        decision = await self._guard.evaluate(req)
        if decision.decision != RiskOutcome.ALLOW or decision.reservation_id is None:
            return None
        trade = PaperTrade(uuid4(), req.request_id, decision.reservation_id, req.market_id, req.side, req.size_usd, price)
        self._trades.append(trade)
        return trade

    async def close_trade(self, trade_id: UUID, realized_pnl: Decimal = Decimal("0")) -> bool:
        if not realized_pnl.is_finite():
            raise ValueError("Realized PnL must be finite")
        for trade in self._trades:
            if trade.trade_id == trade_id:
                await self._guard.portfolio.record_pnl(realized_pnl)
                await self._guard.release_reservation(trade.reservation_id)
                self._trades.remove(trade)
                return True
        return False

    @property
    def trades(self) -> list[PaperTrade]:
        return list(self._trades)
