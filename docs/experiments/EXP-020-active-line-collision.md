# EXP-020: Active Development Collision

Date: 2026-10-03

EngineeringOS now has an executable pre-dispatch collision check comparing a planned mutation surface with files currently modified/untracked by an active dirty development line.

For the planned DevControl release-provenance producer change, the current active branch is `fix/release-supervisor-self-update` with 32 modified/untracked paths. The explicitly planned provenance surface contains 5 paths. Exact path overlap is currently 0, so the probe returns `CLEAR` rather than blocking merely because the repository is dirty.

This corrects an overly conservative human interpretation from the preceding observation: dirty workspace alone is not sufficient evidence of collision. Blocking requires a demonstrated conflicting surface (or a stronger semantic dependency/ownership rule).

## Invariants

- dirty + overlapping mutation path => `BLOCKED_BY_ACTIVE_LINE` / `ISOLATE_OR_WAIT`;
- dirty + disjoint exact path surface => `CLEAR` at this evidence level;
- overlap without an active dirty line does not itself block.

Exact-path clearance is necessary but not sufficient for safety. Future semantic overlap checks must account for shared contracts, generated files, build metadata, and dependency relationships.
