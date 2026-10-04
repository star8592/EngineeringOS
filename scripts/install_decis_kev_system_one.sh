#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
state_root="${XDG_DATA_HOME:-$HOME/.local/share}/engineeringos/decis-kev"
src="$state_root/src"
models="$state_root/models"
unit_dir="$HOME/.config/systemd/user"
unit="$unit_dir/engineeringos-decis-kev.service"
port="${ENGINEERINGOS_DECIS_KEV_PORT:-8019}"
revision="ae7c27be7774efc75411b97037a9d2f9ff98abc3"
hf_home="${HF_HOME:-$HOME/.cache/huggingface}"
python_bin="${ENGINEERINGOS_DECIS_KEV_PYTHON:-python3.12}"

command -v uv >/dev/null 2>&1 || { echo "uv is required" >&2; exit 1; }
command -v "$python_bin" >/dev/null 2>&1 || { echo "$python_bin is required" >&2; exit 1; }
"$python_bin" - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit("Decis kev environment requires Python >= 3.12")
print("DECIS_KEV_PYTHON=", sys.executable, sys.version.split()[0])
PY

mkdir -p "$state_root" "$models" "$unit_dir"
if [ ! -d "$src/.git" ]; then
  git clone https://github.com/chaitin/Decis.git "$src"
fi
cd "$src"
git fetch origin "$revision"
git checkout --detach "$revision"

export UV_LINK_MODE=copy
uv sync --python "$python_bin" --extra dev --extra kev
uv run decis download --engine kev-0.8b --dest "$models"

adapter="$models/kev-0.8b"
for required in adapter_config.json adapter_model.safetensors head.pt; do
  test -s "$adapter/$required" || {
    echo "missing kev adapter file: $adapter/$required" >&2
    exit 1
  }
done

HF_HOME="$hf_home" "$src/.venv/bin/python" - <<'PY'
import json
from pathlib import Path
from huggingface_hub import snapshot_download

repo_id = "Qwen/Qwen3.5-0.8B-Base"
revision = "dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68"
root = Path(snapshot_download(repo_id=repo_id, revision=revision, local_files_only=True))
marker = root / "config.json"
index = root / "model.safetensors.index.json"
if not marker.is_file() or not index.is_file():
    raise SystemExit(f"incomplete Qwen base cache at {root}")
manifest = json.loads(index.read_text())
missing = sorted({
    name for name in manifest.get("weight_map", {}).values()
    if isinstance(name, str) and not (root / name).is_file()
})
if missing:
    raise SystemExit(f"incomplete Qwen base cache, missing: {missing[:3]}")
print("DECIS_KEV_BASE=", root)
PY

"$src/.venv/bin/python" - <<'PY'
import torch
if not torch.cuda.is_available():
    raise SystemExit("CUDA is required for the managed kev shadow candidate")
print("DECIS_KEV_TORCH=", torch.__version__, "CUDA=", torch.cuda.get_device_name(0))
PY

cat > "$unit" <<EOF
[Unit]
Description=EngineeringOS Decis kev GPU System-One shadow candidate
After=default.target

[Service]
Type=simple
Environment=DECIS_API_KEY=local
Environment=DECIS_DEVICE=cuda
Environment=DECIS_DTYPE=bf16
Environment=HF_HUB_OFFLINE=1
Environment="HF_HOME=$hf_home"
ExecStart=$src/.venv/bin/decis serve --engine kev-0.8b --model-path kev-0.8b=$adapter --host 127.0.0.1 --port $port --preload
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now engineeringos-decis-kev.service
printf 'Decis kev shadow candidate installed at http://127.0.0.1:%s\n' "$port"
printf 'Readiness: curl -fsS -H "Authorization: Bearer local" http://127.0.0.1:%s/readyz\n' "$port"
printf 'Benchmark: python3 %s/scripts/run_system_one_edb.py --backend decis --base-url http://127.0.0.1:%s --model jev-latest --api-key local\n' "$repo" "$port"
