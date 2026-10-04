import hashlib
import pathlib
import sys
import tempfile

sys.path.insert(0, "src/engineeringos")

from control_loop_details import build_details, verify_evidence_ref


def event(seq, typ, command_id, *, side_effecting=False, refs=()):
    payload = {
        "command_id": command_id,
        "idempotency_key": f"idem:{command_id}",
        "action_kind": "TEST_ACTION",
        "side_effecting": side_effecting,
    }
    if refs:
        payload["evidence_refs"] = list(refs)
    return {
        "seq": seq,
        "event_id": f"e{seq}",
        "type": typ,
        "payload": payload,
    }


with tempfile.TemporaryDirectory() as td:
    root = pathlib.Path(td)
    evidence = root / "ok.json"
    evidence.write_bytes(b'{"ok":true}\n')
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    good_ref = f"file:{evidence}#sha256:{digest}"

    bad = root / "bad.json"
    bad.write_text("tampered")
    bad_ref = f"file:{bad}#sha256:{'0'*64}"

    good = verify_evidence_ref(good_ref)
    assert good["verified"] is True
    assert good["reason"] == "VERIFIED"

    bad_result = verify_evidence_ref(bad_ref)
    assert bad_result["verified"] is False
    assert bad_result["reason"] == "EVIDENCE_DIGEST_MISMATCH"

    unsupported = verify_evidence_ref("https://example.test/evidence")
    assert unsupported["reason"] == "UNSUPPORTED_EVIDENCE_SCHEME"

    events = [
        event(1, "COMMAND_INTENT_RECORDED", "ok"),
        event(2, "COMMAND_DISPATCHED", "ok"),
        event(3, "COMMAND_EFFECT_CONFIRMED", "ok", refs=(good_ref,)),
        event(4, "COMMAND_INTENT_RECORDED", "unknown", side_effecting=True),
        event(5, "COMMAND_DISPATCHED", "unknown", side_effecting=True),
        event(6, "COMMAND_COMPLETION_UNKNOWN", "unknown", side_effecting=True),
        event(7, "COMMAND_INTENT_RECORDED", "broken"),
        event(8, "COMMAND_DISPATCHED", "broken"),
        event(9, "COMMAND_EFFECT_CONFIRMED", "broken", refs=(bad_ref,)),
    ]
    projection = {
        "mode": "SHADOW",
        "target": "Example",
        "snapshot_content_sha256": "abc",
        "items": [
            {
                "item_id": "w1",
                "kind": "GOOD",
                "schedule_state": "DISPATCHABLE",
                "policy": "ALLOW",
                "command_id": "ok",
                "command_state": "SUCCEEDED",
            },
            {
                "item_id": "w2",
                "kind": "UNKNOWN",
                "schedule_state": "DISPATCHABLE",
                "policy": "ALLOW",
                "command_id": "unknown",
                "command_state": "UNKNOWN_COMPLETION",
            },
            {
                "item_id": "w3",
                "kind": "BROKEN",
                "schedule_state": "DISPATCHABLE",
                "policy": "ALLOW",
                "command_id": "broken",
                "command_state": "SUCCEEDED",
            },
            {
                "item_id": "w4",
                "kind": "BLOCKED",
                "schedule_state": "BLOCKED",
                "policy": "DENY",
                "command_state": None,
            },
        ],
    }

    details = build_details(projection, events)
    by_id = {row["item_id"]: row for row in details["items"]}

    assert details["authority"] == "DERIVED_FROM_COMMAND_EVENT_LOG"
    assert details["target_mutation_authorized"] is False
    assert details["summary"]["commands"] == 3
    assert details["summary"]["succeeded"] == 2
    assert details["summary"]["unknown_completion"] == 1
    assert details["summary"]["probe_required"] == 1
    assert details["summary"]["verified_receipts"] == 1
    assert details["summary"]["evidence_invalid"] == 1

    assert by_id["w1"]["receipt_source"] == "COMMAND_EVENT_REPLAY"
    assert by_id["w1"]["evidence_integrity"] == "VERIFIED"
    assert by_id["w1"]["retry_decision"] == "DO_NOT_RETRY"
    assert [row["type"] for row in by_id["w1"]["timeline"]] == [
        "COMMAND_INTENT_RECORDED",
        "COMMAND_DISPATCHED",
        "COMMAND_EFFECT_CONFIRMED",
    ]

    assert by_id["w2"]["command_state"] == "UNKNOWN_COMPLETION"
    assert by_id["w2"]["retry_decision"] == "PROBE_REQUIRED"
    assert by_id["w2"]["evidence_integrity"] == "PENDING"

    assert by_id["w3"]["evidence_integrity"] == "INVALID"
    assert by_id["w4"]["receipt_source"] == "NO_COMMAND"
    assert by_id["w4"]["evidence_integrity"] == "NOT_APPLICABLE"

print("22 command receipt projection invariants passed")
