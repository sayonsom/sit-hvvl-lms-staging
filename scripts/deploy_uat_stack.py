#!/usr/bin/env python3
"""Deploy the HVVL Compose stack with secret-safe preflight and diagnostics.

The optional PostgreSQL password rotation updates the login role inside an
existing data volume without deleting or reinitialising that volume. Secrets
are read from the server-owned environment file and are never printed or put
on a subprocess command line.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from validate_uat_environment import (
    ValidationIssue,
    load_environment_file,
    validate_environment,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = REPOSITORY_ROOT / "docker-compose.uat.yml"
APPLICATION_SERVICES = ("virtuallab", "backend-api", "lti-backend")


class DeploymentError(RuntimeError):
    """Raised when a deployment command fails after safe diagnostics."""


def _print_validation_errors(env_path: Path, issues: Sequence[ValidationIssue]) -> None:
    print(f"ERROR: {env_path} is not ready for deployment:", file=sys.stderr)
    for issue in sorted(set(issues)):
        print(f"- {issue.variable}: {issue.message}", file=sys.stderr)
    print(
        "No configured values were printed. Correct the listed variables and rerun.",
        file=sys.stderr,
    )
    if any(issue.variable == "POSTGRES_PASSWORD" for issue in issues):
        print(
            "Existing PostgreSQL volumes must be migrated to the same strong password; "
            "after updating the env file, rerun with --rotate-postgres-password.",
            file=sys.stderr,
        )


def _compose_command(env_path: Path, *arguments: str) -> list[str]:
    return [
        "docker",
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        str(COMPOSE_FILE),
        *arguments,
    ]


def _run(
    command: Sequence[str],
    *,
    input_text: str | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    print(f"+ {shlex.join(command)}", flush=True)
    return subprocess.run(
        list(command),
        cwd=REPOSITORY_ROOT,
        check=check,
        text=True,
        input=input_text,
        capture_output=capture_output,
    )


def _sql_identifier(value: str) -> str:
    if not value or "\x00" in value or "\n" in value or "\r" in value:
        raise DeploymentError("PostgreSQL user contains unsupported characters")
    return '"' + value.replace('"', '""') + '"'


def _sql_literal(value: str) -> str:
    if not value or "\x00" in value or "\n" in value or "\r" in value:
        raise DeploymentError("PostgreSQL password contains unsupported characters")
    return "'" + value.replace("'", "''") + "'"


def _database_coordinates(values: dict[str, str]) -> tuple[str, str, str]:
    database_user = values.get("POSTGRES_USER", "alignuser").strip() or "alignuser"
    database_name = values.get("POSTGRES_DB", "aligndb").strip() or "aligndb"
    return database_user, database_name, values["POSTGRES_PASSWORD"]


def _start_postgres(env_path: Path) -> None:
    _run(
        _compose_command(
            env_path,
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            "120",
            "postgres",
        )
    )


def postgres_password_matches(env_path: Path, values: dict[str, str]) -> bool:
    """Verify the configured password over TCP without exposing its value."""

    database_user, database_name, password = _database_coordinates(values)
    verification_script = (
        'IFS= read -r PGPASSWORD; export PGPASSWORD; '
        'exec psql --no-psqlrc -h 127.0.0.1 -U "$1" -d "$2" -c "\\q"'
    )
    result = _run(
        _compose_command(
            env_path,
            "exec",
            "-T",
            "postgres",
            "sh",
            "-ceu",
            verification_script,
            "verify-password",
            database_user,
            database_name,
        ),
        input_text=password + "\n",
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def rotate_postgres_password(env_path: Path, values: dict[str, str]) -> None:
    """Synchronise an existing PostgreSQL role with POSTGRES_PASSWORD."""

    database_user, database_name, password = _database_coordinates(values)

    print("Starting PostgreSQL for a data-preserving role-password rotation...")
    _start_postgres(env_path)

    sql = (
        f"ALTER ROLE {_sql_identifier(database_user)} WITH LOGIN "
        f"PASSWORD {_sql_literal(password)};\n"
    )
    _run(
        _compose_command(
            env_path,
            "exec",
            "-T",
            "postgres",
            "psql",
            "--no-psqlrc",
            "--set=ON_ERROR_STOP=1",
            "--username",
            database_user,
            "--dbname",
            database_name,
        ),
        input_text=sql,
    )

    if not postgres_password_matches(env_path, values):
        raise DeploymentError("PostgreSQL rejected the password after rotation")
    print("PASS: PostgreSQL role password matches the environment file (value redacted).")


def _print_failure_diagnostics(env_path: Path) -> None:
    print("Deployment failed; collecting redacted service diagnostics...", file=sys.stderr)
    _run(_compose_command(env_path, "ps"), check=False)
    _run(
        _compose_command(
            env_path,
            "logs",
            "--tail=200",
            "backend-api",
            "lti-backend",
        ),
        check=False,
    )

    container = _run(
        _compose_command(env_path, "ps", "-q", "backend-api"),
        capture_output=True,
        check=False,
    ).stdout.strip()
    if container:
        _run(
            [
                "docker",
                "inspect",
                "--format",
                "{{range .State.Health.Log}}{{println .Output}}{{end}}",
                container,
            ],
            check=False,
        )


def deploy(
    env_path: Path,
    *,
    rotate_password: bool,
    wait_timeout: int,
) -> None:
    values, parse_issues = load_environment_file(env_path)
    unreadable = any(issue.variable == "ENV_FILE" for issue in parse_issues)
    issues = parse_issues if unreadable else parse_issues + validate_environment(values)
    if issues:
        _print_validation_errors(env_path, issues)
        raise DeploymentError("environment preflight failed")

    print(f"PASS: {env_path} satisfies the deployment policy (values redacted).")
    _run(_compose_command(env_path, "config", "--quiet"))

    if rotate_password:
        rotate_postgres_password(env_path, values)
    else:
        print("Checking the existing PostgreSQL volume before rebuilding applications...")
        _start_postgres(env_path)
        if not postgres_password_matches(env_path, values):
            raise DeploymentError(
                "existing PostgreSQL role does not match POSTGRES_PASSWORD; "
                "rerun once with --rotate-postgres-password"
            )
        print("PASS: PostgreSQL role password matches the environment file (value redacted).")

    _run(_compose_command(env_path, "pull", "redis"))
    _run(
        _compose_command(
            env_path,
            "build",
            "--pull",
            "--no-cache",
            *APPLICATION_SERVICES,
        )
    )
    try:
        _run(
            _compose_command(
                env_path,
                "up",
                "-d",
                "--remove-orphans",
                "--wait",
                "--wait-timeout",
                str(wait_timeout),
            )
        )
    except subprocess.CalledProcessError as error:
        _print_failure_diagnostics(env_path)
        raise DeploymentError("Compose stack did not become healthy") from error

    _run(_compose_command(env_path, "ps"))
    print("PASS: all Compose services reported healthy.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and deploy the HVVL UAT/production Compose stack safely."
    )
    parser.add_argument("env_file", nargs="?", default=".env.uat")
    parser.add_argument(
        "--rotate-postgres-password",
        action="store_true",
        help=(
            "synchronise the existing PostgreSQL role to POSTGRES_PASSWORD before deployment; "
            "does not remove or recreate the data volume"
        ),
    )
    parser.add_argument("--wait-timeout", type=int, default=240)
    args = parser.parse_args(argv)

    if args.wait_timeout < 30:
        parser.error("--wait-timeout must be at least 30 seconds")

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        deploy(
            env_path,
            rotate_password=args.rotate_postgres_password,
            wait_timeout=args.wait_timeout,
        )
    except (DeploymentError, subprocess.CalledProcessError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
