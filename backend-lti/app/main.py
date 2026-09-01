"""
FastAPI LTI 1.3 Backend Service
Handles LTI login, launch, and session management for SIT Brightspace integration
"""
from fastapi import FastAPI, Request, Form, Header, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import httpx
import time
import jwt
from typing import Optional
from urllib.parse import urlencode

from .config import settings
from .lti_handler import LTIHandler, LTIValidationError
from .session_manager import SessionManager
from .models import (
    LoginCodeExchangeRequest,
    LoginCodeExchangeResponse,
    SessionResponse,
    StaffCodeExchangeRequest,
    StaffCodeExchangeResponse,
)
from .staff_oidc_handler import StaffOIDCHandler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LTI 1.3 Backend Service",
    description="Handles LTI 1.3 authentication for SIT Brightspace integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_API_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_API_DOCS else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize LTI Handler and Session Manager
lti_handler = LTIHandler()
session_manager = SessionManager()
staff_oidc_handler = StaffOIDCHandler()


def _normalized_backend_roles(user_data: dict, auth_method: str) -> list[str]:
    raw_roles = user_data.get("roles") or []
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]

    roles = {
        str(role).strip().lower()
        for role in raw_roles
        if str(role).strip()
    }

    if auth_method == "staff":
        email = (user_data.get("email") or "").strip().lower()
        if email in settings.staff_admin_emails_list:
            roles.update({"admin", "teacher"})
        if not roles:
            roles.add("teacher")
    elif auth_method == "lti" and not roles:
        roles.add("student")

    return sorted(roles)


def create_backend_api_token(
    user_data: dict,
    course_data: Optional[dict] = None,
    auth_method: str = "lti",
) -> Optional[str]:
    """Mint a short-lived signed token for backend-api authorization."""
    if not settings.BACKEND_API_JWT_SECRET:
        logger.warning("BACKEND_API_JWT_SECRET/VHVL_SIGNING_KEY is not configured; API token not issued")
        return None

    now = int(time.time())
    roles = _normalized_backend_roles(user_data, auth_method)
    if auth_method == "staff":
        user_data["roles"] = roles

    claims = {
        "sub": user_data.get("sub") or user_data.get("user_id") or user_data.get("email"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "roles": roles,
        "auth_method": auth_method,
        "iat": now,
        "exp": now + min(settings.SESSION_TTL, 8 * 60 * 60),
    }
    if auth_method == "staff" and settings.staff_course_ids_list:
        claims["course_ids"] = settings.staff_course_ids_list
    if course_data:
        claims["course"] = course_data
        claims["course_id"] = course_data.get("course_id") or course_data.get("id")
    if settings.BACKEND_API_JWT_AUDIENCE:
        claims["aud"] = settings.BACKEND_API_JWT_AUDIENCE

    return jwt.encode(claims, settings.BACKEND_API_JWT_SECRET, algorithm="HS256")


def _list_claim(claims: dict, key: str) -> list[str]:
    value = claims.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def ensure_staff_account_allowed(user: dict, claims: dict) -> None:
    email = (user.get("email") or claims.get("email") or claims.get("upn") or "").lower()

    allowed_emails = settings.staff_allowed_emails_list
    if allowed_emails and email not in allowed_emails:
        raise HTTPException(status_code=403, detail="Staff account is not in the allowed email list")

    allowed_domain = settings.STAFF_ALLOWED_EMAIL_DOMAIN.strip().lower().lstrip("@")
    if allowed_domain and not email.endswith(f"@{allowed_domain}"):
        raise HTTPException(status_code=403, detail="Staff account is not in the allowed email domain")

    allowed_roles = settings.staff_allowed_roles_list
    token_roles = _list_claim(claims, "roles")
    if allowed_roles and not any(role in allowed_roles for role in token_roles):
        raise HTTPException(status_code=403, detail="Staff account does not have an allowed role")

    allowed_groups = settings.staff_allowed_group_ids_list
    token_groups = _list_claim(claims, "groups")
    if allowed_groups and not any(group in allowed_groups for group in token_groups):
        raise HTTPException(status_code=403, detail="Staff account is not in an allowed group")


async def sync_student_to_backend(user_data: dict) -> bool:
    """
    Sync student to alignbackendapis database.
    Creates student if they don't exist, updates login info if they do.
    """
    try:
        email = user_data.get('email')
        name = user_data.get('name', 'Unknown User')
        
        if not email:
            logger.warning("No email in user_data, skipping backend sync")
            return False
        
        backend_url = settings.BACKEND_API_URL
        
        # Check if student exists
        service_headers = {}
        if settings.BACKEND_API_SERVICE_TOKEN:
            service_headers["X-Service-Token"] = settings.BACKEND_API_SERVICE_TOKEN

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Try to get student
                response = await client.get(
                    f"{backend_url}/students/{email}",
                    headers=service_headers,
                )
                
                if response.status_code == 200:
                    # Student exists, update login info
                    logger.info(f"Student {email} exists, updating login info")
                    login_response = await client.put(
                        f"{backend_url}/students/{email}/login",
                        headers=service_headers,
                    )
                    if login_response.status_code == 200:
                        logger.info(f"Updated login info for {email}")
                    return True
                    
            except httpx.HTTPStatusError:
                pass  # Student doesn't exist, create them
            
            # Student doesn't exist, create them
            logger.info(f"Creating new student: {email}")
            
            # Get profile picture or use a default placeholder
            profile_pic = user_data.get('picture')
            if not profile_pic or profile_pic.strip() == '':
                # Use a default gravatar or placeholder
                profile_pic = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=200"
            
            student_data = {
                "name": name,
                "email": email,
                "date_of_birth": None,
                "profile_picture": profile_pic,
                "location": None
            }
            
            create_response = await client.post(
                f"{backend_url}/students/",
                json=student_data,
                headers=service_headers,
            )
            
            if create_response.status_code in [200, 201]:
                logger.info(f"Successfully created student {email}")
                return True
            else:
                logger.error(f"Failed to create student: {create_response.status_code} - {create_response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error syncing student to backend: {str(e)}", exc_info=True)
        return False


@app.get("/health")
@app.get("/lti/health")
async def health_check():
    """Process liveness endpoint for internal and same-origin proxy checks."""
    return {"status": "healthy", "service": "lti-backend"}


@app.get("/health/ready")
@app.get("/lti/health/ready")
async def readiness_check():
    """Configuration and Redis readiness for internal and public proxy checks."""
    failed_checks = list(settings.readiness_configuration_errors)
    try:
        session_manager.redis_client.ping()
    except Exception:
        failed_checks.append("redis")

    if failed_checks:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "failed_checks": sorted(set(failed_checks))},
        )
    return {"status": "ready", "service": "lti-backend"}


@app.post("/lti/login")
async def lti_login(
    request: Request,
    iss: str = Form(...),
    login_hint: str = Form(...),
    target_link_uri: str = Form(...),
    lti_message_hint: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None)
):
    """
    Handle LTI 1.3 login initiation from Brightspace
    
    This endpoint receives the initial LTI login request, generates state/nonce,
    and redirects to Brightspace authorization endpoint.
    """
    try:
        logger.info(f"LTI Login Initiation received from issuer: {iss}")
        logger.debug("Received LTI login parameters")
        
        # Validate required parameters
        if not iss or not login_hint or not target_link_uri:
            logger.error("Missing required parameters in LTI login")
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Handle the login initiation
        auth_url = lti_handler.handle_login(
            iss=iss,
            login_hint=login_hint,
            target_link_uri=target_link_uri,
            lti_message_hint=lti_message_hint,
            client_id=client_id
        )
        
        logger.info(f"Redirecting to authorization URL")
        return RedirectResponse(url=auth_url, status_code=302)
        
    except HTTPException:
        raise
    except LTIValidationError as e:
        logger.warning("LTI login validation failed: %s", e.reason)
        raise HTTPException(status_code=400, detail="Invalid LTI login request")
    except Exception as e:
        logger.error(f"Error in LTI login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login initiation failed")


@app.post("/lti/launch")
async def lti_launch(
    request: Request,
    id_token: str = Form(...),
    state: str = Form(...)
):
    """
    Handle LTI 1.3 launch request from Brightspace
    
    This endpoint receives the JWT ID token, validates it, extracts user/course info,
    creates a session, and redirects with a short-lived one-time login code.
    """
    try:
        logger.info("LTI launch received")
        
        # Validate required parameters
        if not id_token or not state:
            logger.error("Missing required parameters in LTI launch")
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Handle the launch and validate token
        user_data, course_data = lti_handler.handle_launch(id_token, state)
        
        # Sync student with backend API
        await sync_student_to_backend(user_data)
        
        # Create session
        session_token = session_manager.create_session(user_data, course_data)
        
        login_code = session_manager.create_login_code(session_token)
        logger.info("LTI session created")

        # Only a short-lived, one-time code is placed in browser history.
        redirect_url = f"{settings.FRONTEND_URL}/app?login_code={login_code}"
        logger.debug("Redirecting completed LTI launch to the frontend")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except LTIValidationError as e:
        logger.warning("LTI launch validation failed: %s", e.reason)
        query = urlencode({"error": "invalid_token", "reason": e.reason})
        error_url = f"{settings.FRONTEND_URL}/lti-required?{query}"
        return RedirectResponse(url=error_url, status_code=302)
    except Exception as e:
        logger.error(f"Error in LTI launch: {str(e)}", exc_info=True)
        error_url = f"{settings.FRONTEND_URL}/lti-required?error=launch_failed"
        return RedirectResponse(url=error_url, status_code=302)


@app.get("/lti/staff/login")
async def staff_login(prompt: Optional[str] = None):
    """
    Start staff/admin OIDC login.
    Uses server-generated state/PKCE and redirects user to IdP authorize endpoint.
    """
    try:
        auth_url = await staff_oidc_handler.build_authorization_url(prompt=prompt)
        return RedirectResponse(url=auth_url, status_code=302)
    except ValueError as e:
        logger.error(f"Staff login configuration error: {str(e)}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/staff?error=staff_not_configured", status_code=302)
    except Exception as e:
        logger.error(f"Error starting staff login: {str(e)}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/staff?error=staff_login_failed", status_code=302)


@app.post("/lti/staff/exchange", response_model=StaffCodeExchangeResponse)
async def staff_exchange(payload: StaffCodeExchangeRequest):
    """
    Exchange authorization code server-side (BFF) to avoid browser CORS to IdP token endpoint.
    """
    try:
        user, claims = await staff_oidc_handler.exchange_code(code=payload.code, state=payload.state)
        ensure_staff_account_allowed(user, claims)
        api_token = create_backend_api_token(user, auth_method="staff")
        return StaffCodeExchangeResponse(user=user, claims=claims, api_token=api_token)
    except HTTPException:
        raise
    except ValueError:
        logger.warning("Staff code exchange was rejected")
        raise HTTPException(status_code=400, detail="Staff sign-in could not be completed")
    except Exception as e:
        logger.error(f"Unexpected staff code exchange error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Staff sign-in failed")


@app.get("/lti/staff/logout")
async def staff_logout():
    """
    Start staff/admin logout at identity provider.
    Frontend should clear local state first, then redirect here.
    """
    try:
        logout_url = await staff_oidc_handler.build_logout_url()
        return RedirectResponse(url=logout_url, status_code=302)
    except Exception as e:
        logger.error(f"Error starting staff logout: {str(e)}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/staff", status_code=302)


@app.get("/lti/session/validate")
async def validate_session(authorization: Optional[str] = Header(None)) -> SessionResponse:
    """
    Validate session token and return user/course information
    
    Used by frontend to check if session is still valid and get user context.
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        session_token = authorization.split(" ", 1)[1]
        
        # Validate session
        session_data = session_manager.get_session(session_token)
        
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        logger.debug(f"Session validated for user: {session_data['user'].get('email', 'unknown')}")
        
        return SessionResponse(
            user=session_data['user'],
            course=session_data['course'],
            api_token=create_backend_api_token(
                session_data["user"],
                session_data["course"],
                auth_method="lti",
            ),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Session validation failed")


@app.post("/lti/session/exchange", response_model=LoginCodeExchangeResponse)
async def exchange_login_code(payload: LoginCodeExchangeRequest) -> LoginCodeExchangeResponse:
    """Consume a one-time launch code without exposing a session token in the URL."""
    session_token = session_manager.consume_login_code(payload.login_code)
    if not session_token:
        raise HTTPException(status_code=401, detail="Invalid or expired login code")

    session_data = session_manager.get_session(session_token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return LoginCodeExchangeResponse(
        session_token=session_token,
        user=session_data["user"],
        course=session_data["course"],
        api_token=create_backend_api_token(
            session_data["user"],
            session_data["course"],
            auth_method="lti",
        ),
    )


@app.post("/lti/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout endpoint - destroys the session
    """
    try:
        if not authorization:
            return JSONResponse(
                content={"message": "No session to logout"},
                status_code=200
            )
        
        # Extract token
        if authorization.startswith("Bearer "):
            session_token = authorization.split(" ", 1)[1]
            
            # Delete session
            session_manager.delete_session(session_token)
            logger.info("Session destroyed")
        
        return JSONResponse(
            content={"message": "Logged out successfully"},
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}", exc_info=True)
        # Return success anyway since logout should be idempotent
        return JSONResponse(
            content={"message": "Logged out"},
            status_code=200
        )


@app.get("/lti/session/refresh")
async def refresh_session(authorization: Optional[str] = Header(None)):
    """
    Refresh session TTL
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization")
        
        session_token = authorization.split(" ", 1)[1]
        
        # Refresh session
        refreshed = session_manager.refresh_session(session_token)
        
        if not refreshed:
            raise HTTPException(status_code=401, detail="Session not found")
        
        return JSONResponse(
            content={"message": "Session refreshed"},
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Session refresh failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
