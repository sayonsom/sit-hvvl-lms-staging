import unittest

from app.session_manager import SessionManager


class FakeRedis:
    def __init__(self):
        self.values = {}

    def setex(self, key, _ttl, value):
        self.values[key] = value

    def getdel(self, key):
        return self.values.pop(key, None)


class SessionManagerOneTimeValueTests(unittest.TestCase):
    def setUp(self):
        self.manager = SessionManager.__new__(SessionManager)
        self.manager.redis_client = FakeRedis()

    def test_state_is_consumed_atomically_once(self):
        self.manager.store_state("state-value", {"nonce": "nonce-value"})
        self.assertEqual(self.manager.get_state("state-value"), {"nonce": "nonce-value"})
        self.assertIsNone(self.manager.get_state("state-value"))

    def test_login_code_is_short_lived_handoff_not_session_token(self):
        code = self.manager.create_login_code("session-token")
        self.assertNotEqual(code, "session-token")
        self.assertEqual(self.manager.consume_login_code(code), "session-token")
        self.assertIsNone(self.manager.consume_login_code(code))


if __name__ == "__main__":
    unittest.main()
