import unittest
import httpx
from app.market_data.polymarket_client import AsyncPublicClient, PublicMarketDataError

class PublicClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_order_book_uses_get(self):
        seen = []
        async def handler(request):
            seen.append((request.method, request.url.path, request.url.params.get("token_id")))
            return httpx.Response(200, json={"bids": [], "asks": []})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url=AsyncPublicClient.BASE_URL) as http:
            result = await AsyncPublicClient(client=http, requests_per_second=1000).get_order_book("token-123")
        self.assertEqual(result, {"bids": [], "asks": []})
        self.assertEqual(seen, [("GET", "/book", "token-123")])

    async def test_retries_transient_server_error(self):
        calls = {"count": 0}
        async def handler(request):
            calls["count"] += 1
            return httpx.Response(503) if calls["count"] == 1 else httpx.Response(200, json={"price": "0.5"})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url=AsyncPublicClient.BASE_URL) as http:
            result = await AsyncPublicClient(client=http, requests_per_second=1000, max_retries=1).get_market_price("token-123")
        self.assertEqual(result["price"], "0.5")
        self.assertEqual(calls["count"], 2)

    async def test_absolute_url_rejected(self):
        async with httpx.AsyncClient(base_url=AsyncPublicClient.BASE_URL) as http:
            client = AsyncPublicClient(client=http)
            with self.assertRaises(ValueError):
                await client.get_json("https://example.com/steal")

    async def test_non_transient_http_error_is_sanitized(self):
        async def handler(request):
            return httpx.Response(404)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url=AsyncPublicClient.BASE_URL) as http:
            with self.assertRaises(PublicMarketDataError):
                await AsyncPublicClient(client=http, requests_per_second=1000).get_json("/missing")

if __name__ == "__main__":
    unittest.main()
