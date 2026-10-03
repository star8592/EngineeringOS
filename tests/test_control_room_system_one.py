import pathlib

root=pathlib.Path(".")
dash=(root/"dashboard/index.html").read_text()
proj=(root/"src/engineeringos/dashboard_projector.py").read_text()
sup=(root/"src/engineeringos/supervisor.py").read_text()

assert "System-One · Laya shadow routing" in dash
assert "./runtime/system-one.json" in dash
assert "system-one/projection.json" in proj
assert "dashboard/runtime/system-one.json" in proj
assert "src/engineeringos/system_one_shadow.py" in sup
assert "system_one_status" in sup
print("6 Control Room/System-One integration invariants passed")
