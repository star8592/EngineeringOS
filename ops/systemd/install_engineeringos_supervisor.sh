#!/usr/bin/env bash
set -euo pipefail
test "$(id -u)" -eq 0 || { echo "root required" >&2; exit 1; }
install -m 0644 ops/systemd/engineeringos-supervisor.service /etc/systemd/system/engineeringos-supervisor.service
systemctl daemon-reload
systemctl enable engineeringos-supervisor.service
echo "ENGINEERINGOS_SUPERVISOR=INSTALLED"
echo "Start only after stopping any legacy bare supervisor process."
