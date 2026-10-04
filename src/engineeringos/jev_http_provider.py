from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from system_one_contract import AdvisoryDecision, ROUTES, TypedQuestion
from system_one_provider import (
    BatchProviderResult,
    ChoiceResult,
    ProviderResult,
    SystemOneProviderError,
)


class JevCompatibleHTTPProvider:
    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
        health_path: str = "/health",
        readiness_path: str | None = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.health_path = health_path
        self.readiness_path = readiness_path

    def _headers(self) -> dict[str, str]:
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
        }
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_json(self, path: str) -> tuple[int, dict[str, Any], float]:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            headers=self._headers(),
            method="GET",
        )
        started = time.monotonic()
        with urllib.request.urlopen(
            request,
            timeout=self.timeout_seconds,
        ) as response:
            raw = response.read().decode("utf-8")
            body = json.loads(raw) if raw.strip() else {}
            return (
                response.status,
                body,
                round((time.monotonic() - started) * 1000, 3),
            )

    def health(self) -> dict[str, Any]:
        started = time.monotonic()
        try:
            status, body, health_latency = self._get_json(
                self.health_path
            )
            ready_body = None
            ready_status = None
            if self.readiness_path:
                ready_status, ready_body, _ = self._get_json(
                    self.readiness_path
                )
            available = (
                200 <= status < 300
                and (
                    ready_status is None
                    or 200 <= ready_status < 300
                )
            )
            return {
                "provider": self.name,
                "available": available,
                "status_code": status,
                "latency_ms": round(
                    (time.monotonic() - started) * 1000,
                    3,
                ),
                "health_latency_ms": health_latency,
                "body": body,
                "ready_status_code": ready_status,
                "ready_body": ready_body,
            }
        except Exception as exc:
            return {
                "provider": self.name,
                "available": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "latency_ms": round(
                    (time.monotonic() - started) * 1000,
                    3,
                ),
            }

    def _choice_question_payload(
        self,
        question: TypedQuestion,
    ) -> dict[str, Any]:
        question.validate()
        if question.kind != "choice":
            raise SystemOneProviderError(
                "SYSTEM_ONE_HTTP_PROVIDER_CURRENTLY_REQUIRES_CHOICE"
            )
        if not question.options:
            raise SystemOneProviderError(
                "CHOICE_OPTIONS_REQUIRED"
            )
        return {
            "type": "choice",
            "instructions": question.instructions,
            "criteria": (
                dict(question.criteria)
                if question.criteria
                else {
                    option: option.replace("_", " ").lower()
                    for option in question.options
                }
            ),
        }

    def decide_many(
        self,
        *,
        state: Any,
        questions: tuple[TypedQuestion, ...],
    ) -> BatchProviderResult:
        if not questions:
            raise SystemOneProviderError("QUESTIONS_REQUIRED")
        payload = {
            "state": state,
            "model": self.model,
            "questions": {
                q.question_id: self._choice_question_payload(q)
                for q in questions
            },
        }
        request = urllib.request.Request(
            f"{self.base_url}/v1/systemone",
            data=json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                body = json.loads(
                    response.read().decode("utf-8")
                )
                inference_header = response.headers.get(
                    "X-Inference-Time-Ms"
                )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(
                "utf-8",
                errors="replace",
            )
            raise SystemOneProviderError(
                f"SYSTEM_ONE_HTTP_{exc.code}:{detail[:500]}"
            ) from exc
        except Exception as exc:
            raise SystemOneProviderError(
                f"SYSTEM_ONE_HTTP_UNAVAILABLE:{type(exc).__name__}:{exc}"
            ) from exc

        if inference_header is not None:
            try:
                latency_ms: float | None = float(
                    inference_header
                )
            except ValueError:
                latency_ms = None
        else:
            decis_latency = (
                (body.get("decis") or {}).get("latency_ms")
                if isinstance(body, dict)
                else None
            )
            if decis_latency is not None:
                latency_ms = float(decis_latency)
            else:
                latency_ms = round(
                    (time.monotonic() - started) * 1000,
                    3,
                )

        raw_answers = body.get("answers") or {}
        by_id = {
            q.question_id: q
            for q in questions
        }
        answers: dict[str, ChoiceResult] = {}
        for question_id, question in by_id.items():
            answer = raw_answers.get(question_id)
            if not isinstance(answer, dict):
                raise SystemOneProviderError(
                    f"SYSTEM_ONE_ANSWER_MISSING:{question_id}"
                )
            choice = answer.get("choice")
            if choice not in question.options:
                raise SystemOneProviderError(
                    f"SYSTEM_ONE_CHOICE_OUT_OF_CONTRACT:{question_id}"
                )
            probabilities = {
                str(key): float(value)
                for key, value in (
                    answer.get("probabilities") or {}
                ).items()
            }
            answer_confidence = answer.get(
                "answer_confidence"
            )
            if answer_confidence is None:
                answer_confidence = probabilities.get(
                    choice
                )
            if answer_confidence is None:
                answer_confidence = answer.get(
                    "confidence"
                )
            if answer_confidence is None:
                raise SystemOneProviderError(
                    f"SYSTEM_ONE_ANSWER_CONFIDENCE_MISSING:{question_id}"
                )
            answer_confidence = float(
                answer_confidence
            )
            if not 0.0 <= answer_confidence <= 1.0:
                raise SystemOneProviderError(
                    f"SYSTEM_ONE_ANSWER_CONFIDENCE_INVALID:{question_id}"
                )
            answers[question_id] = ChoiceResult(
                question_id=question_id,
                choice=str(choice),
                answer_confidence=answer_confidence,
                probabilities=probabilities,
                raw_answer=answer,
            )

        return BatchProviderResult(
            answers=answers,
            model=str(
                (body.get("routing") or {}).get("model")
                or body.get("model")
                or self.model
            ),
            latency_ms=latency_ms,
            raw=body,
        )

    def decide(
        self,
        *,
        state: Any,
        question: TypedQuestion,
    ) -> ProviderResult:
        batch = self.decide_many(
            state=state,
            questions=(question,),
        )
        answer = batch.answers[
            question.question_id
        ]
        if answer.choice not in ROUTES:
            raise SystemOneProviderError(
                "SYSTEM_ONE_ROUTE_OUT_OF_CONTRACT"
            )
        decision = AdvisoryDecision(
            source=self.name,
            question_id=question.question_id,
            recommended_route=answer.choice,
            confidence=answer.answer_confidence,
            raw_answer=answer.raw_answer,
        )
        decision.validate()
        return ProviderResult(
            decision=decision,
            model=batch.model,
            answer_confidence=(
                answer.answer_confidence
            ),
            probabilities=answer.probabilities,
            latency_ms=batch.latency_ms,
            raw=batch.raw,
        )
