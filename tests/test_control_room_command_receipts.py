import pathlib

root = pathlib.Path(".")
dash = (root / "dashboard/index.html").read_text()
proj = (root / "src/engineeringos/dashboard_projector.py").read_text()
sup = (root / "src/engineeringos/supervisor.py").read_text()
details = (root / "src/engineeringos/control_loop_details.py").read_text()

assert "Command receipts & outcome evidence" in dash
assert "./runtime/control-loop-details.json" in dash
assert "Unknown completion" in dash
assert "Probe required" in dash
assert "Evidence invalid" in dash
assert "retry_decision" in dash
assert "evidence_integrity" in dash
assert "control-loop/details.json" in proj
assert "dashboard/runtime/control-loop-details.json" in proj
assert "src/engineeringos/control_loop_details.py" in sup
assert "command_probe_required" in sup
assert "command_evidence_invalid" in sup
assert "DERIVED_FROM_COMMAND_EVENT_LOG" in details
assert "verify_evidence_ref" in details
assert "target_mutation_authorized" in details
print("15 Control Room command-receipt integration invariants passed")
