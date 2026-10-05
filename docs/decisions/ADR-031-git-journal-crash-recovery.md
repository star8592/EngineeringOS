# ADR-031: Recover committed work across the Git/journal crash window

Status: Accepted

## Problem

Autonomous convergence commits to Git before the durable WORK_COMMITTED event is appended. A process crash in that narrow window leaves repository truth ahead of journal truth. Treating the new HEAD as generic SOURCE_SHA_DRIFT can cause a valid completed change to be replanned or duplicated.

## Decision

Every EngineeringOS autonomous commit carries recovery trailers that bind the commit to durable work identity and contract evidence:

- EngineeringOS-Item
- EngineeringOS-Source
- EngineeringOS-Diff-SHA256
- EngineeringOS-Recovery-Token

The recovery token is a deterministic hash of project, item id, intent generation, source SHA, allowed paths and verification argv.

On restart, durable_supervisor_runtime reconciles Git before dispatching any provider. Recovery is accepted only when:

1. source SHA is an ancestor of current HEAD;
2. the first first-parent descendant has source SHA as its parent;
3. all required trailers exist exactly once;
4. item/source/recovery token match the durable contract;
5. actual changed paths are non-empty and contained in allowed_paths;
6. the reconstructed binary diff hash matches the committed trailer.

When all checks pass, EngineeringOS reconstructs a commit receipt, appends the missing WORK_COMMITTED event, and applies the normal completion predicate. A1/A2 capability-evidence work may therefore become RESOLVED without re-running the coding provider.

## Safety

HEAD movement alone is never completion evidence. A commit message containing an item id alone is never completion evidence. Missing, malformed, mismatched, or ambiguous recovery evidence fails closed and the ordinary reconciliation path remains authoritative.

## Acceptance

A restart test commits a real mutation and intentionally skips all journal completion events. The next resume recovers the exact commit, invokes the provider zero times, records the work as RESOLVED, and a second restart performs no duplicate recovery or mutation.
