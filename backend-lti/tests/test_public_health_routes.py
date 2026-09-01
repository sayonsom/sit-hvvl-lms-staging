import unittest
from unittest.mock import patch

from app.config import settings
from app.session_manager import SessionManager


original_key_set_url = settings.KEY_SET_URL
settings.KEY_SET_URL = "https://lms.example.invalid/jwks"
with patch.object(SessionManager, "__init__", return_value=None):
    from app.main import app
settings.KEY_SET_URL = original_key_set_url


class PublicHealthRouteTests(unittest.TestCase):
    def test_internal_and_same_origin_health_routes_are_registered(self):
        route_paths = {route.path for route in app.routes}

        self.assertIn("/health", route_paths)
        self.assertIn("/health/ready", route_paths)
        self.assertIn("/lti/health", route_paths)
        self.assertIn("/lti/health/ready", route_paths)


if __name__ == "__main__":
    unittest.main()
