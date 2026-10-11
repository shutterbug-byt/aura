
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


HOST = "127.0.0.1"
PORT = 8000

REQUIRED_FIELDS = {
    "event_type",
    "event_id",
    "timestamp",
    "transcript",
    "language",
    "confidence",
    "source",
}


class MockBackendHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/events/voice":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            event = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})
            return

        if not isinstance(event, dict):
            self.send_json(400, {"error": "Event must be a JSON object"})
            return

        missing = REQUIRED_FIELDS - event.keys()
        if missing:
            self.send_json(
                400,
                {"error": "Missing fields", "fields": sorted(missing)},
            )
            return

        if event["event_type"] != "voice_input":
            self.send_json(400, {"error": "Invalid event_type"})
            return

        if not isinstance(event["transcript"], str) or not event["transcript"].strip():
            self.send_json(400, {"error": "Transcript must not be empty"})
            return

        if not isinstance(event["source"], str) or not event["source"].strip():
            self.send_json(400, {"error": "Source must not be empty"})
            return

        print("\nReceived AURA voice event:")
        print(json.dumps(event, indent=2, ensure_ascii=False))

        self.send_json(
            200,
            {
                "status": "accepted",
                "event_id": event["event_id"],
            },
        )

    def send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print(f"[MockBackend] {args[0]}")


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), MockBackendHandler)
    print(f"Mock backend listening at http://{HOST}:{PORT}")
    print("Endpoint: POST /events/voice")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock backend stopped.")
    finally:
        server.server_close()
