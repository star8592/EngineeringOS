# EngineeringOS

AI-native software engineering control plane for continuously evolving software systems.

EngineeringOS manages the causal chain from human intent to architecture, agent work, evidence, convergence, release, production verification, and learning. It coordinates mature engineering infrastructure instead of replacing Git, CI, merge queues, coding agents, or execution backends.

**Cross-project access / login protocol:** Before SSH, DevControl/Zoria remote operations, OAuth, Chrome, payment credentials or deployment, read the [single canonical access and authentication lessons runbook](docs/operations/CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md). Every project root `AGENTS.md` should link to it; audit with `python3 scripts/audit_access_runbook_links.py /path/to/code/workspace`. A link only confirms discoverability, not actual login success or authorization.\n\n**Cross-project mandatory data integrity rule:** [ADR-033 — No embedded business configuration or fabricated records](docs/decisions/ADR-033-no-hardcoded-or-fabricated-business-data.md). Every project must use real provenance-backed data and explicit configuration; scanner entrypoint: `python3 scripts/audit_data_integrity.py /path/to/repo`. A scanner result is not proof of complete remediation.

## Founding principles
- AI reasons; deterministic systems own durable state and execution.
- Globally evolving, locally deterministic.
- Parallel development must be paired with continuous convergence.
- Done means integrated, released, production-verified, cleaned up, and learned from.
- Architecture, contracts, tests, main, artifacts, and production evidence outrank chat history as engineering truth.
- DevControl is the selected machine-execution backend for this project; execution backends must not silently drift.

## First proving ground
DevControl is the first real system under management. Milestone 0 reconstructs its engineering state before any automated merging is attempted.

## Engineering memory

Important discussions must converge into durable project state; conversation history is not the authoritative engineering memory. See `docs/principles/engineering-memory.md` and ADR-004.

## Continuous supervisor

EngineeringOS can continuously supervise DevControl in G2 shadow mode without mutating the target project:

```bash
./scripts/engineeringos_service.sh install
python3 scripts/engineeringos_status.py
```

The supervisor refreshes live engineering evidence, reconciliation, queue, scheduling, shadow command evidence, convergence time-series, and the read-only Control Room every five minutes. Mutable state lives under `.engineeringos/runtime/`; committed `.engineeringos/**` content remains historical engineering evidence.
