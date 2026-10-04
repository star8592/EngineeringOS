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
        answers = {}
        for qid, question in request["questions"].items():
            assert question["type"] == "choice"
            assert "criteria" in question
            if qid == "secondary_route":
                choice = "STATIC_ANALYSIS"
                probs = {
                    "STATIC_ANALYSIS": 0.88,
                    "TEST_EXECUTION": 0.12,
                }
            else:
                choice = "REASONING_REVIEW"
                probs = {
                    "DETERMINISTIC_CANDIDATE": 0.04,
                    "REASONING_REVIEW": 0.91,
                    "FORMAL_OR_HIGH_ASSURANCE": 0.05,
                }
            answers[qid] = {
                "type": "choice",
                "choice": choice,
                "probabilities": probs,
                "confidence": 0.71,
                "answer_confidence": probs[choice],
            }

        body = json.dumps({
            "model": "laya-rl-agent",
            "answers": answers,
            "usage": {"input_tokens": 12, "output_tokens": 0},
            "routing": {"model": "typed-decisions"},
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
    provider = LayaLocalProvider(
        base_url=f"http://127.0.0.1:{server.server_port}"
    )
    assert provider.health()["available"] is True

    lane = TypedQuestion(
        question_id="engineering_lane",
        kind="choice",
        instructions="Choose lane",
        options=(
            "DETERMINISTIC_CANDIDATE",
            "REASONING_REVIEW",
            "FORMAL_OR_HIGH_ASSURANCE",
        ),
    )
    authority = TypedQuestion(
        question_id="secondary_route",
        kind="choice",
        instructions="Which secondary engineering route?",
        options=(
            "STATIC_ANALYSIS",
            "TEST_EXECUTION",
        ),
    )
    batch = provider.decide_many(
        state={"kind": "semantic-change"},
        questions=(lane, authority),
    )
    assert set(batch.answers) == {
        "engineering_lane",
        "secondary_route",
    }
    assert (
        batch.answers["engineering_lane"].choice
        == "REASONING_REVIEW"
    )
    assert (
        batch.answers["secondary_route"].choice
        == "STATIC_ANALYSIS"
    )
    assert (
        batch.answers["engineering_lane"].answer_confidence
        == 0.91
    )
    assert batch.latency_ms == 7.5
    assert batch.model == "typed-decisions"

    single = provider.decide(
        state={"kind": "semantic-change"},
        question=lane,
    )
    assert (
        single.decision.recommended_route
        == "REASONING_REVIEW"
    )
finally:
    server.shutdown()
    thread.join(timeout=2)

unavailable = LayaLocalProvider(
    base_url="http://127.0.0.1:1",
    timeout_seconds=0.1,
)
assert unavailable.health()["available"] is False

print("9 Laya provider invariants passed")
