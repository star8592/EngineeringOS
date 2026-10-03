import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, "src/engineeringos")

from laya_provider import LayaLocalProvider
from system_one_contract import TypedQuestion


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        assert self.path == "/v1/systemone"
        n = int(self.headers["content-length"])
        request = json.loads(self.rfile.read(n))
        qid, question = next(iter(request["questions"].items()))
        assert question["type"] == "choice"
        assert "criteria" in question
        body = json.dumps({
            "model": "laya-rl-agent",
            "answers": {
                qid: {
                    "type": "choice",
                    "choice": "REASONING_REVIEW",
                    "probabilities": {
                        "DETERMINISTIC_CANDIDATE": 0.04,
                        "REASONING_REVIEW": 0.91,
                        "FORMAL_OR_HIGH_ASSURANCE": 0.03,
                        "HUMAN_REVIEW": 0.02
                    },
                    "confidence": 0.71,
                    "answer_confidence": 0.91
                }
            },
            "usage": {"input_tokens": 12, "output_tokens": 0},
            "routing": {"model": "typed-decisions"}
        }).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("X-Inference-Time-Ms", "7.5")
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    provider = LayaLocalProvider(base_url=f"http://127.0.0.1:{server.server_port}")
    assert provider.health()["available"] is True
    q = TypedQuestion(
        question_id="lane",
        kind="choice",
        instructions="Choose lane",
        options=(
            "DETERMINISTIC_CANDIDATE",
            "REASONING_REVIEW",
            "FORMAL_OR_HIGH_ASSURANCE",
            "HUMAN_REVIEW"
        )
    )
    result = provider.decide(state={"kind": "semantic-change"}, question=q)
    assert result.decision.recommended_route == "REASONING_REVIEW"
    assert result.answer_confidence == 0.91
    assert result.latency_ms == 7.5
    assert result.model == "typed-decisions"
finally:
    server.shutdown()
    thread.join(timeout=2)

unavailable = LayaLocalProvider(base_url="http://127.0.0.1:1", timeout_seconds=0.1)
assert unavailable.health()["available"] is False

print("6 Laya provider invariants passed")
