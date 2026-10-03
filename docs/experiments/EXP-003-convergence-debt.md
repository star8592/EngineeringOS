# EXP-003: Typed workspaces and Convergence Debt

## Goal

Represent convergence pressure without pretending every old or divergent branch is bad.

## Initial debt dimensions

- Duplicate-state debt: multiple active labels/workspaces representing identical Git state without an explicit relationship.
- Divergence debt: active implementation lines drifting from authoritative main while still expected to converge.
- Overlap debt: independent active lines modifying the same engineering surface.
- Role debt: workspaces whose purpose cannot be classified as development, release, production snapshot, forensic/incident, experiment, or archive.
- Dirty-workspace debt: uncommitted state that is not captured as durable evidence.
- Verification debt: integrated/released work lacking required qualification or production evidence.

Scores must preserve the underlying evidence and dimensions. A single aggregate may be added later for dashboards, but it must never hide why debt exists.
