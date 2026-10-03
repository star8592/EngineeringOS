# Engineering Memory: Discussion Must Become Durable State

Status: Founding principle

EngineeringOS treats important engineering discussion as input, not durable truth. A useful discussion is incomplete until its decisions, hypotheses, evidence, unresolved questions, and superseded ideas are written into versioned project state.

## Invariant

**Conversation is a discovery surface; the repository is durable engineering memory.**

No important architectural conclusion should depend on someone remembering which chat contained it. Chat history may retain nuance, but authoritative engineering state must be reconstructable from repository artifacts and machine evidence.

## Required capture loop

Conversation / incident / experiment
→ extract claims, decisions, hypotheses, constraints, and open questions
→ reconcile with existing documents
→ update the canonical document rather than creating unnecessary parallel notes
→ record material decisions as ADRs
→ link experiments to evidence and findings
→ mark changed conclusions as superseded instead of silently contradicting older text
→ commit and push
→ use the updated state as input to subsequent work.

## Memory layers

1. **Vision and principles** — slow-changing purpose and invariants.
2. **Architecture and ADRs** — current design and why choices were made.
3. **Landscape research** — external systems, papers, projects, and Build/Adopt/Integrate conclusions.
4. **Experiments and evidence** — hypotheses, procedures, raw/generated evidence, findings, and model changes.
5. **Engineering World Model** — machine-readable current relationships among intent, tasks, code, tests, releases, production, and incidents.
6. **Decision/change history** — Git history preserves how the understanding evolved.

## Anti-patterns

- Treating chat summaries as the only memory.
- Creating a new document for every conversation without reconciling existing canonical documents.
- Recording a conclusion without its evidence or confidence.
- Leaving obsolete architecture text looking current.
- Allowing generated dashboards to become more authoritative than their source evidence.
- Calling a task complete before its durable project state is updated.

## Definition of Done extension

For material engineering work, `DONE` requires both implementation/evidence and **memory convergence**: canonical docs, ADRs, model/schema, experiments, and machine state must reflect the new reality.
