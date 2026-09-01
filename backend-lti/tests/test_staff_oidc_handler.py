import json
import time
import unittest
from types import SimpleNamespace

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import settings
from app.staff_oidc_handler import StaffOIDCHandler


class FakeRedis:
    def __init__(self):
        self.values = {}

    def setex(self, key, _ttl, value):
        self.values[key] = value

    def getdel(self, key):
        return self.values.pop(key, None)


class FakeJwksClient:
    def __init__(self, key):
        self.key = key

    def get_signing_key_from_jwt(self, _token):
        return SimpleNamespace(key=self.key)


class StaffOIDCSecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_client_id = settings.STAFF_OIDC_CLIENT_ID
        settings.STAFF_OIDC_CLIENT_ID = "staff-client"
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.handler = StaffOIDCHandler.__new__(StaffOIDCHandler)
        self.handler.session_manager = SimpleNamespace(redis_client=FakeRedis())
        self.handler._jwks_client = FakeJwksClient(self.private_key.public_key())

    def tearDown(self):
        settings.STAFF_OIDC_CLIENT_ID = self.original_client_id

    def _token(self, nonce=None):
        now = int(time.time())
        claims = {
            "iss": "https://idp.example.edu",
            "aud": "staff-client",
            "sub": "staff-user",
            "iat": now,
            "exp": now + 300,
        }
        if nonce is not None:
            claims["nonce"] = nonce
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    def test_staff_state_is_atomically_consumed_once(self):
        self.handler._store_state("state", {"nonce": "nonce"})
        self.assertEqual(self.handler._consume_state("state"), {"nonce": "nonce"})
        self.assertIsNone(self.handler._consume_state("state"))

    def test_staff_id_token_requires_expected_nonce(self):
        with self.assertRaisesRegex(ValueError, "Nonce mismatch"):
            self.handler._validate_id_token(
                self._token(),
                expected_nonce="expected",
                issuer="https://idp.example.edu",
            )

    def test_staff_id_token_accepts_matching_nonce(self):
        claims = self.handler._validate_id_token(
            self._token(nonce="expected"),
            expected_nonce="expected",
            issuer="https://idp.example.edu",
        )
        self.assertEqual(claims["sub"], "staff-user")


if __name__ == "__main__":
    unittest.main()
