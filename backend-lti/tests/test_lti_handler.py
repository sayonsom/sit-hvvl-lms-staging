import time
import unittest
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import settings
from app.lti_handler import LTIHandler, LTIValidationError


DEPLOYMENT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
MESSAGE_TYPE_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/message_type"
CONTEXT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/context"
ROLES_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/roles"


class FakeSessionManager:
    def __init__(self):
        self.states = {}

    def store_state(self, state, data):
        self.states[state] = data

    def get_state(self, state):
        return self.states.pop(state, None)


class FakeJwksClient:
    def __init__(self, public_key):
        self.public_key = public_key

    def get_signing_key_from_jwt(self, _token):
        return SimpleNamespace(key=self.public_key)


class LTIHandlerTests(unittest.TestCase):
    def setUp(self):
        self.original = {
            name: getattr(settings, name)
            for name in (
                "CLIENT_ID",
                "LTI_CLIENT_IDS",
                "DEPLOYMENT_ID",
                "LTI_DEPLOYMENT_IDS",
                "ISSUER",
                "AUTHORIZATION_ENDPOINT",
                "KEY_SET_URL",
                "TOOL_URL",
                "FRONTEND_URL",
                "LTI_CLOCK_SKEW_SECONDS",
            )
        }
        settings.CLIENT_ID = "client-primary"
        settings.LTI_CLIENT_IDS = "client-primary,client-secondary"
        settings.DEPLOYMENT_ID = "deployment-primary"
        settings.LTI_DEPLOYMENT_IDS = "deployment-primary,deployment-secondary"
        settings.ISSUER = "https://lms.example.edu"
        settings.AUTHORIZATION_ENDPOINT = "https://lms.example.edu/d2l/lti/authenticate"
        settings.KEY_SET_URL = "https://lms.example.edu/d2l/.well-known/jwks"
        settings.TOOL_URL = "https://tool.example.edu"
        settings.FRONTEND_URL = "https://tool.example.edu"
        settings.LTI_CLOCK_SKEW_SECONDS = 60

        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.session_manager = FakeSessionManager()
        self.handler = LTIHandler(
            session_manager=self.session_manager,
            jwks_client=FakeJwksClient(self.private_key.public_key()),
        )

    def tearDown(self):
        for name, value in self.original.items():
            setattr(settings, name, value)

    def _token(self, *, audience="client-secondary", nonce="nonce-1", deployment="deployment-primary"):
        now = int(time.time())
        claims = {
            "iss": settings.ISSUER,
            "aud": audience,
            "sub": "student-1",
            "email": "student@example.edu",
            "name": "Student One",
            "iat": now,
            "exp": now + 300,
            "nonce": nonce,
            DEPLOYMENT_CLAIM: deployment,
            MESSAGE_TYPE_CLAIM: "LtiResourceLinkRequest",
            CONTEXT_CLAIM: {"id": "course-1", "label": "C1", "title": "Course One"},
            ROLES_CLAIM: ["http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"],
        }
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    def test_login_binds_allowlisted_client_and_issuer_into_state(self):
        auth_url = self.handler.handle_login(
            iss=settings.ISSUER,
            login_hint="opaque-login-hint",
            target_link_uri="https://tool.example.edu/courses/1",
            client_id="client-secondary",
        )

        query = parse_qs(urlparse(auth_url).query)
        state = query["state"][0]
        self.assertEqual(query["client_id"], ["client-secondary"])
        self.assertEqual(self.session_manager.states[state]["client_id"], "client-secondary")
        self.assertEqual(self.session_manager.states[state]["iss"], settings.ISSUER)

    def test_login_rejects_unregistered_client(self):
        with self.assertRaises(LTIValidationError) as context:
            self.handler.handle_login(
                iss=settings.ISSUER,
                login_hint="opaque-login-hint",
                target_link_uri="https://tool.example.edu/courses/1",
                client_id="attacker-client",
            )
        self.assertEqual(context.exception.reason, "invalid_client")

    def test_launch_uses_client_bound_to_state(self):
        self.session_manager.states["state-1"] = {
            "nonce": "nonce-1",
            "iss": settings.ISSUER,
            "client_id": "client-secondary",
        }
        user, course = self.handler.handle_launch(self._token(), "state-1")
        self.assertEqual(user["email"], "student@example.edu")
        self.assertEqual(course["course_id"], "course-1")
        self.assertNotIn("state-1", self.session_manager.states)

    def test_launch_rejects_token_for_different_audience(self):
        self.session_manager.states["state-2"] = {
            "nonce": "nonce-1",
            "iss": settings.ISSUER,
            "client_id": "client-primary",
        }
        with self.assertRaises(LTIValidationError) as context:
            self.handler.handle_launch(self._token(audience="client-secondary"), "state-2")
        self.assertEqual(context.exception.reason, "invalid_audience")

    def test_launch_rejects_unknown_deployment(self):
        self.session_manager.states["state-3"] = {
            "nonce": "nonce-1",
            "iss": settings.ISSUER,
            "client_id": "client-secondary",
        }
        with self.assertRaises(LTIValidationError) as context:
            self.handler.handle_launch(self._token(deployment="unknown-deployment"), "state-3")
        self.assertEqual(context.exception.reason, "invalid_deployment")

    def test_launch_rejects_nonce_mismatch(self):
        self.session_manager.states["state-4"] = {
            "nonce": "expected-nonce",
            "iss": settings.ISSUER,
            "client_id": "client-secondary",
        }
        with self.assertRaises(LTIValidationError) as context:
            self.handler.handle_launch(self._token(nonce="wrong-nonce"), "state-4")
        self.assertEqual(context.exception.reason, "invalid_nonce")


if __name__ == "__main__":
    unittest.main()
