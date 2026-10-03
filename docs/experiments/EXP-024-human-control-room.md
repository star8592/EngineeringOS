# EXP-024: Human Control Room

Added the first static read-only Control Room prototype backed by the existing G2 shadow snapshot and durable queue. It deliberately consumes the same machine state as agents rather than inventing dashboard-only status.

Next iterations add time-series history, dependency/contract graph visualization, lease/agent activity, evidence drill-down, and shadow-decision outcome comparison.
