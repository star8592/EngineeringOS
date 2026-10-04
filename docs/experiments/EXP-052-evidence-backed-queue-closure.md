# EXP-052: Close recovered DevControl debt with authoritative evidence

Date: 2026-10-04

## Problem

After EXP-050 and EXP-051, the live evidence plane had already converged:

- current DevControl main CI = PASS;
- live production qualification = PASS;
- deployment identity = RESOLVED;
- artifact identity = PARTIAL.

However three historical work items remained `PENDING_RESOLUTION`:

- `RESTORE_MAIN_QUALIFICATION`;
- `RESOLVE_LIVE_PRODUCTION_QUALIFICATION`;
- `CLOSE_DEPLOYMENT_IDENTITY_GAP`.

The queue reconciler only knew how to close the original `RESOLVE_MAIN_QUALIFICATION` kind.

This created false persistent debt even though the authoritative conditions had recovered.

## Change

The queue reconciler now maps recovered conditions to immutable closure evidence.

### CI recovery

Both qualification-gap kinds close only from exact current-head CI success.

### Live production qualification

Closure requires the qualified release evidence file, release id, and full source SHA. The release evidence file is referenced with a SHA-256 content binding.

### Deployment identity

Closure requires the resolved deployment binding plus server and Agent deployed-tree digests.

### Artifact identity

No automatic closure was added. It remains open while build artifact identity is only PARTIAL.

## Expected live result

On the current DevControl state, the first post-merge Supervisor cycle should retire the three historical pending items while keeping `CLOSE_ARTIFACT_IDENTITY_GAP` active.

This reduces queue debt by evidence rather than deletion or status rewriting.
