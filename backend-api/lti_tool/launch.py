import logging
from utils import validate_token
from templates import render_template
from session_manager import get_state_data

logger = logging.getLogger(__name__)

# Role mappings
ROLE_MAPPINGS = {
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor': 'Instructor',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner': 'Learner',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Member': 'Member',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor': 'Mentor',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator': 'Administrator',
    'http://purl.imsglobal.org/vocab/lis/v2/membership#TeachingAssistant': 'Teaching Assistant',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor': 'Institution Instructor',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner': 'Institution Learner',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member': 'Institution Member',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor': 'Institution Mentor',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff': 'Institution Staff',
    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator': 'Institution Administrator',
    # Add more mappings as needed
}

def handle_launch(request_handler, form_data):
    """
    Handle the LTI launch request after authentication.
    """
    try:
        logger.debug("Handling LTI launch request")
        # Extract required parameters
        id_token = form_data.get('id_token', [None])[0]
        state = form_data.get('state', [None])[0]

        logger.debug(f"id_token: {id_token}")
        logger.debug(f"state: {state}")

        # Validate required parameters
        if not id_token or not state:
            logger.error("Missing required parameters in launch request")
            request_handler.send_error(400, "Missing required parameters")
            return

        # Retrieve state data
        state_data = get_state_data(state)
        if not state_data:
            logger.error("Invalid or expired state parameter")
            request_handler.send_error(400, "Invalid state")
            return

        # Extract nonce from state data
        nonce = state_data['nonce']
        logger.debug(f"Retrieved nonce from state data: {nonce}")

        # Validate token
        decoded_token = validate_token(id_token, nonce)

        if not decoded_token:
            logger.error("Token validation failed")
            request_handler.send_error(400, "Invalid token")
            return

        # Extract user info
        user_info = extract_user_info(decoded_token)
        logger.debug(f"Extracted user info: {user_info}")

        # Render response
        html_content = render_template('launch.html', user_info)
        logger.debug("Rendering launch.html template")

        request_handler.send_response(200)
        request_handler.send_header('Content-Type', 'text/html; charset=utf-8')
        content_length = len(html_content.encode('utf-8'))
        request_handler.send_header('Content-Length', str(content_length))
        request_handler.end_headers()
        request_handler.wfile.write(html_content.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error in handle_launch: {e}", exc_info=True)
        request_handler.send_error(500, "Internal Server Error")

def extract_user_info(decoded_token):
    """
    Extract user and course information from the decoded token.
    """
    context_claim = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/context', {})
    lis_claim = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/lis', {})
    roles_uris = decoded_token.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
    
    # Map role URIs to friendly names
    friendly_roles = []
    for role_uri in roles_uris:
        role_name = ROLE_MAPPINGS.get(role_uri)
        if role_name:
            friendly_roles.append(role_name)
        else:
            # Extract the last part after '#' or '/'
            if '#' in role_uri:
                role_name = role_uri.split('#')[-1]
            elif '/' in role_uri:
                role_name = role_uri.rsplit('/', 1)[-1]
            else:
                role_name = role_uri  # Use the full URI if separator not found
            friendly_roles.append(role_name)

    # Remove duplicates and sort the roles
    friendly_roles = sorted(set(friendly_roles))

    # Process course_section_sourcedid as before
    full_course_section = lis_claim.get('course_section_sourcedid', 'N/A')
    if full_course_section != 'N/A' and ':' in full_course_section:
        course_section = full_course_section.split(':', 1)[1].strip()
    else:
        course_section = full_course_section

    user_info = {
        'user_id': lis_claim.get('person_sourcedid', decoded_token.get('sub', 'N/A')),
        'name': decoded_token.get('name', 'N/A'),
        'given_name': decoded_token.get('given_name', 'N/A'),
        'family_name': decoded_token.get('family_name', 'N/A'),
        'email': decoded_token.get('email', 'N/A'),
        'roles': friendly_roles,  # Updated roles
        'course_id': context_claim.get('id', 'N/A'),
        'course_code': context_claim.get('label', 'N/A'),
        'course_title': context_claim.get('title', 'N/A'),
        'course_section': course_section,
    }
    return user_info