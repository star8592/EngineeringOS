# EXP-048: Versioned EDB adjudication boundary

Date: 2026-10-04

## Problem

EXP-047 creates useful review candidates from real shadow observations, but a candidate queue alone does not define how benchmark truth is created. Without a single explicit adjudication boundary, model suggestions, Scheduler references, UI actions, or ad-hoc scripts could silently become labels.

## Decision

EngineeringOS now uses a versioned JSONL adjudication ledger:

`benchmarks/edb/adjudications.jsonl`

The ledger is initially empty. No gold labels are invented to bootstrap the system.

A review record must bind the exact candidate id, semantic signature, routing contract, reviewer reference, timestamp, rationale, and evidence references. Accepted records additionally provide the expected processing lane and an allowed gold label source.

## Gold-source policy

Allowed:

- human expert review;
- formal evidence;
- reviewed consensus.

Forbidden as direct gold authority:

- System-One model;
- model-only review;
- weak Scheduler reference;
- Scheduler-only review.

This prevents a model from generating labels used to prove its own quality.

## Runtime behavior

Supervisor runs adjudication after candidate curation. It derives a gold JSONL projection and an adjudication summary. Malformed, stale, duplicate, blocked, or source-invalid records fail closed and are counted as invalid.

Control Room reads the same projection and exposes review-record, gold, pending, and invalid counts. It has no write path.

## Initial state

The versioned adjudication ledger contains zero records, therefore:

- gold count = 0;
- no benchmark truth is synthesized;
- existing candidates remain pending or blocked;
- model routing influence remains disabled.

The next evidence milestone is to adjudicate diverse candidates with explicit provenance until the EDB reaches the admission floor.
