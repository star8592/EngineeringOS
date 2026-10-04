#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unit_dir="$HOME/.config/systemd/user"
unit="$unit_dir/engineeringos-supervisor.service"
mkdir -p "$unit_dir" "$repo/.engineeringos/runtime"
cat > "$unit" <<EOF
[Unit]
Description=EngineeringOS Continuous Project Supervisor
After=default.target

[Service]
Type=simple
WorkingDirectory=$repo
ExecStart=/usr/bin/python3 $repo/src/engineeringos/supervisor.py --interval 300
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
case "${1:-install}" in
  install|start) systemctl --user enable --now engineeringos-supervisor.service ;;
  restart) systemctl --user restart engineeringos-supervisor.service ;;
  stop) systemctl --user disable --now engineeringos-supervisor.service ;;
  status) systemctl --user status engineeringos-supervisor.service --no-pager ;;
  *) echo "usage: $0 {install|start|restart|stop|status}" >&2; exit 2;;
esac
