"""Public, unauthenticated Polymarket market-data client. No order endpoints exist here."""
import httpx
from app.predictive.models import Market, OrderBook

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"


class PolymarketDataClient:
    def __init__(self, timeout: float = 12.0, transport=None):
        self._client = httpx.Client(timeout=timeout, transport=transport,
                                    headers={"User-Agent": "JOKER-Predictive-Engine/0.1"})

    def close(self) -> None:
        self._client.close()

    def list_markets(self, *, limit: int = 100, offset: int = 0) -> list[Market]:
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        response = self._client.get(
            f"{GAMMA_URL}/markets",
            params={"active": "true", "closed": "false", "limit": limit,
                    "offset": offset, "order": "volume24hr", "ascending": "false"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Unexpected Gamma API response")
        return [Market.from_gamma(item) for item in payload if isinstance(item, dict)]

    def get_order_book(self, token_id: str) -> OrderBook:
        if not token_id or len(token_id) > 128 or not token_id.isdigit():
            raise ValueError("Invalid Polymarket token ID")
        response = self._client.get(f"{CLOB_URL}/book", params={"token_id": token_id})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Unexpected CLOB order-book response")
        return OrderBook.from_clob(payload)
