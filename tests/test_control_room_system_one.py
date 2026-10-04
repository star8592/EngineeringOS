import pathlib

root = pathlib.Path(".")
dash = (root / "dashboard/index.html").read_text()
proj = (root / "src/engineeringos/dashboard_projector.py").read_text()
sup = (root / "src/engineeringos/supervisor.py").read_text()
shadow = (root / "src/engineeringos/system_one_shadow.py").read_text()

assert "System-One · open shadow routing" in dash
assert "EDB curation" in dash
assert "./runtime/system-one.json" in dash
assert "./runtime/system-one-edb-curation.json" in dash
assert "./runtime/system-one-edb-adjudication.json" in dash
assert "Gold labels" in dash
assert "Auto adjudication" in dash
assert "human_authority_decision" in dash
assert "human_authority_source" in dash
assert "human_authority_confidence" not in dash
assert "system-one/projection.json" in proj
assert "system-one/edb-curation-summary.json" in proj
assert "system-one/edb-adjudication-summary.json" in proj
assert "dashboard/runtime/system-one-edb-adjudication.json" in proj
assert "src/engineeringos/system_one_shadow.py" in sup
assert "src/engineeringos/edb_curation.py" in sup
assert "src/engineeringos/edb_adjudication.py" in sup
assert "system_one_edb_gold" in sup
assert "system_one_edb_invalid_reviews" in sup
assert "SYSTEM_ONE_ADVISORY" in shadow
assert "PROJECT_POLICY" in shadow
assert "processing-lane+authority-policy/v2" in shadow
print("22 Control Room/System-One adjudication-boundary invariants passed")
