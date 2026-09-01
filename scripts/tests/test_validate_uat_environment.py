import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent / "backend-api"))

from app.core.config_validation import readiness_configuration_errors  # noqa: E402
from validate_uat_environment import (  # noqa: E402
    load_environment_file,
    main,
    validate_environment,
)


def valid_environment() -> dict[str, str]:
    return {
        "REACT_APP_AAD_CLIENT_ID": "sit-adfs-public-client-id",
        "REACT_APP_AAD_AUTHORITY": "https://fs-uat.singaporetech.edu.sg/adfs",
        "REACT_APP_AAD_REDIRECT_URI": "https://hvlabonline.singaporetech.edu.sg/oauth2/callback",
        "REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN": "singaporetech.edu.sg",
        "CLIENT_ID": "brightspace-client-id",
        "DEPLOYMENT_ID": "brightspace-deployment-id",
        "ISSUER": "https://xsitestg.singaporetech.edu.sg",
        "AUTHORIZATION_ENDPOINT": "https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate",
        "KEY_SET_URL": "https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks",
        "TOOL_URL": "https://hvlabonline.singaporetech.edu.sg",
        "FRONTEND_URL": "https://hvlabonline.singaporetech.edu.sg",
        "ALLOWED_ORIGINS": "https://hvlabonline.singaporetech.edu.sg,https://xsitestg.singaporetech.edu.sg",
        "CORS_ALLOWED_ORIGINS": "https://hvlabonline.singaporetech.edu.sg,https://xsitestg.singaporetech.edu.sg",
        "CSP_FRAME_ANCESTORS": "'self' https://hvlabonline.singaporetech.edu.sg https://xsitestg.singaporetech.edu.sg",
        "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI": "https://hvlabonline.singaporetech.edu.sg/staff",
        "STAFF_COURSE_IDS": "2",
        "POSTGRES_PASSWORD": "database-password-long-enough",
        "BACKEND_API_SERVICE_TOKEN": "service-token-value-that-is-long-enough-1",
        "BACKEND_API_JWT_SECRET": "jwt-secret-value-that-is-long-enough-2",
        "BACKEND_API_JWT_AUDIENCE": "hvvl-backend-api",
        "LOCAL_STORAGE_SIGNING_KEY": "storage-key-value-that-is-long-enough-3",
    }


class UatEnvironmentValidationTests(unittest.TestCase):
    def test_accepts_complete_production_configuration(self):
        self.assertEqual(validate_environment(valid_environment()), [])

    def test_rejects_legacy_missing_backend_readiness_values(self):
        values = valid_environment()
        for variable in (
            "POSTGRES_PASSWORD",
            "BACKEND_API_SERVICE_TOKEN",
            "BACKEND_API_JWT_SECRET",
            "BACKEND_API_JWT_AUDIENCE",
            "LOCAL_STORAGE_SIGNING_KEY",
        ):
            values.pop(variable)

        variables = {issue.variable for issue in validate_environment(values)}
        self.assertTrue(
            {
                "POSTGRES_PASSWORD",
                "BACKEND_API_SERVICE_TOKEN",
                "BACKEND_API_JWT_SECRET",
                "BACKEND_API_JWT_AUDIENCE",
                "LOCAL_STORAGE_SIGNING_KEY",
            }.issubset(variables)
        )

    def test_preflight_matches_backend_runtime_readiness_rules(self):
        values = valid_environment()
        backend_values = {
            "DB_PASSWORD": values["POSTGRES_PASSWORD"],
            "API_SERVICE_TOKEN": values["BACKEND_API_SERVICE_TOKEN"],
            "BACKEND_API_JWT_SECRET": values["BACKEND_API_JWT_SECRET"],
            "BACKEND_API_JWT_AUDIENCE": values["BACKEND_API_JWT_AUDIENCE"],
            "LOCAL_STORAGE_SIGNING_KEY": values["LOCAL_STORAGE_SIGNING_KEY"],
        }
        self.assertEqual(readiness_configuration_errors(backend_values), [])

        backend_values["API_SERVICE_TOKEN"] = "too-short"
        backend_errors = readiness_configuration_errors(backend_values)
        preflight_errors = validate_environment(
            {**values, "BACKEND_API_SERVICE_TOKEN": "too-short"}
        )
        self.assertIn("service_token", backend_errors)
        self.assertIn(
            "BACKEND_API_SERVICE_TOKEN",
            {issue.variable for issue in preflight_errors},
        )

    def test_rejects_placeholders_reused_secrets_and_invalid_course_ids(self):
        values = valid_environment()
        reused = "same-signing-value-that-is-at-least-32-characters"
        values.update(
            {
                "CLIENT_ID": "<brightspace-client-id>",
                "BACKEND_API_SERVICE_TOKEN": reused,
                "BACKEND_API_JWT_SECRET": reused,
                "LOCAL_STORAGE_SIGNING_KEY": reused,
                "STAFF_COURSE_IDS": "2,not-a-course",
            }
        )

        variables = {issue.variable for issue in validate_environment(values)}
        self.assertIn("CLIENT_ID", variables)
        self.assertIn("BACKEND_API_* / LOCAL_STORAGE_SIGNING_KEY", variables)
        self.assertIn("STAFF_COURSE_IDS", variables)

    def test_loads_quoted_values_and_reports_invalid_lines(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env.uat"
            env_file.write_text(
                "export CSP_FRAME_ANCESTORS='self https://example.edu'\ninvalid line\n",
                encoding="utf-8",
            )
            values, issues = load_environment_file(env_file)

        self.assertEqual(values["CSP_FRAME_ANCESTORS"], "self https://example.edu")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].variable, "ENV_FILE line 2")

    def test_cli_never_prints_secret_values(self):
        values = valid_environment()
        sensitive_value = "do-not-print"
        values["BACKEND_API_SERVICE_TOKEN"] = sensitive_value

        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env.uat"
            env_file.write_text(
                "\n".join(f"{key}={value}" for key, value in values.items()),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            stdout = io.StringIO()
            with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
                exit_code = main([str(env_file)])

        rendered_output = stderr.getvalue() + stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertNotIn(sensitive_value, rendered_output)
        self.assertIn("BACKEND_API_SERVICE_TOKEN", rendered_output)

    def test_cli_reports_unreadable_file_without_secondary_noise(self):
        missing_file = Path("/path/that/does/not/exist/.env.uat")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main([str(missing_file)])

        rendered_output = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("ENV_FILE", rendered_output)
        self.assertNotIn("POSTGRES_PASSWORD", rendered_output)


if __name__ == "__main__":
    unittest.main()
