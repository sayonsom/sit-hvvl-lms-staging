import contextlib
import io
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from deploy_staging import (  # noqa: E402
    STAGING_COMPOSE_PROJECT,
    STAGING_ORIGIN,
    main,
    prepare_staging_environment,
)


def valid_environment(password: str = "database-password-long-enough") -> dict[str, str]:
    return {
        "REACT_APP_AAD_CLIENT_ID": "sit-adfs-public-client-id",
        "REACT_APP_AAD_AUTHORITY": "https://fs-uat.singaporetech.edu.sg/adfs",
        "REACT_APP_AAD_REDIRECT_URI": f"{STAGING_ORIGIN}/oauth2/callback",
        "REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN": "singaporetech.edu.sg",
        "CLIENT_ID": "brightspace-client-id",
        "DEPLOYMENT_ID": "brightspace-deployment-id",
        "ISSUER": "https://xsitestg.singaporetech.edu.sg",
        "AUTHORIZATION_ENDPOINT": "https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate",
        "KEY_SET_URL": "https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks",
        "TOOL_URL": STAGING_ORIGIN,
        "FRONTEND_URL": STAGING_ORIGIN,
        "ALLOWED_ORIGINS": f"{STAGING_ORIGIN},https://xsitestg.singaporetech.edu.sg",
        "CORS_ALLOWED_ORIGINS": f"{STAGING_ORIGIN},https://xsitestg.singaporetech.edu.sg",
        "CSP_FRAME_ANCESTORS": f"'self' {STAGING_ORIGIN} https://xsitestg.singaporetech.edu.sg",
        "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI": f"{STAGING_ORIGIN}/staff",
        "STAFF_COURSE_IDS": "2",
        "POSTGRES_DB": "aligndb",
        "POSTGRES_USER": "alignuser",
        "POSTGRES_PASSWORD": password,
        "BACKEND_API_SERVICE_TOKEN": "service-token-value-that-is-long-enough-1",
        "BACKEND_API_JWT_SECRET": "jwt-secret-value-that-is-long-enough-2",
        "BACKEND_API_JWT_AUDIENCE": "hvvl-backend-api",
        "LOCAL_STORAGE_SIGNING_KEY": "storage-key-value-that-is-long-enough-3",
    }


def write_environment(directory: str, values: dict[str, str]) -> Path:
    env_path = Path(directory) / ".env.uat"
    env_path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )
    return env_path


class StagingEnvironmentPreparationTests(unittest.TestCase):
    def test_replaces_legacy_password_without_printing_old_or_new_values(self):
        legacy_password = "legacy-short"
        generated_password = "generated-password-that-is-more-than-sixteen-characters"
        values = valid_environment(legacy_password)

        with tempfile.TemporaryDirectory() as directory:
            env_path = write_environment(directory, values)
            stdout = io.StringIO()
            with mock.patch(
                "deploy_staging.secrets.token_urlsafe",
                return_value=generated_password,
            ), contextlib.redirect_stdout(stdout):
                generated = prepare_staging_environment(env_path)

            rendered_file = env_path.read_text(encoding="utf-8")
            rendered_output = stdout.getvalue()
            self.assertTrue(generated)
            self.assertIn(f"POSTGRES_PASSWORD={generated_password}", rendered_file)
            self.assertNotIn(legacy_password, rendered_file)
            self.assertNotIn(legacy_password, rendered_output)
            self.assertNotIn(generated_password, rendered_output)
            self.assertEqual(stat.S_IMODE(env_path.stat().st_mode), 0o600)

    def test_retry_with_strong_password_is_idempotent(self):
        values = valid_environment()
        with tempfile.TemporaryDirectory() as directory:
            env_path = write_environment(directory, values)
            original = env_path.read_bytes()
            generated = prepare_staging_environment(env_path)

            self.assertFalse(generated)
            self.assertEqual(env_path.read_bytes(), original)
            self.assertEqual(stat.S_IMODE(env_path.stat().st_mode), 0o600)

    def test_refuses_production_environment(self):
        values = valid_environment()
        values["FRONTEND_URL"] = "https://hvlabonline.singaporetech.edu.sg"
        with tempfile.TemporaryDirectory() as directory:
            env_path = write_environment(directory, values)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(env_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("staging-host guard", stderr.getvalue())

    def test_main_always_uses_data_preserving_rotation(self):
        values = valid_environment()
        with tempfile.TemporaryDirectory() as directory:
            env_path = write_environment(directory, values)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPOSE_PROJECT_NAME", None)
                with mock.patch("deploy_staging.deploy") as deploy_mock:
                    exit_code = main([str(env_path)])
                self.assertEqual(
                    os.environ["COMPOSE_PROJECT_NAME"],
                    STAGING_COMPOSE_PROJECT,
                )

        self.assertEqual(exit_code, 0)
        deploy_mock.assert_called_once_with(
            env_path.resolve(),
            rotate_password=True,
            wait_timeout=240,
        )

    def test_rejects_symbolic_link_before_modifying_legacy_password(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symbolic links are unavailable")

        with tempfile.TemporaryDirectory() as directory:
            real_path = write_environment(directory, valid_environment("legacy-short"))
            link_path = Path(directory) / "linked.env"
            link_path.symlink_to(real_path)
            with self.assertRaisesRegex(Exception, "symbolic-link"):
                prepare_staging_environment(link_path)


if __name__ == "__main__":
    unittest.main()
