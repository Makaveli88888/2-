from decimal import Decimal
from app.predictive.models import OrderBook, decimal_value


class PaperTradingEngine:
    """Local simulation only. This module has no credentials and cannot submit live orders."""
    def __init__(self, store, fee_bps: int = 0):
        if fee_bps < 0 or fee_bps > 10_000:
            raise ValueError("Invalid paper fee basis points")
        self.store = store
        self.fee_rate = Decimal(fee_bps) / Decimal(10_000)

    def submit_limit(self, *, market_id: str, token_id: str, side: str,
                     limit_price, size, book: OrderBook) -> dict:
        if side not in {"buy", "sell"}:
            raise ValueError("Side must be buy or sell")
        price = decimal_value(limit_price, minimum=Decimal("0.0001"), maximum=Decimal("0.9999"))
        quantity = decimal_value(size, minimum=Decimal("0.00000001"), maximum=Decimal("1000000"))
        levels = sorted(book.asks if side == "buy" else book.bids,
                        key=lambda level: level[0], reverse=(side == "sell"))
        remaining = quantity
        notional = Decimal("0")
        filled = Decimal("0")
        for level_price, available in levels:
            executable = level_price <= price if side == "buy" else level_price >= price
            if not executable or remaining <= 0:
                continue
            take = min(remaining, available)
            filled += take
            remaining -= take
            notional += take * level_price
        average = notional / filled if filled else None
        fee = notional * self.fee_rate
        status = "filled" if filled == quantity else ("partial" if filled > 0 else "unfilled")
        return self.store.record_paper_order({
            "market_id": market_id, "token_id": token_id, "side": side,
            "limit_price": str(price), "requested_size": str(quantity),
            "filled_size": str(filled), "average_price": str(average) if average is not None else None,
            "fee": str(fee), "status": status,
        })
