#!/usr/bin/env python3
"""One-command, data-preserving deployment for the dedicated SIT staging host.

The server-owned ``.env.uat`` remains the source of truth and is never printed.
For a legacy short PostgreSQL password, this command generates a strong value,
stores it in the environment file with mode 0600, and rotates the existing
PostgreSQL role over the container's local socket before starting the stack.
"""

from __future__ import annotations

import argparse
import os
import secrets
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from deploy_uat_stack import DeploymentError, deploy
from validate_uat_environment import (
    ValidationIssue,
    load_environment_file,
    validate_environment,
)


STAGING_ORIGIN = "https://hvlabonline-uat.singaporetech.edu.sg"
STAGING_COMPOSE_PROJECT = "sit_test_v1"
PASSWORD_VARIABLE = "POSTGRES_PASSWORD"
PASSWORD_MINIMUM_LENGTH = 16


def _configured_password(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        len(value) >= PASSWORD_MINIMUM_LENGTH
        and bool(normalized)
        and not any(
            marker in normalized
            for marker in (
                "changeme",
                "change_me",
                "replace_with",
                "placeholder",
                "<",
                ">",
            )
        )
    )


def _print_issues(env_path: Path, issues: Sequence[ValidationIssue]) -> None:
    print(f"ERROR: {env_path} is not ready for staging:", file=sys.stderr)
    for issue in sorted(set(issues)):
        print(f"- {issue.variable}: {issue.message}", file=sys.stderr)
    print("No configured values were printed.", file=sys.stderr)


def _replace_password(env_path: Path, password: str) -> None:
    """Atomically replace exactly one POSTGRES_PASSWORD assignment."""

    if env_path.is_symlink():
        raise DeploymentError("refusing to modify a symbolic-link environment file")

    metadata = env_path.stat()
    original = env_path.read_text(encoding="utf-8")
    output: list[str] = []
    replacements = 0
    for raw_line in original.splitlines(keepends=True):
        candidate = raw_line.strip()
        if candidate.startswith("export "):
            candidate = candidate.removeprefix("export ").lstrip()
        key = candidate.split("=", 1)[0].strip() if "=" in candidate else ""
        if key == PASSWORD_VARIABLE:
            newline = "\r\n" if raw_line.endswith("\r\n") else "\n"
            output.append(f"{PASSWORD_VARIABLE}={password}{newline}")
            replacements += 1
        else:
            output.append(raw_line)

    if replacements != 1:
        raise DeploymentError(
            "the environment file must contain exactly one POSTGRES_PASSWORD assignment"
        )

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{env_path.name}.",
        dir=env_path.parent,
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.writelines(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, stat.S_IRUSR | stat.S_IWUSR)
        try:
            os.chown(temporary_path, metadata.st_uid, metadata.st_gid)
        except PermissionError:
            pass
        os.replace(temporary_path, env_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def prepare_staging_environment(env_path: Path) -> bool:
    """Validate staging identity and repair a legacy database password if needed.

    Returns True when a new PostgreSQL password was generated.
    """

    values, parse_issues = load_environment_file(env_path)
    if parse_issues:
        _print_issues(env_path, parse_issues)
        raise DeploymentError("environment parsing failed")

    frontend_url = values.get("FRONTEND_URL", "").rstrip("/")
    if frontend_url != STAGING_ORIGIN:
        _print_issues(
            env_path,
            [
                ValidationIssue(
                    "FRONTEND_URL",
                    f"must be the dedicated staging origin {STAGING_ORIGIN}",
                )
            ],
        )
        raise DeploymentError("staging-host guard failed")

    generated = not _configured_password(values.get(PASSWORD_VARIABLE, ""))
    if generated:
        candidate_password = secrets.token_urlsafe(48)
        candidate_values = {**values, PASSWORD_VARIABLE: candidate_password}
        non_password_issues = [
            issue
            for issue in validate_environment(candidate_values)
            if issue.variable != PASSWORD_VARIABLE
        ]
        if non_password_issues:
            _print_issues(env_path, non_password_issues)
            raise DeploymentError("environment preflight failed")
        _replace_password(env_path, candidate_password)
        print(
            "PASS: replaced the legacy PostgreSQL password in .env.uat "
            "with a generated strong value (value redacted)."
        )
    else:
        issues = validate_environment(values)
        if issues:
            _print_issues(env_path, issues)
            raise DeploymentError("environment preflight failed")
        os.chmod(env_path, stat.S_IRUSR | stat.S_IWUSR)

    return generated


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Repair and deploy the dedicated SIT HVVL staging stack safely."
    )
    parser.add_argument("env_file", nargs="?", default=".env.uat")
    parser.add_argument("--wait-timeout", type=int, default=240)
    args = parser.parse_args(argv)

    if args.wait_timeout < 30:
        parser.error("--wait-timeout must be at least 30 seconds")

    env_path = Path(args.env_file).resolve()
    try:
        prepare_staging_environment(env_path)
        # The existing UAT database, Redis, and local-storage volumes were
        # created under this Compose project name in /usr/local/src/sit_test_v1.
        # Keep using them even though this repository has a new directory name.
        os.environ.setdefault("COMPOSE_PROJECT_NAME", STAGING_COMPOSE_PROJECT)
        # Staging's server-owned environment is authoritative. Rotating the
        # role to the configured value on every run makes retries idempotent,
        # including a retry after interruption between file update and ALTER ROLE.
        deploy(env_path, rotate_password=True, wait_timeout=args.wait_timeout)
    except (DeploymentError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("PASS: SIT HVVL staging deployment completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
