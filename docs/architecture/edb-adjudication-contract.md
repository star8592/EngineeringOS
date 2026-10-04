# EDB Adjudication Contract

EngineeringOS treats System-One shadow observations, EDB candidates, and benchmark gold labels as three different evidence classes.

## Evidence classes

1. **Shadow observation** — runtime evidence from an open System-One backend plus deterministic project/scheduler context. It is never benchmark truth.
2. **EDB candidate** — a deduplicated review item produced deterministically from observations. It remains `edb_gold=false`.
3. **Gold EDB row** — a derived benchmark row created only from a valid, versioned adjudication record bound to the exact candidate semantics.

## Versioned adjudication ledger

The source of adjudication truth is:

`benchmarks/edb/adjudications.jsonl`

Each record must bind:

- `candidate_id`;
- `semantic_signature`;
- `routing_contract`;
- `decision`;
- `reviewer_ref`;
- `reviewed_at`;
- `rationale`;
- one or more `evidence_refs`.

For `ACCEPT_GOLD`, the record must also provide an `expected_lane` and an allowed `label_source`.

## Allowed gold sources

- `HUMAN_EXPERT`
- `FORMAL_EVIDENCE`
- `REVIEWED_CONSENSUS`

The following cannot directly create gold:

- System-One model output;
- model-only review;
- weak Scheduler reference;
- Scheduler-only review.

These sources may be evidence presented to an adjudicator, but they cannot be the adjudication authority.

## Fail-closed semantics

A record is invalid and produces no gold when:

- candidate id is absent;
- semantic signature or routing contract does not match;
- candidate is blocked or already gold;
- expected lane is invalid;
- review provenance is incomplete;
- duplicate adjudications exist for one candidate;
- a reject decision carries a label;
- a forbidden gold source is used.

Invalid records remain visible in the adjudication summary. They do not mutate candidates or benchmark output.

## Runtime projection

The Supervisor derives:

- `.engineeringos/runtime/system-one/edb-gold.jsonl`
- `.engineeringos/runtime/system-one/edb-adjudication-summary.json`

Control Room may display these projections but cannot create or mutate adjudication records. There is no dashboard-only approval or labeling path.

## Authorization boundary

EDB adjudication affects benchmark truth only. It does not authorize execution, change project human-authority policy, or lower deterministic/formal assurance gates.
