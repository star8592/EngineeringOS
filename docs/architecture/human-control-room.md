# Human Control Room

EngineeringOS must remain observable to humans. Automation does not imply invisibility.

The Control Room is a read-only projection of machine state, never a second source of truth. Initial views:
- system/gate health;
- control-loop stage status;
- durable work queue and lifecycle;
- branch/agent ownership and leases;
- dependency/contract graph;
- convergence debt;
- assurance/CI requirements and evidence;
- source -> artifact -> release -> runtime provenance;
- shadow decisions versus later outcomes.

Human operators should be able to drill from a red/yellow state to the exact evidence that caused it. Future action buttons must call the same policy/authorization APIs as agents; the dashboard must not create a parallel approval semantic.
