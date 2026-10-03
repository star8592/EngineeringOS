# EXP-008 Initial Findings: Fact Registry

Date: 2026-10-03

A minimal executable Fact Registry now represents engineering facts with subject, predicate, value, scope, observation time, source identity, authority, confidence, and evidence reference.

## First result

The earlier version mismatch is now modeled correctly rather than treated as a direct contradiction:

- `repository/origin-main` reports product version `3.1.16` at the latest observation.
- a canonical architecture document contains a production-health claim for version `3.1.14` and release ID `3a51151`.

Because the scopes differ, the registry emits `SOURCE_PRODUCTION_VERSION_DRIFT`, not `VALUE_CONTRADICTION`. Resolution requires live production identity plus provenance linking the production release ID to a full source SHA.

This also exposed why facts must be re-observed rather than copied from previous experiment prose: DevControl's source version advanced during EngineeringOS development. The World Model must be temporal and refreshable.

## Executable invariants

The initial tests establish:

1. same subject + predicate + scope with incompatible values is a contradiction;
2. different scopes are not direct contradictions merely because their values differ.

The host did not have `pytest` installed. EngineeringOS did not mutate the host Python environment merely to satisfy a preferred test runner; the two dependency-free invariant tests run directly with Python. Tooling dependencies will be declared explicitly before adopting a test framework.

## Next step

EXP-009 will add authority rules and temporal validity, then ingest live runtime/release evidence through the existing DevControl evidence sources. This will allow the registry to resolve source-vs-production drift without guessing.
