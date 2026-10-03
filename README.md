# EngineeringOS

AI-native software engineering control plane for continuously evolving software systems.

EngineeringOS manages the causal chain from human intent to architecture, agent work, evidence, convergence, release, production verification, and learning. It coordinates mature engineering infrastructure instead of replacing Git, CI, merge queues, coding agents, or execution backends.

## Founding principles
- AI reasons; deterministic systems own durable state and execution.
- Globally evolving, locally deterministic.
- Parallel development must be paired with continuous convergence.
- Done means integrated, released, production-verified, cleaned up, and learned from.
- Architecture, contracts, tests, main, artifacts, and production evidence outrank chat history as engineering truth.
- DevControl is the selected machine-execution backend for this project; execution backends must not silently drift.

## First proving ground
DevControl is the first real system under management. Milestone 0 reconstructs its engineering state before any automated merging is attempted.

## Engineering memory

Important discussions must converge into durable project state; conversation history is not the authoritative engineering memory. See `docs/principles/engineering-memory.md` and ADR-004.
