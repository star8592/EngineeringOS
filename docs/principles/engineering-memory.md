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

## Evidence-Calibrated Operational Diagnosis (added 2026-10-09)

An AI developer or operator MUST NOT extrapolate a component-local error into a platform-wide outage, infer code failure from a job that never executed, or prescribe new infrastructure before reconstructing the existing topology.

### Mandatory evidence ladder

1. **Scope**: Record the exact system, tenant/account, repository, branch, commit, workflow, run/job ID, environment and observation time before naming a cause.
2. **Intent versus routing**: Inspect the authoritative configuration at the affected commit (for example, GitHub Actions `runs-on`) rather than relying on chat summaries or another repository's CI status.
3. **Topology**: Inventory existing machines, process/service state, per-project registration, runner labels, credentials boundaries, permissions, and route reachability. A process that is online does not prove it is authorized or eligible for that repository.
4. **Execution**: Distinguish **not scheduled**, **not assigned**, **started**, **tests failed**, **deploy failed** and **production verification failed**. No job assigned (`runner_id=0`) and no steps run cannot be attributed to failing code tests.
5. **Cause with confidence**: Represent `OBSERVED` / `INFERRED` / `UNKNOWN` separately. Mark a root cause `CONFIRMED` only with directly matching logs, annotations, API responses or a reproducible experiment.
6. **Counterevidence**: Before asserting "entire CI is broken," check at least one independent same-platform project or runner pool. Counterexamples must narrow the incident scope.
7. **Minimal reversible repair**: Prefer connecting to healthy existing capabilities over recreating infrastructure. Preserve unrelated project state, isolate new workloads and avoid sharing production secrets or privilege.
8. **Post-remediation closure**: Re-run the failed path; verify the *actual* assigned executor and executed steps. Record test/run evidence, rollback boundary, unresolved risks, and update canonical documents/ADRs. An edited YAML file, running container or registered runner alone is not DONE.

### EngineeringOS automation requirement

Project adapters SHOULD implement a read-only **Reality Check / CI Doctor** diagnostic that materializes the evidence ladder into a structured report with source timestamps and uncertainty, instead of allowing an AI to freely guess the failure domain. CI diagnoses should be tested against adversarial fixtures: wrong workflow runner route, healthy runners scoped to another repository, job with no assigned executor, offline matching runner, quota/budget annotation, and a genuinely failing test step.

### Reference incident

On 2026-10-09, RustContentFactory's `ubuntu-latest` workflow targeted GitHub-hosted runners and GitHub reported a billing/budget block before a job was assigned, while Z890 simultaneously had active repo-scoped self-hosted runners for DevControl2 and Zoryvia. The warranted diagnosis was **repository workflow routing and missing repo runner registration**, not "the entire self-hosted CI fleet is unavailable." The corrective Rust CI Doctor and evidence trail live in `star8592/RustContentFactory` (PR #2, `docs/CI_REALITY_CHECK.md`). Its remote CI remains blocked until a real repo runner executes a green run.
