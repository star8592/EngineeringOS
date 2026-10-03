# EXP-012: Ownership, Leases, and Evidence Closure

Implemented the first dependency-free coordination primitives for parallel agents.

Verified invariants:
1. an unexpired lease prevents a second agent from claiming the same work;
2. an expired lease can be reclaimed;
3. closure cannot be requested without evidence;
4. resolution requires `PENDING_RESOLUTION` and retains closure evidence.

This deliberately separates coordination from execution authority: holding a lease does not authorize destructive or production actions.
