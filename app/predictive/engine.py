"""Transparent baseline consensus model. This is a heuristic, not a trained ML/RL model."""
from decimal import Decimal
from app.predictive.models import Market


class PredictiveConsensusEngine:
    def __init__(self, store, *, minimum_move: Decimal = Decimal("0.005")):
        self.store = store
        self.minimum_move = minimum_move

    def observe(self, market: Market) -> list[dict]:
        signals = []
        for index, probability in enumerate(market.outcome_prices):
            outcome = f"outcome_{index}"
            previous = self.store.previous_snapshot(market.market_id, outcome)
            self.store.record_snapshot(market.market_id, outcome, probability,
                                       market.volume, market.liquidity)
            delta = probability - previous if previous is not None else Decimal("0")
            projected = max(Decimal("0"), min(Decimal("1"), probability + delta / Decimal("2")))
            direction = "up" if delta > self.minimum_move else (
                "down" if delta < -self.minimum_move else "flat")
            activity = min(Decimal("0.20"), market.volume / Decimal("500000"))
            depth = min(Decimal("0.20"), market.liquidity / Decimal("250000"))
            momentum = min(Decimal("0.20"), abs(delta) * Decimal("4"))
            confidence = min(Decimal("0.80"), Decimal("0.20") + activity + depth + momentum)
            signals.append({
                "market_id": market.market_id, "question": market.question,
                "outcome": outcome, "current_probability": str(probability),
                "previous_probability": str(previous) if previous is not None else None,
                "change": str(delta), "direction": direction,
                "heuristic_projection": str(projected),
                "confidence_heuristic": str(confidence),
                "model": "consensus_momentum_baseline_v0.1",
                "is_calibrated": False,
            })
        return signals
