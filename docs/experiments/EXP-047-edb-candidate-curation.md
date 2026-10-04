# EXP-047: Shadow observations to EDB candidate curation

Date: 2026-10-04

## Goal

Turn continuously collected System-One shadow observations into a durable, deduplicated review queue without silently promoting weak Scheduler references into benchmark truth.

## Design

The curation layer reads `.engineeringos/runtime/system-one/observations.jsonl` and groups observations by a semantic signature composed of:

- routing contract;
- work kind;
- work reason;
- required assurance;
- automation class.

Repeated supervisor observations of the same engineering semantics collapse into one candidate. Model output is intentionally not part of the semantic signature, so repeated or changed model predictions do not create duplicate benchmark examples.

Each candidate records the weak Scheduler reference, model recommendations/revisions, latest probabilities, observation count, authority-policy result, and source observation ids.

## Safety contract

Generated candidates are always:

- `edb_gold=false`;
- `expected_lane=null`;
- `label_source=null`;
- `authorization=UNAVAILABLE`.

The curation layer cannot adjudicate.

Candidates with missing semantic context are `BLOCKED_INCOMPLETE_CONTEXT`. Candidates with unresolved human-authority policy are `BLOCKED_AUTHORITY_POLICY_UNRESOLVED`.

Priority is deterministic:

1. authority-policy unresolved or model/Scheduler disagreement;
2. A3/A4/A5 high-assurance work;
3. low-confidence model observations;
4. routine examples.

## Runtime integration

The continuous Supervisor now runs curation after observation ingestion and before admission evaluation. Control Room shows candidate count, pending adjudication, blocked candidates, gold labels and the explicit `auto_labeling=false` state.

This creates the data path needed to grow EDB toward the 100-case evidence floor while preserving the distinction between evidence, weak references, and adjudicated truth.
