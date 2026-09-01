# config.py
import os

CLIENT_ID = os.getenv('CLIENT_ID', 'REPLACE_WITH_BRIGHTSPACE_CLIENT_ID')
DEPLOYMENT_ID = os.getenv('DEPLOYMENT_ID', 'REPLACE_WITH_BRIGHTSPACE_DEPLOYMENT_ID')
AUTHORIZATION_ENDPOINT = os.getenv('AUTHORIZATION_ENDPOINT', 'https://example.brightspace.com/d2l/lti/authenticate')
KEY_SET_URL = os.getenv('KEY_SET_URL', 'https://example.brightspace.com/d2l/.well-known/jwks')
TOOL_URL = os.getenv('TOOL_URL', 'http://localhost:8000')
ISSUER = os.getenv('ISSUER', 'https://example.brightspace.com')


