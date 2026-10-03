# EXP-044: Durable System-One shadow observation ledger

Date: 2026-10-04

EngineeringOS now persists real Laya shadow-routing observations instead of overwriting a single projection every supervisor cycle.

Each observation is deduplicated by the tuple of snapshot identity, work item, and model revision. It records:

- work item and source snapshot identity;
- deterministic Scheduler lane;
- Laya raw recommendation and advisory route;
- probability distribution and answer confidence;
- model/checkpoint revision;
- latency;
- required assurance and automation class;
- whether the raw model recommendation agrees with the Scheduler reference.

These records are explicitly marked `WEAK_SCHEDULER_REFERENCE` and `edb_gold=false`. They are evidence for future benchmark curation, not ground truth. Scheduler/model agreement is therefore an operational metric, not an accuracy claim.

The rolling summary exposes observation count, comparable observations, Scheduler agreement, high-assurance disagreements, median confidence, and median latency in Control Room.

This creates a real data path for expanding EDB from dogfood while preserving the distinction between weak references and adjudicated benchmark labels.
