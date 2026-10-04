import pathlib
import sys
import tempfile

sys.path.insert(0, "src/engineeringos")

from devcontrol_deployment_observer import (
    DeploymentObservationError,
    canonical_tree_digest,
    evaluate_deployment_binding,
    remote_tree_command,
)


with tempfile.TemporaryDirectory() as td:
    root = pathlib.Path(td)
    (root / "bin").mkdir()
    (root / "bin" / "gateway").write_bytes(b"gateway-v1")
    (root / "VERSION").write_text("3.1.21\n")
    first = canonical_tree_digest(root)
    second = canonical_tree_digest(root)
    assert first == second
    assert first["file_count"] == 2
    assert first["tree_sha256"]

    (root / "VERSION").write_text("3.1.22\n")
    changed = canonical_tree_digest(root)
    assert changed["tree_sha256"] != first["tree_sha256"]

    link = root / "current"
    link.symlink_to("bin/gateway")
    with_link = canonical_tree_digest(root)
    assert with_link["symlink_count"] == 1
    assert with_link["tree_sha256"] != changed["tree_sha256"]

cmd = remote_tree_command("/opt/devcontrol3/releases/e3b88b47")
assert cmd.startswith("python3 -c ")
assert "/opt/devcontrol3/releases/e3b88b47" in cmd
assert "\n" not in cmd

try:
    canonical_tree_digest(pathlib.Path("/definitely/missing"))
    raise AssertionError("missing tree root accepted")
except DeploymentObservationError as exc:
    assert str(exc) == "TREE_ROOT_MISSING"

server = {
    "state": "RESOLVED",
    "observed_release_id": "e3b88b47",
    "tree_sha256": "a" * 64,
}
agent = {
    "state": "RESOLVED",
    "observed_release_id": "e3b88b47",
    "tree_sha256": "b" * 64,
}
resolved = evaluate_deployment_binding(
    release_id="e3b88b47",
    full_source_sha="e3b88b47ccce96409eb929fd56ff8ff6e4cc68de",
    server=server,
    agent=agent,
)
assert resolved["state"] == "RESOLVED"
assert resolved["binding_sha256"]
assert resolved["reasons"] == []

wrong_source = evaluate_deployment_binding(
    release_id="e3b88b47",
    full_source_sha="21ee5ea86cca1890a5a830d2f680b14455f7f83b",
    server=server,
    agent=agent,
)
assert wrong_source["state"] == "PARTIAL"
assert "RELEASE_SOURCE_MISMATCH" in wrong_source["reasons"]

missing_agent = evaluate_deployment_binding(
    release_id="e3b88b47",
    full_source_sha="e3b88b47ccce96409eb929fd56ff8ff6e4cc68de",
    server=server,
    agent={"state": "UNKNOWN"},
)
assert missing_agent["state"] == "PARTIAL"
assert "AGENT_DEPLOYMENT_UNRESOLVED" in missing_agent["reasons"]
assert "AGENT_TREE_DIGEST_MISSING" in missing_agent["reasons"]

print("16 DevControl deployment-provenance invariants passed")
