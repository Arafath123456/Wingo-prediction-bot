from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from database.session import get_session
import psutil
import time
from loguru import logger

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Check database connection
            try:
                session = get_session()
                session.execute("SELECT 1")
                db_ok = True
            except Exception:
                db_ok = False
            
            # Check system resources
            mem_ok = psutil.virtual_memory().percent < 90
            cpu_ok = psutil.cpu_percent() < 90
            
            if db_ok and mem_ok and cpu_ok:
                self.send_response(200)
                self.end_headers()
                self.write_response({
                    "status": "ok",
                    "database": "connected",
                    "memory": f"{psutil.virtual_memory().percent}%",
                    "cpu": f"{psutil.cpu_percent()}%"
                })
            else:
                self.send_response(503)
                self.end_headers()
                self.write_response({
                    "status": "degraded",
                    "database": "connected" if db_ok else "disconnected",
                    "memory": f"{psutil.virtual_memory().percent}%",
                    "cpu": f"{psutil.cpu_percent()}%"
                })
        elif self.path == '/metrics':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'# Health metrics are served on /metrics endpoint by Prometheus client')
        else:
            self.send_response(404)
            self.end_headers()
    
    def write_response(self, data: dict):
        import json
        self.wfile.write(json.dumps(data).encode('utf-8'))

def start_health_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

def init_health_monitoring():
    Thread(target=start_health_server, daemon=True).start()