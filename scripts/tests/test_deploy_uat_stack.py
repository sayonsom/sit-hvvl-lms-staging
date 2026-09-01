import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from deploy_uat_stack import (  # noqa: E402
    DeploymentError,
    _sql_identifier,
    _sql_literal,
    deploy,
    rotate_postgres_password,
)


def valid_environment() -> dict[str, str]:
    return {
        "REACT_APP_AAD_CLIENT_ID": "sit-adfs-public-client-id",
        "REACT_APP_AAD_AUTHORITY": "https://fs-uat.singaporetech.edu.sg/adfs",
        "REACT_APP_AAD_REDIRECT_URI": (
            "https://hvlabonline-uat.singaporetech.edu.sg/oauth2/callback"
        ),
        "REACT_APP_AAD_ALLOWED_EMAILS": "teacher@singaporetech.edu.sg",
        "CLIENT_ID": "brightspace-client-id",
        "DEPLOYMENT_ID": "brightspace-deployment-id",
        "ISSUER": "https://xsitestg.singaporetech.edu.sg",
        "AUTHORIZATION_ENDPOINT": (
            "https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate"
        ),
        "KEY_SET_URL": "https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks",
        "TOOL_URL": "https://hvlabonline-uat.singaporetech.edu.sg",
        "FRONTEND_URL": "https://hvlabonline-uat.singaporetech.edu.sg",
        "ALLOWED_ORIGINS": (
            "https://hvlabonline-uat.singaporetech.edu.sg,"
            "https://xsitestg.singaporetech.edu.sg"
        ),
        "CORS_ALLOWED_ORIGINS": (
            "https://hvlabonline-uat.singaporetech.edu.sg,"
            "https://xsitestg.singaporetech.edu.sg"
        ),
        "CSP_FRAME_ANCESTORS": (
            "'self' https://hvlabonline-uat.singaporetech.edu.sg "
            "https://xsitestg.singaporetech.edu.sg"
        ),
        "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI": (
            "https://hvlabonline-uat.singaporetech.edu.sg/staff"
        ),
        "STAFF_COURSE_IDS": "2",
        "POSTGRES_DB": "aligndb",
        "POSTGRES_USER": "alignuser",
        "POSTGRES_PASSWORD": "database-password-long-enough",
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


class PostgresPasswordRotationTests(unittest.TestCase):
    def test_sql_quoting_handles_quotes_without_changing_the_value(self):
        self.assertEqual(_sql_identifier('align"user'), '"align""user"')
        self.assertEqual(_sql_literal("pass'word"), "'pass''word'")

    def test_rejects_multiline_sql_inputs(self):
        with self.assertRaises(DeploymentError):
            _sql_identifier("alignuser\nALTER ROLE")
        with self.assertRaises(DeploymentError):
            _sql_literal("password\nnext-line")

    def test_rotation_keeps_password_off_subprocess_arguments(self):
        values = valid_environment()
        password = values["POSTGRES_PASSWORD"]
        calls: list[tuple[list[str], dict[str, object]]] = []

        def fake_run(command, **kwargs):
            calls.append((list(command), kwargs))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        stdout = io.StringIO()
        with mock.patch("deploy_uat_stack._run", side_effect=fake_run):
            with contextlib.redirect_stdout(stdout):
                rotate_postgres_password(Path("/secure/.env.uat"), values)

        self.assertEqual(len(calls), 3)
        rendered_arguments = "\n".join(" ".join(command) for command, _ in calls)
        self.assertNotIn(password, rendered_arguments)
        self.assertNotIn(password, stdout.getvalue())
        self.assertIn("ALTER ROLE", str(calls[1][1]["input_text"]))
        self.assertEqual(calls[2][1]["input_text"], password + "\n")


class DeploymentPreflightTests(unittest.TestCase):
    def test_weak_existing_password_stops_before_compose_and_explains_migration(self):
        values = valid_environment()
        weak_password = "shortpass"
        values["POSTGRES_PASSWORD"] = weak_password

        with tempfile.TemporaryDirectory() as temporary_directory:
            env_path = write_environment(temporary_directory, values)
            stderr = io.StringIO()
            with mock.patch("deploy_uat_stack._run") as run_mock:
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(DeploymentError):
                        deploy(env_path, rotate_password=False, wait_timeout=240)

        rendered = stderr.getvalue()
        run_mock.assert_not_called()
        self.assertIn("POSTGRES_PASSWORD", rendered)
        self.assertIn("--rotate-postgres-password", rendered)
        self.assertNotIn(weak_password, rendered)

    def test_valid_deployment_runs_preflight_before_compose(self):
        values = valid_environment()

        with tempfile.TemporaryDirectory() as temporary_directory:
            env_path = write_environment(temporary_directory, values)
            completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
            with mock.patch("deploy_uat_stack._run", return_value=completed) as run_mock:
                deploy(env_path, rotate_password=False, wait_timeout=240)

        commands = [call.args[0] for call in run_mock.call_args_list]
        self.assertEqual(commands[0][-2:], ["config", "--quiet"])
        self.assertEqual(commands[1][-1], "postgres")
        self.assertEqual(commands[2][-3:], ["verify-password", "alignuser", "aligndb"])
        self.assertEqual(commands[3][-2:], ["pull", "redis"])
        self.assertIn("build", commands[4])
        self.assertIn("--wait", commands[5])
        self.assertEqual(commands[6][-1], "ps")

    def test_existing_volume_password_mismatch_stops_before_build(self):
        values = valid_environment()

        with tempfile.TemporaryDirectory() as temporary_directory:
            env_path = write_environment(temporary_directory, values)
            successful = subprocess.CompletedProcess([], 0, stdout="", stderr="")
            rejected = subprocess.CompletedProcess([], 1, stdout="", stderr="authentication failed")
            with mock.patch(
                "deploy_uat_stack._run",
                side_effect=[successful, successful, rejected],
            ) as run_mock:
                with self.assertRaisesRegex(
                    DeploymentError,
                    "--rotate-postgres-password",
                ):
                    deploy(env_path, rotate_password=False, wait_timeout=240)

        commands = [call.args[0] for call in run_mock.call_args_list]
        self.assertEqual(len(commands), 3)
        self.assertNotIn("build", [argument for command in commands for argument in command])


if __name__ == "__main__":
    unittest.main()
