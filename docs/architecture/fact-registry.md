# Engineering Fact Registry

Engineering memory requires facts with provenance and time, not isolated strings.

Example:

```yaml
subject: devcontrol
predicate: product_version
value: 3.1.13
scope: repository/origin-main
observed_at: 2026-10-03T00:00:00Z
source_type: git-file
source_identity: VERSION@<source-sha>
authority: canonical-source
```

A live `/readyz` observation would be a separate fact with `scope: production`. If it says `3.1.14`, the system should surface source/production drift rather than rewriting either value.

## Authority is predicate-specific

Git may be authoritative for source identity; CI for qualification results; release manifests for artifact identity; runtime endpoints for deployed identity; accepted ADRs for intended architecture. No source is globally authoritative for every predicate.

## Temporal semantics

Old facts are not necessarily wrong. Incident reports and historical decisions preserve facts that were true at a prior time. Current-state reconciliation must respect validity windows and document role.
