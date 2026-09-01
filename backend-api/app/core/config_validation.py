import os
from collections.abc import Mapping


_PLACEHOLDER_MARKERS = ("changeme", "change_me", "replace_with", "placeholder", "<", ">")


def _is_configured(value: str) -> bool:
    normalized = value.strip().lower()
    return bool(normalized) and not any(marker in normalized for marker in _PLACEHOLDER_MARKERS)


def readiness_configuration_errors(environ: Mapping[str, str] | None = None) -> list[str]:
    values = environ if environ is not None else os.environ
    checks = {
        "database_password": (values.get("DB_PASSWORD", ""), 16),
        "service_token": (values.get("API_SERVICE_TOKEN", ""), 32),
        "jwt_secret": (
            values.get("BACKEND_API_JWT_SECRET", "") or values.get("VHVL_SIGNING_KEY", ""),
            32,
        ),
        "jwt_audience": (values.get("BACKEND_API_JWT_AUDIENCE", ""), 1),
        "storage_signing_key": (values.get("LOCAL_STORAGE_SIGNING_KEY", ""), 32),
    }
    errors = [
        name
        for name, (value, minimum_length) in checks.items()
        if not _is_configured(value) or len(value) < minimum_length
    ]

    independent_secrets = [
        checks["service_token"][0],
        checks["jwt_secret"][0],
        checks["storage_signing_key"][0],
    ]
    if (
        all(_is_configured(value) for value in independent_secrets)
        and len(set(independent_secrets)) != len(independent_secrets)
    ):
        errors.append("independent_signing_secrets")

    return sorted(errors)
