from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


def decimal_value(value: Any, *, minimum: Decimal | None = None,
                   maximum: Decimal | None = None) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Invalid decimal value") from exc
    if not result.is_finite():
        raise ValueError("Value must be finite")
    if minimum is not None and result < minimum:
        raise ValueError("Value below allowed minimum")
    if maximum is not None and result > maximum:
        raise ValueError("Value above allowed maximum")
    return result


@dataclass(frozen=True)
class Market:
    market_id: str
    question: str
    slug: str
    active: bool
    closed: bool
    volume: Decimal
    liquidity: Decimal
    outcome_prices: list[Decimal]
    token_ids: list[str]

    @classmethod
    def from_gamma(cls, raw: dict[str, Any]) -> "Market":
        import json

        def parse_list(value: Any) -> list[Any]:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    return []
            return value if isinstance(value, list) else []

        def metric(primary: str, fallback: str) -> Decimal:
            value = raw.get(primary)
            if value in (None, ""):
                value = raw.get(fallback, 0)
            if value in (None, ""):
                value = 0
            return decimal_value(value, minimum=Decimal("0"))

        prices = [decimal_value(v, minimum=Decimal("0"), maximum=Decimal("1"))
                  for v in parse_list(raw.get("outcomePrices"))]
        tokens = [str(v) for v in parse_list(raw.get("clobTokenIds")) if str(v)]
        return cls(
            market_id=str(raw.get("id", "")),
            question=str(raw.get("question", "")),
            slug=str(raw.get("slug", "")),
            active=raw.get("active", raw.get("acceptingOrders", False)) is True,
            closed=raw.get("closed", False) is True,
            volume=metric("volume24hr", "volume"),
            liquidity=metric("liquidityNum", "liquidity"),
            outcome_prices=prices,
            token_ids=tokens,
        )


@dataclass(frozen=True)
class OrderBook:
    bids: list[tuple[Decimal, Decimal]]
    asks: list[tuple[Decimal, Decimal]]

    @classmethod
    def from_clob(cls, raw: dict[str, Any]) -> "OrderBook":
        def levels(key: str) -> list[tuple[Decimal, Decimal]]:
            result = []
            for item in raw.get(key, []) or []:
                price = decimal_value(item.get("price"), minimum=Decimal("0"), maximum=Decimal("1"))
                size = decimal_value(item.get("size"), minimum=Decimal("0"))
                if size > 0:
                    result.append((price, size))
            return result
        return cls(bids=levels("bids"), asks=levels("asks"))

    @property
    def best_bid(self) -> Decimal | None:
        return max((p for p, _ in self.bids), default=None)

    @property
    def best_ask(self) -> Decimal | None:
        return min((p for p, _ in self.asks), default=None)
