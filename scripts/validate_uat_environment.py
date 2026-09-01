#!/usr/bin/env python3
"""Validate the server-owned UAT environment before rebuilding the stack.

The validator deliberately reports variable names and policy failures only. It
must never echo configured values because the input file contains production
credentials and signing material.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


PLACEHOLDER_MARKERS = (
    "changeme",
    "change_me",
    "replace_with",
    "placeholder",
    "<",
    ">",
)

REQUIRED_CONFIGURATION = (
    "REACT_APP_AAD_CLIENT_ID",
    "REACT_APP_AAD_AUTHORITY",
    "REACT_APP_AAD_REDIRECT_URI",
    "CLIENT_ID",
    "DEPLOYMENT_ID",
    "ISSUER",
    "AUTHORIZATION_ENDPOINT",
    "KEY_SET_URL",
    "TOOL_URL",
    "FRONTEND_URL",
    "ALLOWED_ORIGINS",
    "CORS_ALLOWED_ORIGINS",
    "CSP_FRAME_ANCESTORS",
    "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI",
    "STAFF_COURSE_IDS",
)

HTTPS_URL_CONFIGURATION = (
    "REACT_APP_AAD_AUTHORITY",
    "REACT_APP_AAD_REDIRECT_URI",
    "ISSUER",
    "AUTHORIZATION_ENDPOINT",
    "KEY_SET_URL",
    "TOOL_URL",
    "FRONTEND_URL",
    "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI",
)

SECRET_REQUIREMENTS = {
    "POSTGRES_PASSWORD": 16,
    "BACKEND_API_SERVICE_TOKEN": 32,
    "BACKEND_API_JWT_SECRET": 32,
    "LOCAL_STORAGE_SIGNING_KEY": 32,
}

STAFF_ACCESS_POLICY_KEYS = (
    "REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN",
    "REACT_APP_AAD_ALLOWED_EMAILS",
    "REACT_APP_AAD_ALLOWED_GROUP_IDS",
    "REACT_APP_AAD_ALLOWED_ROLES",
    "STAFF_ALLOWED_EMAIL_DOMAIN",
    "STAFF_ALLOWED_EMAILS",
    "STAFF_ALLOWED_GROUP_IDS",
    "STAFF_ALLOWED_ROLES",
)


@dataclass(frozen=True, order=True)
class ValidationIssue:
    variable: str
    message: str


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_environment_file(path: Path) -> tuple[dict[str, str], list[ValidationIssue]]:
    values: dict[str, str] = {}
    issues: list[ValidationIssue] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return {}, [ValidationIssue("ENV_FILE", "cannot be read as a UTF-8 environment file")]

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            issues.append(
                ValidationIssue(
                    f"ENV_FILE line {line_number}",
                    "must use KEY=VALUE syntax",
                )
            )
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            issues.append(
                ValidationIssue(
                    f"ENV_FILE line {line_number}",
                    "contains an invalid variable name",
                )
            )
            continue
        values[key] = _strip_optional_quotes(value.strip())

    return values, issues


def _is_configured(value: str) -> bool:
    normalized = value.strip().lower()
    return bool(normalized) and not any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def _origin(value: str) -> str:
    parsed = urlsplit(value)
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}" if parsed.netloc else ""


def _csv_values(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def validate_environment(values: dict[str, str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for variable in REQUIRED_CONFIGURATION:
        if not _is_configured(values.get(variable, "")):
            issues.append(
                ValidationIssue(variable, "is missing, blank, or still contains a placeholder")
            )

    for variable in HTTPS_URL_CONFIGURATION:
        value = values.get(variable, "")
        if not _is_configured(value):
            continue
        parsed = urlsplit(value)
        if parsed.scheme.lower() != "https" or not parsed.netloc:
            issues.append(ValidationIssue(variable, "must be an absolute HTTPS URL"))

    for variable, minimum_length in SECRET_REQUIREMENTS.items():
        value = values.get(variable, "")
        if not _is_configured(value) or len(value) < minimum_length:
            issues.append(
                ValidationIssue(
                    variable,
                    f"must be a non-placeholder value of at least {minimum_length} characters",
                )
            )

    signing_values = [
        values.get("BACKEND_API_SERVICE_TOKEN", ""),
        values.get("BACKEND_API_JWT_SECRET", ""),
        values.get("LOCAL_STORAGE_SIGNING_KEY", ""),
    ]
    if all(_is_configured(value) for value in signing_values) and len(set(signing_values)) != 3:
        issues.append(
            ValidationIssue(
                "BACKEND_API_* / LOCAL_STORAGE_SIGNING_KEY",
                "must use three independent values",
            )
        )

    audience = values.get("BACKEND_API_JWT_AUDIENCE", "")
    if not _is_configured(audience):
        issues.append(
            ValidationIssue(
                "BACKEND_API_JWT_AUDIENCE",
                "is missing, blank, or still contains a placeholder",
            )
        )

    if not any(_is_configured(values.get(key, "")) for key in STAFF_ACCESS_POLICY_KEYS):
        issues.append(
            ValidationIssue(
                "STAFF_ACCESS_POLICY",
                "must configure at least one allowed domain, email, group, or role",
            )
        )

    course_ids = _csv_values(values.get("STAFF_COURSE_IDS", ""))
    if course_ids and any(not course_id.isdigit() for course_id in course_ids):
        issues.append(
            ValidationIssue(
                "STAFF_COURSE_IDS",
                "must contain comma-separated numeric internal course IDs",
            )
        )

    frontend_url = values.get("FRONTEND_URL", "").rstrip("/")
    frontend_origin = _origin(frontend_url)
    if frontend_origin:
        for variable in (
            "REACT_APP_AAD_REDIRECT_URI",
            "STAFF_OIDC_POST_LOGOUT_REDIRECT_URI",
            "TOOL_URL",
        ):
            value = values.get(variable, "")
            if _is_configured(value) and _origin(value) != frontend_origin:
                issues.append(
                    ValidationIssue(variable, "must use the same public origin as FRONTEND_URL")
                )

        for variable in ("ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS"):
            origins = {item.rstrip("/") for item in _csv_values(values.get(variable, ""))}
            if frontend_url and frontend_url not in origins:
                issues.append(
                    ValidationIssue(variable, "must include the exact FRONTEND_URL")
                )

        frame_ancestors = values.get("CSP_FRAME_ANCESTORS", "")
        if _is_configured(frame_ancestors) and frontend_url not in frame_ancestors.split():
            issues.append(
                ValidationIssue("CSP_FRAME_ANCESTORS", "must include the exact FRONTEND_URL")
            )

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate HVVL UAT configuration without printing configured values."
    )
    parser.add_argument("env_file", nargs="?", default=".env.uat")
    args = parser.parse_args(argv)

    env_path = Path(args.env_file)
    values, parse_issues = load_environment_file(env_path)
    unreadable_file = any(issue.variable == "ENV_FILE" for issue in parse_issues)
    issues = sorted(set(parse_issues if unreadable_file else parse_issues + validate_environment(values)))

    if issues:
        print(f"ERROR: {env_path} is not ready for deployment:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue.variable}: {issue.message}", file=sys.stderr)
        print("No configured values were printed. Correct the listed variables and rerun.", file=sys.stderr)
        return 1

    print(f"PASS: {env_path} satisfies the UAT readiness policy (values redacted).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
