from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GuardianConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: str = "PAPER"
    policy: str = "paper-v1"
    allow_live_mode: bool = False
    max_exposure_per_market_usd: Decimal = Decimal("50")
    max_total_exposure_usd: Decimal = Decimal("200")
    max_daily_drawdown_usd: Decimal = Decimal("20")
    max_weekly_drawdown_usd: Decimal = Decimal("60")
    min_orderbook_depth_usd: Decimal = Decimal("500")
    max_decisions_per_min: int = Field(default=30, ge=1, le=10000)
    min_confidence_calibrated: float = Field(default=0.55, ge=0, le=1)

    @field_validator(
        "max_exposure_per_market_usd", "max_total_exposure_usd",
        "max_daily_drawdown_usd", "max_weekly_drawdown_usd",
        "min_orderbook_depth_usd",
    )
    @classmethod
    def positive_finite(cls, value: Decimal) -> Decimal:
        if not value.is_finite() or value < 0:
            raise ValueError("Risk limits must be finite and non-negative")
        return value
