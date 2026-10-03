# EXP-014: Scheduler / Dispatcher

## Goal
Turn durable work items into execution candidates without conflating scheduling with authorization.

Scheduler computes readiness from state, dependencies, leases, policy, and assurance requirements. Dispatcher selects an execution class:
- deterministic local automation;
- fast open System-One judge;
- strong reasoning model;
- formal/model-checking path;
- human/explicit-policy gate where required.

Initial implementation remains advisory: it emits dispatch plans and does not execute target-project mutations.
