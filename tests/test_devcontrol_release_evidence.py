import json
import pathlib
import sys
import tempfile

sys.path.insert(0, "src/engineeringos")

import devcontrol_release_evidence as release_module
from devcontrol_release_evidence import build_release_evidence


ready = {
    "status": "ready",
    "version": "3.1.21",
    "release_id": "e3b88b47",
}
qualification = {
    "release": "e3b88b47",
    "gates": ["release_gate_all", "post_deploy"],
}
deployment = {
    "deployment_identity_state": "RESOLVED",
    "deployment_binding_sha256": "c" * 64,
    "server": {
        "tree_sha256": "a" * 64,
    },
    "agent": {
        "tree_sha256": "b" * 64,
    },
    "reasons": [],
}

out = build_release_evidence(
    ready=ready,
    qualification_evidence=qualification,
    release_evidence_file=pathlib.Path("/tmp/e3b88b47.json"),
    full_source_sha="e3b88b47ccce96409eb929fd56ff8ff6e4cc68de",
    deployment=deployment,
)
assert out["source_identity_state"] == "RESOLVED"
assert out["qualification_state"] == "RESOLVED"
assert out["deployment_identity_state"] == "RESOLVED"
assert out["artifact_identity_state"] == "PARTIAL"
assert out["deployment_binding_sha256"] == "c" * 64
assert "deployed-tree digests" in out["reasoning"]["deployment_identity"]
assert "not durably persisted" in out["reasoning"]["artifact_identity"]

partial = build_release_evidence(
    ready=ready,
    qualification_evidence=qualification,
    release_evidence_file=None,
    full_source_sha=None,
    deployment={
        "deployment_identity_state": "PARTIAL",
        "server": {},
        "agent": {},
        "reasons": ["SOURCE_IDENTITY_UNRESOLVED"],
    },
)
assert partial["source_identity_state"] == "UNKNOWN"
assert partial["deployment_identity_state"] == "PARTIAL"
assert partial["artifact_identity_state"] == "UNKNOWN"
assert partial["deployment_binding_sha256"] is None
assert "SOURCE_IDENTITY_UNRESOLVED" in partial["reasoning"]["deployment_identity"]

unqualified = build_release_evidence(
    ready=ready,
    qualification_evidence={"gates": ["post_deploy"]},
    release_evidence_file=None,
    full_source_sha="e3b88b47ccce96409eb929fd56ff8ff6e4cc68de",
    deployment=deployment,
)
assert unqualified["qualification_state"] == "UNKNOWN"

with tempfile.TemporaryDirectory() as td:
    root = pathlib.Path(td)
    release_module.OUT = root / "nested/artifacts/devcontrol-release-evidence.json"
    release_module.EVIDENCE_DIR = root / "release-evidence"
    release_module.EVIDENCE_DIR.mkdir()
    (release_module.EVIDENCE_DIR / "e3b88b47.json").write_text(
        json.dumps(qualification)
    )
    release_module.fetch = lambda _url: ready
    release_module.git = lambda *args: (
        "e3b88b47ccce96409eb929fd56ff8ff6e4cc68de"
        if args == ("rev-list", "--all")
        else ""
    )
    release_module.observe_deployment = lambda **_kwargs: deployment
    release_module.run()
    assert release_module.OUT.exists()
    persisted = json.loads(release_module.OUT.read_text())
    assert persisted["deployment_identity_state"] == "RESOLVED"

print("14 DevControl release-evidence binding invariants passed")
