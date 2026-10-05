# ADR-032: Adopt verified quiet protected work

Status: Accepted

## Problem

External repositories may already contain valuable uncommitted human/agent work when EngineeringOS begins management. Protecting that work indefinitely prevents takeover; blindly committing it risks stealing incomplete or conflicting work.

## Decision

Protected existing work may become ADOPTABLE only under an explicit project policy ADOPT_VERIFIED_QUIET and an A2 management target.

Adoption requires all of the following evidence at the same source SHA:
- canonical origin/branch/upstream with no divergence;
- protected inventory identity still matches the selected adoption plan;
- every protected candidate group is QUIET beyond the configured quiet window;
- no active process references or writable handles inside the source repository;
- a verified deferred candidate for committed baseline debt, with no convergence authority;
- a verified protected repair candidate whose composed full-project verification passes;
- repair paths are a subset of the protected surface;
- deferred candidate paths are disjoint from protected paths;
- no sensitive protected paths;
- exact candidate item IDs and hashes match the manager-selected adoption plan.

The adoption gate itself never mutates the repository. It only changes the state from PROTECTED_EXISTING_WORK to ADOPTABLE.

## Authority

The user's A2 management mandate is durable management authority. The adoption policy is the explicit rule for pre-existing work. EngineeringOS still cannot infer adoption merely from tests passing or from a repository being quiet.

## Failure semantics

Any source change, process activity, candidate/hash mismatch, verification failure, sensitive path, or branch/origin drift invalidates the plan and returns BLOCKED. No product-intent question is raised for these machine conditions.
