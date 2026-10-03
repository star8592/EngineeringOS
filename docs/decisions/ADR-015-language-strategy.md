# ADR-015: Language strategy — Python for discovery, Rust for stabilized control-plane core
Status: Accepted

EngineeringOS is currently prototyped primarily in Python because the project is still discovering its data model, reconciliation semantics, policy boundaries, scheduling rules, and dogfood requirements. Rapid iteration and inspectability are more valuable than premature systems-language optimization at this stage.

The intended long-term architecture is polyglot:

- **Rust** for stabilized long-running control-plane services, concurrency-sensitive state machines, durable queue/lease coordination, high-integrity adapters, policy enforcement boundaries, and performance-sensitive ingestion.
- **Python** for experiments, model evaluation, dataset construction, research tooling, formal-method integration glue, and rapidly changing analysis logic.
- **Web UI (TypeScript/JavaScript + HTML/CSS)** for the Human Control Room.
- **Declarative JSON/YAML/TOML** for project profiles, contract graphs, policy/configuration, and evidence schemas where appropriate.

## Migration rule

Do not rewrite a Python module in Rust merely because Rust is preferred. A module becomes a Rust migration candidate only when:
1. its semantics have stabilized through dogfood;
2. it sits on a reliability/performance/concurrency boundary;
3. its interface can be expressed as a stable contract;
4. executable parity tests exist so the Rust implementation can be proven behaviorally equivalent.

## Initial Rust migration candidates

Likely first candidates after G2 stabilization:
- Fact/World Model storage primitives;
- durable Work Queue and lease state machine;
- dependency/contract graph engine;
- scheduler/dispatcher core;
- evidence ingestion/event log;
- policy/authorization enforcement boundary.

Likely Python-retained areas:
- System-One/Judge benchmarking;
- EDB dataset construction;
- experimental semantic analysis;
- TLA+/Lean orchestration and report generation;
- one-off repository research/adapters until stabilized.
