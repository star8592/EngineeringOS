# EXP-009 Initial Findings: Authority and Temporal Reconciliation

Date: 2026-10-03

Live production evidence was ingested without changing DevControl production.

## Observed facts

- `origin/main` source SHA: `790772c8fc0203794ff1c32ad1414dc72be0c897`
- source version at that SHA: `3.1.16`
- public `/readyz`: version `3.1.14`, release ID `3a51151`
- public `/livez`: version `3.1.14`, release ID `3a51151`

`/readyz` and `/livez` agree, so the production runtime observation is internally consistent.

The production release ID uniquely resolves in Git to full SHA `3a51151b8ae2dd56bfabcad680d7c23df19a5e0c`, which is an ancestor of current `origin/main`. The earlier document claim for production 3.1.14 was therefore not stale at this observation time; it matched live runtime reality. The repository is ahead at 3.1.16.

## Reconciliation result

- runtime endpoint consistency: `RESOLVED`
- source vs production version: `DRIFT`
- production release ID -> full source SHA: `RESOLVED`

This is the first end-to-end example where EngineeringOS avoided "fixing" a correct document from a newer repository value and instead used runtime evidence to establish that source and production legitimately differed.

## Remaining gap

The release ID currently resolves through Git prefix matching. This is useful evidence, but the target provenance contract should publish the full source SHA and artifact digests explicitly so identity does not depend on repository lookup or short-SHA uniqueness.
