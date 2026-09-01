"""
Staff/Admin OIDC Handler (BFF-style)
Performs server-side code exchange to avoid browser CORS dependency on ADFS token endpoint.
"""
import base64
import hashlib
import json
import logging
import secrets
import urllib.parse
from typing import Any, Dict, Optional, Tuple

import httpx
import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

from .config import settings
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class StaffOIDCHandler:
    """Handles staff/admin OIDC login and callback exchange."""

    def __init__(self):
        self.session_manager = SessionManager()
        self._metadata: Optional[Dict[str, Any]] = None
        self._jwks_client: Optional[PyJWKClient] = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.STAFF_OIDC_CLIENT_ID and settings.STAFF_OIDC_AUTHORITY)

    async def build_authorization_url(self, prompt: Optional[str] = None) -> str:
        if not self.is_configured:
            raise ValueError("Staff OIDC is not configured.")

        metadata = await self._get_metadata()
        authorization_endpoint = metadata.get("authorization_endpoint")
        if not authorization_endpoint:
            raise ValueError("OIDC metadata missing authorization endpoint.")

        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self._generate_pkce_pair()
        self._store_state(
            state,
            {
                "nonce": nonce,
                "code_verifier": code_verifier,
            },
        )

        params = {
            "response_type": "code",
            "client_id": settings.STAFF_OIDC_CLIENT_ID,
            "redirect_uri": settings.staff_oidc_redirect_uri,
            "scope": " ".join(settings.staff_oidc_scopes_list),
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        prompt_value = self._normalize_prompt(prompt)
        if prompt_value:
            params["prompt"] = prompt_value

        query = urllib.parse.urlencode(params, safe=":/", quote_via=urllib.parse.quote)
        separator = "&" if "?" in authorization_endpoint else "?"
        return f"{authorization_endpoint}{separator}{query}"

    @staticmethod
    def _normalize_prompt(prompt: Optional[str]) -> Optional[str]:
        if not prompt:
            return None
        normalized = prompt.strip()
        allowed_values = {"none", "login", "consent", "select_account"}
        if normalized in allowed_values:
            return normalized
        return None

    async def exchange_code(self, code: str, state: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if not self.is_configured:
            raise ValueError("Staff OIDC is not configured.")

        state_data = self._consume_state(state)
        if not state_data:
            raise ValueError("Invalid or expired sign-in state.")

        metadata = await self._get_metadata()
        token_endpoint = metadata.get("token_endpoint")
        if not token_endpoint:
            raise ValueError("OIDC metadata missing token endpoint.")

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.STAFF_OIDC_CLIENT_ID,
            "redirect_uri": settings.staff_oidc_redirect_uri,
            "code_verifier": state_data.get("code_verifier", ""),
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                token_endpoint,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            detail = self._extract_token_error(response)
            logger.error("Staff token exchange failed")
            raise ValueError(detail)

        token_data = response.json()
        id_token = token_data.get("id_token")
        if not id_token:
            raise ValueError("Token endpoint did not return id_token.")

        expected_nonce = state_data.get("nonce")
        claims = self._validate_id_token(
            id_token=id_token,
            expected_nonce=expected_nonce,
            issuer=metadata.get("issuer", ""),
        )
        user = self._extract_user_info(claims)
        return user, claims

    async def build_logout_url(self) -> str:
        if not self.is_configured:
            raise ValueError("Staff OIDC is not configured.")

        metadata = await self._get_metadata()
        end_session_endpoint = metadata.get("end_session_endpoint")

        if end_session_endpoint:
            params = {
                "post_logout_redirect_uri": settings.staff_oidc_post_logout_redirect_uri,
                "client_id": settings.STAFF_OIDC_CLIENT_ID,
            }
            query = urllib.parse.urlencode(params, safe=":/", quote_via=urllib.parse.quote)
            separator = "&" if "?" in end_session_endpoint else "?"
            return f"{end_session_endpoint}{separator}{query}"

        authority = settings.STAFF_OIDC_AUTHORITY.rstrip("/")
        return f"{authority}/ls/?wa=wsignout1.0"

    async def _get_metadata(self) -> Dict[str, Any]:
        if self._metadata:
            return self._metadata

        metadata_url = settings.staff_oidc_metadata_url
        if not metadata_url:
            raise ValueError("Staff OIDC metadata URL is not configured.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(metadata_url)
            response.raise_for_status()
            metadata = response.json()

        jwks_uri = metadata.get("jwks_uri")
        if not jwks_uri:
            raise ValueError("OIDC metadata missing jwks_uri.")

        self._metadata = metadata
        self._jwks_client = PyJWKClient(jwks_uri)
        return self._metadata

    @staticmethod
    def _generate_pkce_pair() -> Tuple[str, str]:
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        ).rstrip(b"=").decode("utf-8")
        return code_verifier, code_challenge

    def _store_state(self, state: str, payload: Dict[str, Any]) -> None:
        key = f"staff_oidc_state:{state}"
        self.session_manager.redis_client.setex(key, settings.STATE_TTL, json.dumps(payload))

    def _consume_state(self, state: str) -> Optional[Dict[str, Any]]:
        key = f"staff_oidc_state:{state}"
        value = self.session_manager.redis_client.getdel(key)
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _extract_token_error(response: httpx.Response) -> str:
        try:
            body = response.json()
            error = body.get("error")
            description = body.get("error_description")
            request_id = body.get("client-request-id") or body.get("client_request_id")
            parts = ["Token exchange failed."]
            if error:
                parts.append(f"Error: {error}.")
            if description:
                parts.append(description)
            if request_id:
                parts.append(f"Request ID: {request_id}")
            return " ".join(parts)
        except Exception:
            text = (response.text or "").strip()
            return f"Token exchange failed ({response.status_code}). {text[:300]}"

    def _validate_id_token(self, id_token: str, expected_nonce: Optional[str], issuer: str) -> Dict[str, Any]:
        if not self._jwks_client:
            raise ValueError("OIDC signing keys are not initialized.")

        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                key=signing_key.key,
                algorithms=["RS256"],
                audience=settings.STAFF_OIDC_CLIENT_ID,
                issuer=issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "aud", "iss", "sub"],
                },
            )
        except InvalidTokenError as error:
            raise ValueError(f"Invalid id_token: {str(error)}") from error

        token_nonce = claims.get("nonce")
        if expected_nonce and (
            not isinstance(token_nonce, str)
            or not secrets.compare_digest(token_nonce, expected_nonce)
        ):
            raise ValueError("Nonce mismatch in id_token.")

        return claims

    @staticmethod
    def _extract_user_info(claims: Dict[str, Any]) -> Dict[str, Any]:
        email = claims.get("email") or claims.get("upn") or claims.get("unique_name") or ""
        name = claims.get("name") or claims.get("unique_name") or email or "Staff User"
        given_name = claims.get("given_name", "")
        family_name = claims.get("family_name", "")
        sub = claims.get("sub", "")

        raw_roles = claims.get("roles")
        if isinstance(raw_roles, list):
            roles = [role for role in raw_roles if isinstance(role, str) and role.strip()]
        elif isinstance(raw_roles, str) and raw_roles.strip():
            roles = [raw_roles.strip()]
        else:
            roles = ["Staff"]

        picture = f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&size=200"

        return {
            "user_id": sub or email or name,
            "name": name,
            "given_name": given_name,
            "family_name": family_name,
            "email": email,
            "picture": picture,
            "roles": roles,
            "sub": sub or email or name,
        }
