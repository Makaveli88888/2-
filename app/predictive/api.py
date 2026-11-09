from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.predictive.client import PolymarketDataClient
from app.predictive.engine import PredictiveConsensusEngine
from app.predictive.paper import PaperTradingEngine
from app.predictive.store import PredictiveStore
from app.config import get_settings

router = APIRouter(prefix="/api/predictive", tags=["JOKER Predictive Engine"])
settings = get_settings()
store = PredictiveStore(settings.database_path)


class PaperOrderRequest(BaseModel):
    market_id: str = Field(min_length=1, max_length=128)
    token_id: str = Field(min_length=1, max_length=128, pattern=r"^[0-9]+$")
    side: str = Field(pattern=r"^(buy|sell)$")
    limit_price: str = Field(min_length=1, max_length=32)
    size: str = Field(min_length=1, max_length=32)


@router.get("/health")
def predictive_health():
    return {"engine": "JOKER PREDICTIVE ENGINE", "version": "0.1.0",
            "mode": "paper", "live_execution": False}


@router.get("/markets")
def markets(limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0)):
    client = PolymarketDataClient()
    try:
        rows = client.list_markets(limit=limit, offset=offset)
        return {"count": len(rows), "limit": limit, "offset": offset,
                "markets": [{"market_id": m.market_id, "question": m.question,
                    "slug": m.slug, "volume_24h": str(m.volume), "liquidity": str(m.liquidity),
                    "outcome_prices": [str(p) for p in m.outcome_prices],
                    "token_ids": m.token_ids} for m in rows]}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Polymarket market discovery failed") from exc
    finally:
        client.close()


@router.post("/scan")
def scan(pages: int = Query(1, ge=1, le=10), page_size: int = Query(100, ge=1, le=100)):
    client = PolymarketDataClient()
    engine = PredictiveConsensusEngine(store)
    all_signals = []
    scanned = 0
    try:
        for page in range(pages):
            rows = client.list_markets(limit=page_size, offset=page * page_size)
            if not rows:
                break
            for market in rows:
                all_signals.extend(engine.observe(market))
                scanned += 1
        return {"mode": "paper", "live_execution": False, "markets_scanned": scanned,
                "signals": all_signals, "model": "consensus_momentum_baseline_v0.1",
                "warning": "Heuristic baseline; not calibrated and not investment advice."}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Polymarket scan failed") from exc
    finally:
        client.close()


@router.post("/paper/orders")
def paper_order(request: PaperOrderRequest):
    client = PolymarketDataClient()
    try:
        book = client.get_order_book(request.token_id)
        engine = PaperTradingEngine(store)
        return engine.submit_limit(market_id=request.market_id, token_id=request.token_id,
            side=request.side, limit_price=request.limit_price, size=request.size, book=book)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Paper order simulation failed") from exc
    finally:
        client.close()
