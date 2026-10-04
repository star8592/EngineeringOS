import pathlib

root = pathlib.Path(".")
installer = (root / "scripts/install_decis_kev_system_one.sh").read_text()
provider = (root / "src/engineeringos/decis_provider.py").read_text()

assert "ae7c27be7774efc75411b97037a9d2f9ff98abc3" in installer
assert "uv sync --frozen --python" in installer and "--extra kev" in installer
assert "decis download --engine kev-0.8b --dest" in installer
assert "DECIS_DEVICE=cuda" in installer
assert "DECIS_DTYPE=bf16" in installer
assert "HF_HUB_OFFLINE=1" in installer
assert "HF_HUB_CACHE" in installer
assert "snapshot_download" not in installer
assert "--model-path kev-0.8b=" in installer
assert "engineeringos-decis-kev.service" in installer
assert "127.0.0.1:8019" in provider
assert "sed -i" not in installer and "patch " not in installer

print("12 managed Decis/kev installer contract invariants passed")
