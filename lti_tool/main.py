from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging
from authentication import handle_login
from launch import handle_launch

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LTIRequestHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP request handler for LTI endpoints.
    """

    def do_POST(self):
        """
        Handle POST requests.
        """
        try:
            logger.debug(f"Received POST request at path: {self.path}")
            # Check Content-Type
            content_type = self.headers.get('Content-Type', '')
            if content_type != 'application/x-www-form-urlencoded':
                logger.error(f"Unsupported Content-Type: {content_type}")
                self.send_error(400, "Unsupported Content-Type")
                return

            # Read and parse form data
            content_length = int(self.headers.get('Content-Length', 0))
            logger.debug(f"Content-Length: {content_length}")
            post_data = self.rfile.read(content_length)
            logger.debug(f"Raw POST data: {post_data}")
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            logger.debug(f"Parsed form data: {form_data}")

            if self.path == '/lti/login':
                handle_login(self, form_data)
            elif self.path == '/lti/launch':
                handle_launch(self, form_data)
            else:
                logger.warning(f"Unhandled POST path: {self.path}")
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}", exc_info=True)
            self.send_error(500, "Internal Server Error")

    def do_GET(self):
        """
        Disallow GET requests.
        """
        logger.debug(f"Received GET request at path: {self.path}")
        self.send_error(405, "Method Not Allowed")

    def log_message(self, format, *args):
        """
        Override to use the logging module.
        """
        logger.info("%s - - [%s] %s" %
                    (self.client_address[0],
                     self.log_date_time_string(),
                     format % args))

def run():
    """
    Run the HTTP server.
    """
    server_address = ('', 8000)  # Listen on all interfaces on port 8000
    httpd = HTTPServer(server_address, LTIRequestHandler)
    logger.info('Starting LTI tool server on port 8000...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Stopping LTI tool server...')
        httpd.server_close()

if __name__ == '__main__':
    run()