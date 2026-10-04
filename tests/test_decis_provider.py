import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, "src/engineeringos")

from decis_provider import DecisProvider
from system_one_contract import TypedQuestion


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path == "/healthz":
            body = json.dumps({"status": "ok", "version": "0.4.0"}).encode()
            self.send_response(200)
        elif self.path == "/readyz":
            body = json.dumps({"status": "ready", "engine": "kev-0.8b"}).encode()
            self.send_response(200)
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        assert self.path == "/v1/systemone"
        assert self.headers.get("authorization") == "Bearer local"
        n = int(self.headers["content-length"])
        request = json.loads(self.rfile.read(n))
        qid, question = next(iter(request["questions"].items()))
        assert request["model"] == "jev-latest"
        assert question["criteria"]["FORMAL_OR_HIGH_ASSURANCE"] == "critical"
        body = json.dumps({
            "model": "decis/kev-0.8b@0.4.0",
            "answers": {
                qid: {
                    "type": "choice",
                    "choice": "FORMAL_OR_HIGH_ASSURANCE",
                    "probabilities": {
                        "DETERMINISTIC_CANDIDATE": 0.1,
                        "REASONING_REVIEW": 0.2,
                        "FORMAL_OR_HIGH_ASSURANCE": 0.7,
                    },
                    "confidence": 0.45,
                }
            },
            "usage": {"input_tokens": 42, "output_tokens": 1},
            "decis": {
                "engine": "kev-0.8b",
                "latency_ms": 42.5,
            },
        }).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    provider = DecisProvider(
        base_url=f"http://127.0.0.1:{server.server_port}",
        api_key="local",
        timeout_seconds=2,
    )
    health = provider.health()
    assert health["available"] is True
    assert health["ready_body"]["engine"] == "kev-0.8b"

    q = TypedQuestion(
        question_id="engineering_lane",
        kind="choice",
        instructions="Choose lane",
        options=(
            "DETERMINISTIC_CANDIDATE",
            "REASONING_REVIEW",
            "FORMAL_OR_HIGH_ASSURANCE",
        ),
        criteria=(
            ("DETERMINISTIC_CANDIDATE", "mechanical"),
            ("REASONING_REVIEW", "reasoning"),
            ("FORMAL_OR_HIGH_ASSURANCE", "critical"),
        ),
    )
    result = provider.decide(state={"kind": "AUTH_POLICY"}, question=q)
    assert result.decision.recommended_route == "FORMAL_OR_HIGH_ASSURANCE"
    assert result.answer_confidence == 0.7
    assert result.latency_ms == 42.5
    assert result.model == "decis/kev-0.8b@0.4.0"
finally:
    server.shutdown()
    thread.join(timeout=2)

print("8 Decis Jev-compatible provider invariants passed")
