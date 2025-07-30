from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from loguru import logger
import time

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics':
            self.send_response(200)
            self.end_headers()
            # TODO: Add actual metrics collection
            self.wfile.write(b'# HELP app_health Application health\n')
            self.wfile.write(b'# TYPE app_health gauge\n')
            self.wfile.write(b'app_health 1\n')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    server = HTTPServer(('0.0.0.0', 8000), HealthHandler)
    logger.info("Health check server running on port 8000")
    server.serve_forever()

def init_monitoring():
    # Start health check server in background
    Thread(target=start_health_server, daemon=True).start()
    
    # Initialize Sentry
    import sentry_sdk
    if dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
        logger.info("Sentry monitoring initialized")