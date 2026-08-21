import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MockLLMServer")

class MockOpenAIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override standard log to use our logger format
        logger.info(f"{self.address_string()} - {format % args}")

    def do_POST(self):
        if self.path.startswith("/v1/chat/completions") or self.path.startswith("/chat/completions"):
            auth_header = self.headers.get("Authorization", "")
            
            # Check for simulated 401 error
            if "invalid-key" in auth_header:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_resp = {
                    "error": {
                        "message": "Incorrect API key provided.",
                        "type": "invalid_request_error",
                        "param": None,
                        "code": "invalid_api_key"
                    }
                }
                self.wfile.write(json.dumps(error_resp).encode("utf-8"))
                return

            # Check for simulated 429 error
            if "rate-limit-key" in auth_header:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_resp = {
                    "error": {
                        "message": "Rate limit exceeded for requests. Please try again later.",
                        "type": "requests",
                        "param": None,
                        "code": "rate_limit_exceeded"
                    }
                }
                self.wfile.write(json.dumps(error_resp).encode("utf-8"))
                return

            # Standard successful response
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(request_body) if request_body else {}
            except Exception:
                data = {}

            model = data.get("model", "gpt-4o-mini")

            response_payload = {
                "id": "chatcmpl-mock-998877",
                "object": "chat.completion",
                "created": 1771666600,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "A banking regulatory compliance policy defines rules and operational standards to ensure financial institutions strictly adhere to legal mandates, maintain risk controls, and safeguard customer data and assets."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 28,
                    "completion_tokens": 34,
                    "total_tokens": 62
                }
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_mock_server(host="127.0.0.1", port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, MockOpenAIHandler)
    logger.info(f"Mock OpenAI API server running on http://{host}:{port}/v1")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down.")
        httpd.server_close()

if __name__ == "__main__":
    run_mock_server()
