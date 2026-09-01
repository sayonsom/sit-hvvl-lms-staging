"""
Configuration management for LTI Backend Service
Reads from environment variables with sensible defaults
"""
import os
from typing import List
from pydantic_settings import BaseSettings


_PLACEHOLDER_MARKERS = (
    "replace_with",
    "changeme",
    "change_me",
    "<",
    ">",
)


class Settings(BaseSettings):
    """Application settings"""
    
    # LTI 1.3 Configuration
    CLIENT_ID: str = os.getenv("CLIENT_ID", "")
    LTI_CLIENT_IDS: str = os.getenv("LTI_CLIENT_IDS", "")
    DEPLOYMENT_ID: str = os.getenv("DEPLOYMENT_ID", "")
    LTI_DEPLOYMENT_IDS: str = os.getenv("LTI_DEPLOYMENT_IDS", "")
    ISSUER: str = os.getenv("ISSUER", "")
    AUTHORIZATION_ENDPOINT: str = os.getenv("AUTHORIZATION_ENDPOINT", "")
    KEY_SET_URL: str = os.getenv("KEY_SET_URL", "")
    LTI_CLOCK_SKEW_SECONDS: int = int(os.getenv("LTI_CLOCK_SKEW_SECONDS", "60"))
    LTI_JWKS_TIMEOUT_SECONDS: int = int(os.getenv("LTI_JWKS_TIMEOUT_SECONDS", "10"))
    
    # Tool Configuration
    TOOL_URL: str = os.getenv("TOOL_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Redis Configuration for Session Management
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    
    # Session Configuration
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "28800"))  # 8 hours default
    STATE_TTL: int = int(os.getenv("STATE_TTL", "300"))  # 5 minutes for state/nonce
    LOGIN_CODE_TTL: int = int(os.getenv("LOGIN_CODE_TTL", "60"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into list"""
        return self._split_csv(self.ALLOWED_ORIGINS)
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENABLE_API_DOCS: bool = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Backend API (for creating/syncing students)
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8080/api/v1")
    BACKEND_API_SERVICE_TOKEN: str = os.getenv("BACKEND_API_SERVICE_TOKEN", "")
    BACKEND_API_JWT_SECRET: str = os.getenv(
        "BACKEND_API_JWT_SECRET",
        os.getenv("VHVL_SIGNING_KEY", ""),
    )
    BACKEND_API_JWT_AUDIENCE: str = os.getenv("BACKEND_API_JWT_AUDIENCE", "")

    # Staff/Admin OIDC (server-side exchange to avoid browser CORS on ADFS token endpoint)
    STAFF_OIDC_CLIENT_ID: str = os.getenv("STAFF_OIDC_CLIENT_ID", "")
    STAFF_OIDC_AUTHORITY: str = os.getenv("STAFF_OIDC_AUTHORITY", "")
    STAFF_OIDC_REDIRECT_URI: str = os.getenv("STAFF_OIDC_REDIRECT_URI", "")
    STAFF_OIDC_SCOPES: str = os.getenv("STAFF_OIDC_SCOPES", "openid")
    STAFF_OIDC_METADATA_URL: str = os.getenv("STAFF_OIDC_METADATA_URL", "")
    STAFF_OIDC_POST_LOGOUT_REDIRECT_URI: str = os.getenv("STAFF_OIDC_POST_LOGOUT_REDIRECT_URI", "")
    STAFF_ALLOWED_EMAIL_DOMAIN: str = os.getenv(
        "STAFF_ALLOWED_EMAIL_DOMAIN",
        os.getenv("AAD_ALLOWED_EMAIL_DOMAIN", ""),
    )
    STAFF_ALLOWED_EMAILS: str = os.getenv(
        "STAFF_ALLOWED_EMAILS",
        os.getenv("AAD_ALLOWED_EMAILS", ""),
    )
    STAFF_ALLOWED_ROLES: str = os.getenv(
        "STAFF_ALLOWED_ROLES",
        os.getenv("AAD_ALLOWED_ROLES", ""),
    )
    STAFF_ALLOWED_GROUP_IDS: str = os.getenv(
        "STAFF_ALLOWED_GROUP_IDS",
        os.getenv("AAD_ALLOWED_GROUP_IDS", ""),
    )
    STAFF_ADMIN_EMAILS: str = os.getenv("STAFF_ADMIN_EMAILS", "")
    STAFF_COURSE_IDS: str = os.getenv("STAFF_COURSE_IDS", "")
    REQUIRE_STAFF_OIDC: bool = os.getenv("REQUIRE_STAFF_OIDC", "false").lower() == "true"

    @staticmethod
    def _split_csv(raw: str) -> List[str]:
        return [item.strip() for item in raw.split(",") if item.strip()]

    @staticmethod
    def _is_configured_value(value: str) -> bool:
        normalized = value.strip().lower()
        return bool(normalized) and not any(marker in normalized for marker in _PLACEHOLDER_MARKERS)

    @property
    def lti_client_ids_list(self) -> List[str]:
        values = self._split_csv(self.LTI_CLIENT_IDS)
        if not values and self.CLIENT_ID.strip():
            values = [self.CLIENT_ID.strip()]
        return list(dict.fromkeys(values))

    @property
    def lti_deployment_ids_list(self) -> List[str]:
        values = self._split_csv(self.LTI_DEPLOYMENT_IDS)
        if not values and self.DEPLOYMENT_ID.strip():
            values = [self.DEPLOYMENT_ID.strip()]
        return list(dict.fromkeys(values))

    @property
    def lti_configuration_errors(self) -> List[str]:
        checks = {
            "client_id": [self.CLIENT_ID],
            "client_id_allowlist": self.lti_client_ids_list,
            "deployment_id": [self.DEPLOYMENT_ID],
            "deployment_id_allowlist": self.lti_deployment_ids_list,
            "issuer": [self.ISSUER],
            "authorization_endpoint": [self.AUTHORIZATION_ENDPOINT],
            "key_set_url": [self.KEY_SET_URL],
            "tool_url": [self.TOOL_URL],
            "frontend_url": [self.FRONTEND_URL],
        }
        return [
            name
            for name, values in checks.items()
            if not values or any(not self._is_configured_value(value) for value in values)
        ]

    @staticmethod
    def _is_strong_secret(value: str) -> bool:
        return Settings._is_configured_value(value) and len(value) >= 32

    @property
    def readiness_configuration_errors(self) -> List[str]:
        errors = list(self.lti_configuration_errors)
        secret_checks = {
            "backend_api_service_token": self.BACKEND_API_SERVICE_TOKEN,
            "backend_api_jwt_secret": self.BACKEND_API_JWT_SECRET,
        }
        errors.extend(
            name for name, value in secret_checks.items() if not self._is_strong_secret(value)
        )
        if not self._is_configured_value(self.BACKEND_API_JWT_AUDIENCE):
            errors.append("backend_api_jwt_audience")
        if (
            self.BACKEND_API_SERVICE_TOKEN == self.BACKEND_API_JWT_SECRET
            and self._is_strong_secret(self.BACKEND_API_SERVICE_TOKEN)
        ):
            errors.append("independent_backend_secrets")

        if self.REQUIRE_STAFF_OIDC:
            staff_checks = {
                "staff_oidc_client_id": self.STAFF_OIDC_CLIENT_ID,
                "staff_oidc_authority": self.STAFF_OIDC_AUTHORITY,
                "staff_oidc_redirect_uri": self.staff_oidc_redirect_uri,
            }
            errors.extend(
                name
                for name, value in staff_checks.items()
                if not self._is_configured_value(value)
            )
            if not any(
                (
                    self.STAFF_ALLOWED_EMAIL_DOMAIN.strip(),
                    self.staff_allowed_emails_list,
                    self.staff_allowed_roles_list,
                    self.staff_allowed_group_ids_list,
                )
            ):
                errors.append("staff_access_policy")

        return sorted(set(errors))

    @property
    def staff_oidc_scopes_list(self) -> List[str]:
        raw = self.STAFF_OIDC_SCOPES.replace(",", " ")
        values = [item.strip() for item in raw.split(" ") if item.strip()]
        return values if values else ["openid"]

    @property
    def staff_allowed_emails_list(self) -> List[str]:
        return [item.lower() for item in self._split_csv(self.STAFF_ALLOWED_EMAILS)]

    @property
    def staff_allowed_roles_list(self) -> List[str]:
        return self._split_csv(self.STAFF_ALLOWED_ROLES)

    @property
    def staff_allowed_group_ids_list(self) -> List[str]:
        return self._split_csv(self.STAFF_ALLOWED_GROUP_IDS)

    @property
    def staff_admin_emails_list(self) -> List[str]:
        return [item.lower() for item in self._split_csv(self.STAFF_ADMIN_EMAILS)]

    @property
    def staff_course_ids_list(self) -> List[str]:
        return list(dict.fromkeys(
            item for item in self._split_csv(self.STAFF_COURSE_IDS) if item.isdigit()
        ))

    @property
    def staff_oidc_redirect_uri(self) -> str:
        if self.STAFF_OIDC_REDIRECT_URI:
            return self.STAFF_OIDC_REDIRECT_URI
        return f"{self.FRONTEND_URL.rstrip('/')}/oauth2/callback"

    @property
    def staff_oidc_metadata_url(self) -> str:
        if self.STAFF_OIDC_METADATA_URL:
            return self.STAFF_OIDC_METADATA_URL
        if not self.STAFF_OIDC_AUTHORITY:
            return ""
        return f"{self.STAFF_OIDC_AUTHORITY.rstrip('/')}/.well-known/openid-configuration"

    @property
    def staff_oidc_post_logout_redirect_uri(self) -> str:
        if self.STAFF_OIDC_POST_LOGOUT_REDIRECT_URI:
            return self.STAFF_OIDC_POST_LOGOUT_REDIRECT_URI
        return f"{self.FRONTEND_URL.rstrip('/')}/staff"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
