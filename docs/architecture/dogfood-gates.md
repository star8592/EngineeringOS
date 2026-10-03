# Dogfood Gates

EngineeringOS enters DevControl dogfooding progressively.

## G0 — Core coherence
World Model/facts, evidence reconciliation, policy, manager, durable queue, dependencies, leases, evidence closure, scheduler/dispatcher contracts all exist and pass invariants.

## G1 — Genericity
A second repository can be ingested without changing EngineeringOS core semantics. Project-specific behavior lives in adapters/policies.

## G2 — Shadow DevControl
EngineeringOS observes DevControl and produces plans/queues but executes nothing. Compare its findings with real engineering outcomes.

## G3 — Bounded deterministic actions
Permit reversible, deterministic, low-risk actions with explicit policy and evidence gates. No autonomous merge/delete/deploy.

## G4 — Controlled convergence
Permit selected branch/task convergence actions when dependency, lease, CI, provenance, assurance, and rollback requirements are satisfied.

## G5 — Production-affecting automation
Only after sustained dogfood evidence. Production actions require project policy, exact identity/provenance, post-action verification, and rollback evidence.
