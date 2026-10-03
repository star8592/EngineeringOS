# EXP-010: Policy Plane

## Goal

Separate factual reconciliation from engineering action policy.

The first executable policy classifies current DevControl source/production drift. With live production identity consistent and its release ID resolved to source provenance, source `3.1.16` versus production `3.1.14` is `ACCEPTABLE_DRIFT`, not failure.

## Next

Add policy inputs for age/SLO, CI qualification, production verification freshness, approval/tool-surface invariants, and convergence debt. Policy decisions must always retain links to the evidence that produced them.
