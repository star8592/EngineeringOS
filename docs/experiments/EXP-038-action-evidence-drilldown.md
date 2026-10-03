# EXP-038: Action Evidence Drill-down

Date: 2026-10-04

The continuous supervisor action brief now carries an evidence drill-down so an operator can move directly from "what needs attention" to the concrete engineering state behind that recommendation.

## Added evidence

For current G2 advisory actions:

- dirty-workspace triage includes branch, worktree path, changed-file count, and changed paths;
- overlapping-line review includes both branches, overlap ratio, and shared paths;
- duplicate-state reconciliation includes exact-head alias groups;
- divergent-development review includes ahead/behind and concern evidence;
- artifact/deployment identity gaps include the current release evidence and the precise unresolved identity reason.

Each detail also provides deterministic suggested-resolution steps while retaining `target_mutation_authorized=false`.

## Live result

The first continuous run with drill-down produced five top actions backed by 22 evidence entries:

- artifact identity: 1 evidence record;
- deployment identity: 1 evidence record;
- overlapping development lines: 6 evidence records;
- dirty workspaces: 11 evidence records;
- duplicate heads: 3 evidence records.

Examples observed in the dirty-workspace evidence included a 10-file active-active Gateway workspace, a 36-file release-supervisor workspace, and a 26-file tool-surface convergence workspace.

The Control Room exposes the same detail at `/runtime/action-details.json` and as expandable read-only evidence sections. Runtime projection remains outside Git and produced no repository dirtiness.

## Result

EngineeringOS now provides a continuously refreshed, evidence-backed operator brief rather than only aggregate project-health counters. This advances the G2 Control Room drill-down criterion without adding any approval or mutation semantics.
