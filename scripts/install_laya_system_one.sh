#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
state_root="${XDG_DATA_HOME:-$HOME/.local/share}/engineeringos/laya"
venv="$state_root/venv"
unit_dir="$HOME/.config/systemd/user"
unit="$unit_dir/engineeringos-laya.service"
port="${ENGINEERINGOS_LAYA_PORT:-8017}"
device="${ENGINEERINGOS_LAYA_DEVICE:-auto}"

mkdir -p "$state_root" "$unit_dir"
python3 -m venv "$venv"
"$venv/bin/python" -m pip install --upgrade pip
"$venv/bin/python" -m pip install "laya[serve]"

cat > "$unit" <<EOF
[Unit]
Description=EngineeringOS local Laya System-One provider
After=default.target

[Service]
Type=simple
Environment=LAYA_HOST=127.0.0.1
Environment=LAYA_PORT=$port
Environment=LAYA_DEVICE=$device
Environment=LAYA_PRELOAD=1
Environment=LAYA_MODELS=typed-decisions
Environment=LAYA_AUTO_TASK=0
ExecStart=$venv/bin/laya-serve
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now engineeringos-laya.service
printf 'Laya service installed at http://127.0.0.1:%s\n' "$port"
printf 'Run: curl -fsS http://127.0.0.1:%s/health\n' "$port"
printf 'Then: %s/scripts/run_system_one_edb.py --require\n' "$repo"
