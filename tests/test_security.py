import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

import jwt
from fastapi import HTTPException

from app.security import authenticated_user, create_access_token


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(jwt_secret="test-secret-that-is-at-least-32-characters-long")
        self.settings.jwt_secret = "test-secret-that-is-at-least-32-characters-long"
        self.settings_obj = patch("app.security.get_settings", return_value=self.settings)
        self.settings_obj.start()

    def tearDown(self):
        self.settings_obj.stop()

    def test_valid_token_returns_subject(self):
        token = create_access_token("alice")
        self.assertEqual(authenticated_user("Bearer " + token), "alice")

    def test_missing_token_is_rejected(self):
        with self.assertRaises(HTTPException) as ctx:
            authenticated_user(None)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_invalid_token_is_rejected(self):
        with self.assertRaises(HTTPException) as ctx:
            authenticated_user("Bearer not-a-jwt")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_expired_token_is_rejected(self):
        now = datetime.now(timezone.utc)
        token = jwt.encode({"sub": "alice", "iat": now - timedelta(hours=2),
                            "exp": now - timedelta(hours=1)},
                           self.settings.jwt_secret, algorithm="HS256")
        with self.assertRaises(HTTPException) as ctx:
            authenticated_user("Bearer " + token)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_short_secret_is_rejected(self):
        self.settings.jwt_secret = "short"
        with self.assertRaises(HTTPException) as ctx:
            authenticated_user("Bearer anything")
        self.assertEqual(ctx.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
