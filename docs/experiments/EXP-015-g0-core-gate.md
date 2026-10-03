# EXP-015: G0 Core Coherence Gate

Date: 2026-10-03

The minimum EngineeringOS control-loop components are now executable and pass their current invariant suite:

- Fact Registry: 2 invariants
- Policy Plane: 4 invariants
- Durable Work Queue: 3 invariants
- Ownership/Lease/Evidence Closure: 4 invariants
- Dependency Graph: 4 invariants
- Scheduler: 3 invariants

Total: 20 current invariants passed. Required core modules are present. `G0_CORE_COHERENCE = PASS` for the current prototype definition.

This does not authorize autonomous target mutation. It means the minimum advisory control loop is coherent enough to proceed to G1 genericity and G2 shadow dogfood experiments.

The first shadow dispatch plan for DevControl contains five dispatchable review tasks and explicitly sets `execution_authorized=false` for all of them.
