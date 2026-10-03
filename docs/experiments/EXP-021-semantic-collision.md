# EXP-021: Semantic Collision Gate

Date: 2026-10-03

Exact-path collision checking returned CLEAR for the planned DevControl release-provenance work, but semantic collision analysis correctly found shared contract domains with the active `fix/release-supervisor-self-update` line.

Detected active semantic overlap:
- `release_identity`: `Cargo.toml`, `VERSION`
- `release_qualification`: `scripts/test_server_package.sh`

Result: `BLOCKED_BY_SEMANTIC_COLLISION`, required action `ISOLATE_OR_WAIT`.

This demonstrates why exact file overlap is insufficient. Different files can participate in the same release identity or qualification contract.

The current domain map is deliberately small and explicit. It is a bootstrap mechanism, not the final architecture. Future contract domains should come from machine-readable project manifests/dependency graphs rather than a growing hand-maintained global dictionary.
