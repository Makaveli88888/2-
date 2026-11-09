from __future__ import annotations

import asyncio
import time
from typing import Any
from urllib.parse import urlparse

import httpx


class PublicMarketDataError(RuntimeError):
    pass


class AsyncPublicClient:
    """Read-only Polymarket CLOB client. Only GET requests are exposed."""

    BASE_URL = "https://clob.polymarket.com"

    def __init__(self, *, client: httpx.AsyncClient | None = None, requests_per_second: float = 4.0, max_retries: int = 3, timeout: float = 8.0):
        if requests_per_second <= 0 or max_retries < 0 or timeout <= 0:
            raise ValueError("Invalid public client limits")
        self._client = client or httpx.AsyncClient(base_url=self.BASE_URL, timeout=timeout)
        self._owns_client = client is None
        self._interval = 1.0 / requests_per_second
        self._last_request = 0.0
        self._rate_lock = asyncio.Lock()
        self._max_retries = max_retries

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _throttle(self) -> None:
        async with self._rate_lock:
            wait = self._interval - (time.monotonic() - self._last_request)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request = time.monotonic()

    async def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        parsed = urlparse(path)
        if parsed.scheme or parsed.netloc or not path.startswith("/") or path.startswith("//"):
            raise ValueError("Only relative paths on the configured CLOB host are allowed")
        for attempt in range(self._max_retries + 1):
            await self._throttle()
            try:
                response = await self._client.get(path, params=params)
                if response.status_code == 429 or response.status_code in {500, 502, 503, 504}:
                    if attempt >= self._max_retries:
                        response.raise_for_status()
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = min(max(float(retry_after), 0.0), 5.0) if retry_after else min(0.25 * (2 ** attempt), 4.0)
                    except ValueError:
                        delay = min(0.25 * (2 ** attempt), 4.0)
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                if attempt >= self._max_retries:
                    raise PublicMarketDataError("Polymarket public data request failed") from exc
                await asyncio.sleep(min(0.25 * (2 ** attempt), 4.0))
            except httpx.HTTPStatusError as exc:
                raise PublicMarketDataError(f"Polymarket returned HTTP {exc.response.status_code}") from exc
        raise PublicMarketDataError("Polymarket request exhausted retries")

    async def get_order_book(self, token_id: str) -> dict[str, Any]:
        if not token_id or len(token_id) > 256:
            raise ValueError("Invalid token_id")
        return await self.get_json("/book", params={"token_id": token_id})

    async def get_market_price(self, token_id: str, side: str = "BUY") -> dict[str, Any]:
        if not token_id or len(token_id) > 256 or side not in {"BUY", "SELL"}:
            raise ValueError("Invalid market price request")
        return await self.get_json("/price", params={"token_id": token_id, "side": side})
