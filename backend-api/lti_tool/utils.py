import jwt
import config
import logging
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

def validate_token(id_token, expected_nonce):
    """
    Validate the id_token and return the decoded token if valid.
    """
    try:
        logger.debug("Validating token using PyJWKClient")

        # Initialize PyJWKClient with the JWKS URL
        jwks_client = PyJWKClient(config.KEY_SET_URL)

        # Get the signing key
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        logger.debug("Obtained public key from JWKS")

        # Decode and validate the JWT
        decoded_token = jwt.decode(
            id_token,
            key=signing_key.key,
            algorithms=['RS256'],
            audience=config.CLIENT_ID,
            issuer=config.ISSUER
        )
        logger.debug(f"Decoded token: {decoded_token}")

        # Validate nonce
        if decoded_token.get('nonce') != expected_nonce:
            logger.error("Invalid nonce")
            return None

        # Validate deployment ID
        deployment_id = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/deployment_id')
        if deployment_id != config.DEPLOYMENT_ID:
            logger.error("Invalid deployment ID")
            return None

        return decoded_token

    except InvalidTokenError as e:
        logger.error(f"Token validation error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}", exc_info=True)
        return None