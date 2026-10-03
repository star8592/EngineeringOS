# EXP-016: G1 Genericity

## Goal

Prove EngineeringOS core is not accidentally a DevControl-specific manager.

## Acceptance

Select a second real Git repository and, without changing core fact/policy/queue/dependency/lease/scheduler semantics:

1. inventory source/workspaces;
2. emit scoped facts/evidence;
3. produce at least one reconciliation/policy result where applicable;
4. materialize a durable work queue;
5. produce a shadow dispatch plan.

Only an adapter/project profile may be added. Any required core conditional such as `if project == DevControl` is a G1 failure and triggers architecture correction.
