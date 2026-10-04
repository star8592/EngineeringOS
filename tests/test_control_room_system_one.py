import pathlib

root = pathlib.Path(".")
dash = (root / "dashboard/index.html").read_text()
proj = (root / "src/engineeringos/dashboard_projector.py").read_text()
sup = (root / "src/engineeringos/supervisor.py").read_text()
shadow = (root / "src/engineeringos/system_one_shadow.py").read_text()

assert "System-One · Laya shadow routing" in dash
assert "./runtime/system-one.json" in dash
assert "human_authority_recommendation" in dash
assert "system-one/projection.json" in proj
assert "dashboard/runtime/system-one.json" in proj
assert "src/engineeringos/system_one_shadow.py" in sup
assert "system_one_status" in sup
assert "PROCESSING_LANE" in shadow
assert "HUMAN_AUTHORITY" in shadow
assert "routing_contract" in shadow
print("10 Control Room/System-One two-axis integration invariants passed")
