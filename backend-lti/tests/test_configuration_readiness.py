import unittest

from app.config import settings


class ConfigurationReadinessTests(unittest.TestCase):
    FIELDS = (
        "CLIENT_ID",
        "LTI_CLIENT_IDS",
        "DEPLOYMENT_ID",
        "LTI_DEPLOYMENT_IDS",
        "ISSUER",
        "AUTHORIZATION_ENDPOINT",
        "KEY_SET_URL",
        "TOOL_URL",
        "FRONTEND_URL",
        "BACKEND_API_SERVICE_TOKEN",
        "BACKEND_API_JWT_SECRET",
        "BACKEND_API_JWT_AUDIENCE",
        "REQUIRE_STAFF_OIDC",
        "STAFF_OIDC_CLIENT_ID",
        "STAFF_OIDC_AUTHORITY",
        "STAFF_OIDC_REDIRECT_URI",
        "STAFF_ALLOWED_EMAIL_DOMAIN",
        "STAFF_ALLOWED_EMAILS",
        "STAFF_ALLOWED_ROLES",
        "STAFF_ALLOWED_GROUP_IDS",
        "STAFF_COURSE_IDS",
    )

    def setUp(self):
        self.original = {name: getattr(settings, name) for name in self.FIELDS}
        settings.CLIENT_ID = "brightspace-client"
        settings.LTI_CLIENT_IDS = "brightspace-client"
        settings.DEPLOYMENT_ID = "brightspace-deployment"
        settings.LTI_DEPLOYMENT_IDS = "brightspace-deployment"
        settings.ISSUER = "https://lms.example.edu"
        settings.AUTHORIZATION_ENDPOINT = "https://lms.example.edu/auth"
        settings.KEY_SET_URL = "https://lms.example.edu/jwks"
        settings.TOOL_URL = "https://tool.example.edu"
        settings.FRONTEND_URL = "https://tool.example.edu"
        settings.BACKEND_API_SERVICE_TOKEN = "s" * 40
        settings.BACKEND_API_JWT_SECRET = "j" * 40
        settings.BACKEND_API_JWT_AUDIENCE = "hvvl-backend-api"
        settings.REQUIRE_STAFF_OIDC = True
        settings.STAFF_OIDC_CLIENT_ID = "staff-client"
        settings.STAFF_OIDC_AUTHORITY = "https://idp.example.edu/adfs"
        settings.STAFF_OIDC_REDIRECT_URI = "https://tool.example.edu/oauth2/callback"
        settings.STAFF_ALLOWED_EMAIL_DOMAIN = "example.edu"
        settings.STAFF_ALLOWED_EMAILS = ""
        settings.STAFF_ALLOWED_ROLES = ""
        settings.STAFF_ALLOWED_GROUP_IDS = ""
        settings.STAFF_COURSE_IDS = "2,2,invalid,7"

    def tearDown(self):
        for name, value in self.original.items():
            setattr(settings, name, value)

    def test_accepts_complete_uat_authentication_configuration(self):
        self.assertEqual(settings.readiness_configuration_errors, [])

    def test_rejects_placeholder_registration_and_reused_secrets(self):
        settings.CLIENT_ID = "<brightspace-client-id>"
        settings.LTI_CLIENT_IDS = "<brightspace-client-id>"
        settings.BACKEND_API_JWT_SECRET = settings.BACKEND_API_SERVICE_TOKEN
        errors = settings.readiness_configuration_errors
        self.assertIn("client_id", errors)
        self.assertIn("client_id_allowlist", errors)
        self.assertIn("independent_backend_secrets", errors)

    def test_requires_staff_oidc_when_enabled(self):
        settings.STAFF_OIDC_CLIENT_ID = ""
        settings.STAFF_ALLOWED_EMAIL_DOMAIN = ""
        errors = settings.readiness_configuration_errors
        self.assertIn("staff_oidc_client_id", errors)
        self.assertIn("staff_access_policy", errors)

    def test_staff_course_scope_accepts_only_numeric_ids(self):
        self.assertEqual(settings.staff_course_ids_list, ["2", "7"])


if __name__ == "__main__":
    unittest.main()
