from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile
from typing import Any

from command_processor import replay_command, retry_decision
from event_store import read_events
from state_paths import runtime

STATE = runtime()


def atomic_json(path: pathlib.Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        json.dumps(
            obj,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode()
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def verify_evidence_ref(ref: str) -> dict[str, Any]:
    result = {
        "ref": ref,
        "scheme": None,
        "exists": False,
        "verified": False,
        "reason": None,
    }
    if not ref.startswith("file:"):
        result["reason"] = "UNSUPPORTED_EVIDENCE_SCHEME"
        return result

    body = ref[len("file:") :]
    marker = "#sha256:"
    if marker not in body:
        result["scheme"] = "file"
        result["reason"] = "SHA256_BINDING_REQUIRED"
        return result

    path_text, expected = body.rsplit(marker, 1)
    path = pathlib.Path(path_text)
    result["scheme"] = "file"
    result["path"] = str(path)
    result["expected_sha256"] = expected
    result["exists"] = path.exists()
    if not path.exists():
        result["reason"] = "EVIDENCE_FILE_MISSING"
        return result

    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    result["actual_sha256"] = actual
    if actual != expected:
        result["reason"] = "EVIDENCE_DIGEST_MISMATCH"
        return result

    result["verified"] = True
    result["reason"] = "VERIFIED"
    return result


def command_timeline(
    events: list[dict[str, Any]],
    command_id: str,
) -> list[dict[str, Any]]:
    rows = []
    for event in events:
        payload = event.get("payload") or {}
        if payload.get("command_id") != command_id:
            continue
        rows.append(
            {
                "seq": event.get("seq"),
                "event_id": event.get("event_id"),
                "type": event.get("type"),
                "evidence_refs": payload.get("evidence_refs") or [],
            }
        )
    return rows


def build_details(
    control_projection: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    command_count = 0
    succeeded = 0
    unknown_completion = 0
    probe_required = 0
    verified_receipts = 0
    evidence_invalid = 0

    for item in control_projection.get("items", []):
        command_id = item.get("command_id")
        detail = {
            "item_id": item.get("item_id"),
            "kind": item.get("kind"),
            "schedule_state": item.get("schedule_state"),
            "policy": item.get("policy"),
            "target_mutation_authorized": False,
            "command_id": command_id,
            "receipt_source": (
                "COMMAND_EVENT_REPLAY"
                if command_id
                else "NO_COMMAND"
            ),
            "command_state": item.get("command_state"),
            "retry_decision": None,
            "outcome": None,
            "attempts": 0,
            "side_effecting": None,
            "idempotency_key": None,
            "action_kind": None,
            "timeline": [],
            "evidence": [],
            "evidence_integrity": "NOT_APPLICABLE",
        }

        if not command_id:
            items.append(detail)
            continue

        command_count += 1
        state = replay_command(events, command_id)
        if state is None:
            detail["command_state"] = "MISSING_REPLAY_STATE"
            detail["evidence_integrity"] = "INVALID"
            evidence_invalid += 1
            items.append(detail)
            continue

        decision = retry_decision(state)
        evidence = [
            verify_evidence_ref(ref)
            for ref in state.get("evidence_refs", [])
        ]
        if evidence:
            integrity = (
                "VERIFIED"
                if all(row["verified"] for row in evidence)
                else "INVALID"
            )
        elif state.get("state") in {"SUCCEEDED", "NOT_APPLIED"}:
            integrity = "INVALID"
        else:
            integrity = "PENDING"

        detail.update(
            {
                "command_state": state.get("state"),
                "retry_decision": decision,
                "outcome": state.get("outcome"),
                "attempts": state.get("attempts", 0),
                "side_effecting": state.get("side_effecting"),
                "idempotency_key": state.get("idempotency_key"),
                "action_kind": state.get("action_kind"),
                "timeline": command_timeline(events, command_id),
                "evidence": evidence,
                "evidence_integrity": integrity,
            }
        )

        if state.get("state") == "SUCCEEDED":
            succeeded += 1
        if state.get("state") == "UNKNOWN_COMPLETION":
            unknown_completion += 1
        if decision == "PROBE_REQUIRED":
            probe_required += 1
        if integrity == "VERIFIED":
            verified_receipts += 1
        if integrity == "INVALID":
            evidence_invalid += 1

        items.append(detail)

    return {
        "schema_version": 1,
        "mode": control_projection.get("mode"),
        "target": control_projection.get("target"),
        "snapshot_content_sha256": control_projection.get(
            "snapshot_content_sha256"
        ),
        "target_mutation_authorized": False,
        "authority": "DERIVED_FROM_COMMAND_EVENT_LOG",
        "summary": {
            "items": len(items),
            "commands": command_count,
            "succeeded": succeeded,
            "unknown_completion": unknown_completion,
            "probe_required": probe_required,
            "verified_receipts": verified_receipts,
            "evidence_invalid": evidence_invalid,
        },
        "items": items,
    }


def run() -> dict[str, Any]:
    projection = json.loads(
        runtime("control-loop/projection.json").read_text()
    )
    events = read_events(
        runtime("control-loop/events.jsonl")
    )
    details = build_details(
        projection,
        events,
    )
    atomic_json(
        runtime("control-loop/details.json"),
        details,
    )
    return details


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False,
        )
    )
