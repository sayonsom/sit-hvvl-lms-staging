import secrets
import urllib.parse
import config
import logging
from session_manager import store_state

logger = logging.getLogger(__name__)

def handle_login(request_handler, form_data):
    """
    Handle the LTI login initiation request.
    """
    try:
        logger.debug("Handling LTI login initiation request")
        # Extract required parameters
        iss = form_data.get('iss', [None])[0]
        login_hint = form_data.get('login_hint', [None])[0]
        target_link_uri = form_data.get('target_link_uri', [None])[0]
        lti_message_hint = form_data.get('lti_message_hint', [None])[0]

        logger.debug(f"iss: {iss}")
        logger.debug(f"login_hint: {login_hint}")
        logger.debug(f"target_link_uri: {target_link_uri}")
        logger.debug(f"lti_message_hint: {lti_message_hint}")

        # Validate required parameters
        if not iss or not login_hint or not target_link_uri:
            logger.error("Missing or empty required parameters in login request")
            request_handler.send_error(400, "Missing required parameters")
            return

        # Generate state and nonce
        state = secrets.token_urlsafe(16)
        nonce = secrets.token_urlsafe(16)
        logger.debug(f"Generated state: {state}")
        logger.debug(f"Generated nonce: {nonce}")

        # Store state data
        state_data = {
            'nonce': nonce,
            # Add any other data you need to persist
        }
        store_state(state, state_data)
        logger.debug(f"Stored state data for state: {state}")

        # Prepare redirect parameters
        auth_params = {
            'response_type': 'id_token',
            'client_id': config.CLIENT_ID,
            'redirect_uri': config.TOOL_URL + '/lti/launch',
            'scope': 'openid',
            'login_hint': login_hint,
            'nonce': nonce,
            'prompt': 'none',
            'response_mode': 'form_post',
            'state': state,
            'iss': iss  # Use the incoming 'iss' value
        }

        if lti_message_hint:
            auth_params['lti_message_hint'] = lti_message_hint

        # Build the authorization URL
        auth_url = config.AUTHORIZATION_ENDPOINT + '?' + urllib.parse.urlencode(auth_params, safe='/:')
        logger.debug(f"Redirecting to authorization URL: {auth_url}")

        # Redirect to the authorization URL
        request_handler.send_response(302)
        request_handler.send_header('Location', auth_url)
        request_handler.send_header('Content-Length', '0')
        request_handler.end_headers()
    except Exception as e:
        logger.error(f"Error in handle_login: {e}", exc_info=True)
        request_handler.send_error(500, "Internal Server Error")