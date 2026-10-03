# EXP-007: Memory Convergence

## Goal

Detect when engineering reality changes but canonical project memory does not.

## Initial checks

- material architecture/code changes with no corresponding ADR/canonical-doc update;
- accepted ADR contradicted by newer canonical docs or implementation evidence;
- experiment findings that changed the model but were never reconciled into architecture documents;
- unresolved `UNKNOWN` evidence that later became knowable but was not updated;
- documents referring to superseded version/protocol/tool-surface assumptions as current.

## Principle

This is not a documentation-coverage score. It is consistency checking between engineering reality and durable engineering memory.
