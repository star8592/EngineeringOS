# Open System-One Judge Layer

EngineeringOS should support a provider-neutral, self-hosted fast judgment layer for high-volume engineering events.

## Purpose

Fast judges classify and route events such as duplicate-task candidates, semantic-conflict candidates, architecture drift, approval/tool-surface changes, and whether deeper reasoning or formal verification is required.

They are scouts/routers, not proof kernels.

## Desired cascade

engineering events
→ small fast open judge
→ deterministic automation when confidently low-risk
→ larger local judge for uncertain cases
→ strong reasoning model for complex/high-risk semantics
→ model checking/formal proof for critical invariants.

## Requirements

- open-weight/self-hostable by default;
- provider-neutral typed interface;
- calibrated probabilities, not only labels;
- replaceable implementations;
- benchmarked on EngineeringOS/DevControl evidence rather than vendor leaderboards;
- false-negative cost measured explicitly for safety-critical routing.
