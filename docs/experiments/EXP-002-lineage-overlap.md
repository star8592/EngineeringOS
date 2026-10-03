# EXP-002: DevControl lineage and overlap graph

## Goal

Move from inventory to evidence-backed relationships among concurrent development lines.

## Evidence

- merge-base and ahead/behind against origin/main
- commit containment and patch identity
- changed-file overlap
- exact-head aliases
- attached/detached/locked worktree type
- release/version naming evidence

## Guardrail

No branch will be labeled superseded, safe-to-delete, or safe-to-merge from age/divergence alone. Those are semantic decisions requiring stronger evidence and architecture context.
