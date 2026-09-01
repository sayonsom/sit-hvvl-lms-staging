"""
LTI 1.3 Protocol Handler
Handles login initiation, JWT validation, and user/course data extraction
"""
import secrets
import urllib.parse
import logging
from typing import Tuple, Dict, Any, Optional
import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
    PyJWKClientError,
)

from .config import settings
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class LTIValidationError(ValueError):
    """LTI validation failure with a safe, non-sensitive reason code."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


# Role mappings from LTI URIs to friendly names
ROLE_MAPPINGS = {
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor': 'Instructor',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner': 'Learner',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Member': 'Member',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor': 'Mentor',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator': 'Administrator',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#TeachingAssistant': 'Teaching Assistant',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor': 'Institution Instructor',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner': 'Institution Learner',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student': 'Student',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member': 'Institution Member',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor': 'Institution Mentor',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff': 'Institution Staff',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator': 'Institution Administrator',
}


class LTIHandler:
    """Handles LTI 1.3 protocol operations"""
    
    def __init__(self, session_manager=None, jwks_client=None):
        self.session_manager = session_manager or SessionManager()
        self.jwks_client = jwks_client or PyJWKClient(
            settings.KEY_SET_URL,
            timeout=settings.LTI_JWKS_TIMEOUT_SECONDS,
        )
    
    def handle_login(
        self,
        iss: str,
        login_hint: str,
        target_link_uri: str,
        lti_message_hint: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> str:
        """
        Handle LTI login initiation
        
        Generates state and nonce, stores them, and returns authorization URL
        """
        logger.debug("Processing LTI login initiation")

        if settings.lti_configuration_errors:
            logger.error("LTI login rejected because configuration is incomplete")
            raise LTIValidationError("configuration_error")

        if iss != settings.ISSUER:
            logger.warning("LTI login rejected for an untrusted issuer")
            raise LTIValidationError("invalid_issuer")

        selected_client_id = (client_id or settings.CLIENT_ID).strip()
        if selected_client_id not in settings.lti_client_ids_list:
            logger.warning("LTI login rejected for an unregistered client ID")
            raise LTIValidationError("invalid_client")
        
        # Generate cryptographically secure state and nonce
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        logger.debug("Generated LTI state and nonce")
        
        # Store state data with short TTL (5 minutes)
        state_data = {
            'nonce': nonce,
            'iss': iss,
            'client_id': selected_client_id,
            'target_link_uri': target_link_uri
        }
        self.session_manager.store_state(state, state_data)
        
        # Build authorization parameters
        auth_params = {
            'response_type': 'id_token',
            'client_id': selected_client_id,
            'redirect_uri': f"{settings.TOOL_URL}/lti/launch",
            'scope': 'openid',
            'login_hint': login_hint,
            'nonce': nonce,
            'prompt': 'none',
            'response_mode': 'form_post',
            'state': state,
            'iss': iss
        }
        
        # Add optional lti_message_hint
        if lti_message_hint:
            auth_params['lti_message_hint'] = lti_message_hint
        
        # Build authorization URL
        auth_url = settings.AUTHORIZATION_ENDPOINT + '?' + urllib.parse.urlencode(
            auth_params, 
            safe='/:',
            quote_via=urllib.parse.quote
        )
        
        logger.info("Authorization URL built successfully")
        return auth_url
    
    def handle_launch(self, id_token: str, state: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Handle LTI launch
        
        Validates JWT token and extracts user/course information
        Returns: (user_data, course_data)
        """
        logger.debug("Processing LTI launch")
        
        # Retrieve and validate state
        state_data = self.session_manager.get_state(state)
        if not state_data:
            logger.error("Invalid or expired state parameter")
            raise LTIValidationError("invalid_state")
        
        expected_nonce = state_data.get('nonce')
        expected_issuer = state_data.get('iss')
        expected_client_id = state_data.get('client_id')
        if not all(isinstance(value, str) and value for value in (expected_nonce, expected_issuer, expected_client_id)):
            logger.error("LTI state is missing required validation context")
            raise LTIValidationError("invalid_state")
        
        # Validate JWT token
        decoded_token = self._validate_token(
            id_token,
            expected_nonce=expected_nonce,
            expected_issuer=expected_issuer,
            expected_client_id=expected_client_id,
        )
        
        # Extract user and course information
        user_data = self._extract_user_info(decoded_token)
        course_data = self._extract_course_info(decoded_token)
        
        logger.info("Successfully extracted LTI user and course data")
        
        return user_data, course_data
    
    def _validate_token(
        self,
        id_token: str,
        expected_nonce: str,
        expected_issuer: str,
        expected_client_id: str,
    ) -> Dict[str, Any]:
        """
        Validate JWT ID token
        
        Checks signature, issuer, audience, nonce, and deployment_id
        """
        try:
            logger.debug("Validating JWT token")
            
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(id_token)
            logger.debug("Obtained signing key from JWKS")
            
            # Decode and validate JWT
            decoded_token = jwt.decode(
                id_token,
                key=signing_key.key,
                algorithms=['RS256'],
                audience=expected_client_id,
                issuer=expected_issuer,
                leeway=settings.LTI_CLOCK_SKEW_SECONDS,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True,
                    'require': ['exp', 'iat', 'aud', 'iss', 'sub']
                }
            )
            
            logger.debug("LTI token decoded successfully")
            
            # Validate nonce
            token_nonce = decoded_token.get('nonce')
            if not isinstance(token_nonce, str) or not secrets.compare_digest(token_nonce, expected_nonce):
                logger.warning("LTI token nonce validation failed")
                raise LTIValidationError("invalid_nonce")
            
            # Validate deployment ID
            deployment_id = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/deployment_id')
            if deployment_id not in settings.lti_deployment_ids_list:
                logger.warning("LTI token deployment validation failed")
                raise LTIValidationError("invalid_deployment")
            
            # Validate message type (should be LtiResourceLinkRequest)
            message_type = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/message_type')
            if message_type != 'LtiResourceLinkRequest':
                logger.warning("LTI token message type validation failed")
                raise LTIValidationError("invalid_message_type")
            
            logger.info("Token validation successful")
            return decoded_token
            
        except LTIValidationError:
            raise
        except ExpiredSignatureError:
            logger.warning("LTI token has expired")
            raise LTIValidationError("expired_token")
        except InvalidAudienceError:
            logger.warning("LTI token audience validation failed")
            raise LTIValidationError("invalid_audience")
        except InvalidIssuerError:
            logger.warning("LTI token issuer validation failed")
            raise LTIValidationError("invalid_issuer")
        except InvalidSignatureError:
            logger.warning("LTI token signature validation failed")
            raise LTIValidationError("invalid_signature")
        except PyJWKClientError:
            logger.error("Unable to obtain the LTI signing key from JWKS")
            raise LTIValidationError("jwks_unavailable")
        except InvalidTokenError:
            logger.warning("LTI token claims validation failed")
            raise LTIValidationError("invalid_claims")
        except Exception as e:
            logger.error("Unexpected LTI token validation error", exc_info=True)
            raise LTIValidationError("token_validation_failed") from e
    
    def _extract_user_info(self, decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from decoded JWT token"""
        
        # Get LIS claim
        lis_claim = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/lis', {})
        
        # Get roles and map to friendly names
        roles_uris = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        friendly_roles = []
        
        for role_uri in roles_uris:
            role_name = ROLE_MAPPINGS.get(role_uri)
            if role_name:
                friendly_roles.append(role_name)
            else:
                # Extract role name from URI
                if '#' in role_uri:
                    role_name = role_uri.split('#')[-1]
                elif '/' in role_uri:
                    role_name = role_uri.rsplit('/', 1)[-1]
                else:
                    role_name = role_uri
                friendly_roles.append(role_name)
        
        # Remove duplicates and sort
        friendly_roles = sorted(set(friendly_roles))
        
        user_data = {
            'user_id': lis_claim.get('person_sourcedid', decoded_token.get('sub', 'unknown')),
            'name': decoded_token.get('name', 'Unknown User'),
            'given_name': decoded_token.get('given_name', ''),
            'family_name': decoded_token.get('family_name', ''),
            'email': decoded_token.get('email', ''),
            'picture': decoded_token.get('picture', ''),
            'roles': friendly_roles,
            'sub': decoded_token.get('sub', 'unknown')
        }
        
        logger.debug("Extracted LTI user information")
        return user_data
    
    def _extract_course_info(self, decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """Extract course information from decoded JWT token"""
        
        # Get context claim (course information)
        context_claim = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/context', {})
        
        # Get LIS claim for additional course details
        lis_claim = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/lis', {})
        
        # Process course section
        full_course_section = lis_claim.get('course_section_sourcedid', 'N/A')
        if full_course_section != 'N/A' and ':' in full_course_section:
            course_section = full_course_section.split(':', 1)[1].strip()
        else:
            course_section = full_course_section
        
        course_data = {
            'course_id': context_claim.get('id', 'unknown'),
            'course_code': context_claim.get('label', ''),
            'course_title': context_claim.get('title', 'Unknown Course'),
            'course_section': course_section,
            'course_offering_sourcedid': lis_claim.get('course_offering_sourcedid', ''),
            'context_type': context_claim.get('type', []),
        }
        
        logger.debug("Extracted LTI course information")
        return course_data
