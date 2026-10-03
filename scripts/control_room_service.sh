#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unit_dir="$HOME/.config/systemd/user"; unit="$unit_dir/engineeringos-control-room.service"
mkdir -p "$unit_dir"
cat > "$unit" <<EOF
[Unit]
Description=EngineeringOS G2 Read-Only Control Room
After=default.target

[Service]
Type=simple
WorkingDirectory=$repo
ExecStart=/usr/bin/python3 $repo/scripts/control_room_server.py --bind 127.0.0.1 --port 8777 --directory $repo/dashboard
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
case "${1:-install}" in
  install|start) systemctl --user enable --now engineeringos-control-room.service ;;
  restart) systemctl --user restart engineeringos-control-room.service ;;
  stop) systemctl --user disable --now engineeringos-control-room.service ;;
  status) systemctl --user status engineeringos-control-room.service --no-pager ;;
  *) echo "usage: $0 {install|start|restart|stop|status}" >&2; exit 2;;
esac
