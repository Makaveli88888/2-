import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_main_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "JokerGodAl")

    def test_predictive_health_endpoint_is_wired(self):
        response = self.client.get("/api/predictive/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "paper")
        self.assertFalse(response.json()["live_execution"])


if __name__ == "__main__":
    unittest.main()
