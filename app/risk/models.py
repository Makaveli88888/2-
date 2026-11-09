from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    THROTTLE = "THROTTLE"
    REQUIRE_HUMAN = "REQUIRE_HUMAN"


class RuleResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    rule_id: str
    outcome: Literal["PASS", "FAIL", "SOFT_WARN"]
    reason: str
    params: dict[str, Any] = Field(default_factory=dict)


class RiskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    request_id: UUID = Field(default_factory=uuid4)
    source: Literal["user", "scout", "oracle", "system"]
    market_id: str = Field(min_length=1, max_length=200)
    side: Literal["BUY", "SELL"]
    size_usd: Decimal = Field(gt=0)
    confidence_calibrated: float = Field(ge=0, le=1)
    orderbook_depth_usd: Decimal | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("size_usd", "orderbook_depth_usd")
    @classmethod
    def finite_decimal(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError("Decimal values must be finite")
        return value


class RiskDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    decision_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    decision: RiskOutcome
    policy: str
    mode: str
    rule_results: tuple[RuleResult, ...]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reservation_id: UUID | None = None
