from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from system_one_contract import AdvisoryDecision, ROUTES, TypedQuestion
from system_one_provider import ProviderResult, SystemOneProviderError


class LayaLocalProvider:
    name = "laya-local"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.environ.get("ENGINEERINGOS_LAYA_BASE_URL")
            or "http://127.0.0.1:8017"
        ).rstrip("/")
        self.model = model or os.environ.get("ENGINEERINGOS_LAYA_MODEL") or "typed-decisions"
        self.api_key = api_key or os.environ.get("ENGINEERINGOS_LAYA_API_KEY")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {"content-type": "application/json", "accept": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        return headers

    def health(self) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/health",
            headers=self._headers(),
            method="GET",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw) if raw.strip() else {}
                return {
                    "provider": self.name,
                    "available": 200 <= response.status < 300,
                    "status_code": response.status,
                    "latency_ms": round((time.monotonic() - started) * 1000, 3),
                    "body": body,
                }
        except Exception as exc:
            return {
                "provider": self.name,
                "available": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "latency_ms": round((time.monotonic() - started) * 1000, 3),
            }

    def decide(self, *, state: Any, question: TypedQuestion) -> ProviderResult:
        question.validate()
        if question.kind != "choice":
            raise SystemOneProviderError("LAYA_ROUTE_PROVIDER_REQUIRES_CHOICE")
        if not question.options:
            raise SystemOneProviderError("CHOICE_OPTIONS_REQUIRED")

        payload = {
            "state": state,
            "model": self.model,
            "questions": {
                question.question_id: {
                    "type": "choice",
                    "instructions": question.instructions,
                    "criteria": {
                        option: option.replace("_", " ").lower()
                        for option in question.options
                    },
                }
            },
        }
        request = urllib.request.Request(
            f"{self.base_url}/v1/systemone",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
                inference_header = response.headers.get("X-Inference-Time-Ms")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemOneProviderError(
                f"LAYA_HTTP_{exc.code}:{detail[:500]}"
            ) from exc
        except Exception as exc:
            raise SystemOneProviderError(
                f"LAYA_UNAVAILABLE:{type(exc).__name__}:{exc}"
            ) from exc

        answer = (body.get("answers") or {}).get(question.question_id)
        if not isinstance(answer, dict):
            raise SystemOneProviderError("LAYA_ANSWER_MISSING")
        choice = answer.get("choice")
        if choice not in ROUTES or choice not in question.options:
            raise SystemOneProviderError("LAYA_ROUTE_OUT_OF_CONTRACT")
        probabilities = {
            str(key): float(value)
            for key, value in (answer.get("probabilities") or {}).items()
        }
        answer_confidence = answer.get("answer_confidence")
        if answer_confidence is None:
            answer_confidence = probabilities.get(choice)
        if answer_confidence is None:
            raise SystemOneProviderError("LAYA_ANSWER_CONFIDENCE_MISSING")
        answer_confidence = float(answer_confidence)
        if not 0.0 <= answer_confidence <= 1.0:
            raise SystemOneProviderError("LAYA_ANSWER_CONFIDENCE_INVALID")

        latency_ms: float | None
        if inference_header is not None:
            try:
                latency_ms = float(inference_header)
            except ValueError:
                latency_ms = None
        else:
            latency_ms = round((time.monotonic() - started) * 1000, 3)

        decision = AdvisoryDecision(
            source=self.name,
            question_id=question.question_id,
            recommended_route=choice,
            confidence=answer_confidence,
            raw_answer=answer,
        )
        decision.validate()
        return ProviderResult(
            decision=decision,
            model=str(
                (body.get("routing") or {}).get("model")
                or body.get("model")
                or self.model
            ),
            answer_confidence=answer_confidence,
            probabilities=probabilities,
            latency_ms=latency_ms,
            raw=body,
        )
