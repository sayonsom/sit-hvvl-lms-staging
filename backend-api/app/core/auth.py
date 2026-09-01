import os
import secrets
from dataclasses import dataclass, field
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException
from jwt.exceptions import InvalidTokenError

API_SERVICE_TOKEN = os.getenv("API_SERVICE_TOKEN", "")
BACKEND_API_JWT_SECRET = os.getenv("BACKEND_API_JWT_SECRET") or os.getenv("VHVL_SIGNING_KEY", "")
BACKEND_API_JWT_AUDIENCE = os.getenv("BACKEND_API_JWT_AUDIENCE", "")


@dataclass(frozen=True)
class AuthenticatedActor:
    subject: str
    email: str | None
    roles: set[str] = field(default_factory=set)
    auth_method: str = "unknown"
    course_id: str | None = None
    course_ids: set[str] = field(default_factory=set)
    claims: dict[str, Any] = field(default_factory=dict)

    def has_any_role(self, *roles: str) -> bool:
        return bool(self.roles.intersection(roles))

    @property
    def is_service(self) -> bool:
        return "service" in self.roles

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles

    @property
    def is_teacher(self) -> bool:
        return "teacher" in self.roles or "admin" in self.roles

    @property
    def is_student(self) -> bool:
        return "student" in self.roles


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [value]
    return []


def _normalize_role(role: Any) -> str | None:
    if not isinstance(role, str):
        return None
    value = role.strip().lower()
    if not value:
        return None
    role_name = value.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    if role_name in {"learner", "student"}:
        return "student"
    if role_name in {"instructor", "teachingassistant", "ta", "teacher", "staff"}:
        return "teacher"
    if role_name in {"administrator", "admin", "superadmin"}:
        return "admin"
    if role_name == "service":
        return "service"
    return role_name


def _normalize_roles(raw_roles: Any, auth_method: str | None = None) -> set[str]:
    roles = {
        normalized
        for normalized in (_normalize_role(role) for role in _as_list(raw_roles))
        if normalized
    }
    if not roles:
        if auth_method == "lti":
            roles.add("student")
        elif auth_method == "staff":
            roles.add("teacher")
    return roles


def _extract_email(claims: dict[str, Any]) -> str | None:
    for key in ("email", "upn", "unique_name", "preferred_username"):
        value = claims.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    user = claims.get("user")
    if isinstance(user, dict):
        return _extract_email(user)
    return None


def _extract_subject(claims: dict[str, Any], email: str | None) -> str:
    for key in ("sub", "user_id", "oid"):
        value = claims.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return email or "unknown"


def _extract_course_id(claims: dict[str, Any]) -> str | None:
    for key in ("course_id", "context_id"):
        value = claims.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    course = claims.get("course")
    if isinstance(course, dict):
        for key in ("course_id", "context_id", "id"):
            value = course.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    context = claims.get("context")
    if isinstance(context, dict):
        value = context.get("id")
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _extract_course_ids(claims: dict[str, Any]) -> set[str]:
    values = _as_list(claims.get("course_ids"))
    course_ids = {str(value).strip() for value in values if str(value).strip()}
    single_course_id = _extract_course_id(claims)
    if single_course_id:
        course_ids.add(single_course_id)
    return course_ids


async def require_service_token(
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
):
    if not API_SERVICE_TOKEN:
        raise HTTPException(status_code=503, detail="Service token authentication is not configured")
    if not x_service_token or not secrets.compare_digest(x_service_token, API_SERVICE_TOKEN):
        raise HTTPException(status_code=403, detail="Invalid service token")
    return {"sub": "trusted-service", "roles": ["service"]}


async def get_authenticated_actor(
    authorization: str | None = Header(default=None),
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
) -> AuthenticatedActor:
    if API_SERVICE_TOKEN and x_service_token and secrets.compare_digest(x_service_token, API_SERVICE_TOKEN):
        return AuthenticatedActor(
            subject="trusted-service",
            email=None,
            roles={"service", "admin"},
            auth_method="service",
            claims={"sub": "trusted-service", "roles": ["service", "admin"]},
        )

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    if not BACKEND_API_JWT_SECRET:
        raise HTTPException(status_code=503, detail="Backend API token validation is not configured")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        decode_kwargs: dict[str, Any] = {
            "key": BACKEND_API_JWT_SECRET,
            "algorithms": ["HS256"],
        }
        if BACKEND_API_JWT_AUDIENCE:
            decode_kwargs["audience"] = BACKEND_API_JWT_AUDIENCE
        else:
            decode_kwargs["options"] = {"verify_aud": False}
        claims = jwt.decode(token, **decode_kwargs)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired bearer token")

    auth_method = str(claims.get("auth_method") or claims.get("typ") or "unknown")
    email = _extract_email(claims)
    roles = _normalize_roles(claims.get("roles"), auth_method=auth_method)
    subject = _extract_subject(claims, email)
    return AuthenticatedActor(
        subject=subject,
        email=email,
        roles=roles,
        auth_method=auth_method,
        course_id=_extract_course_id(claims),
        course_ids=_extract_course_ids(claims),
        claims=claims,
    )


async def get_optional_authenticated_actor(
    authorization: str | None = Header(default=None),
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
) -> AuthenticatedActor | None:
    if not authorization and not x_service_token:
        return None
    return await get_authenticated_actor(authorization=authorization, x_service_token=x_service_token)


def require_actor_with_any_role(*roles: str):
    required = set(roles)

    async def checker(
        actor: AuthenticatedActor = Depends(get_authenticated_actor),
    ) -> AuthenticatedActor:
        if actor.roles.intersection(required):
            return actor
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return checker


require_authenticated_user = get_authenticated_actor
require_staff_actor = require_actor_with_any_role("teacher", "admin", "service")
require_admin_or_service_actor = require_actor_with_any_role("admin", "service")
