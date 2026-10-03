# Evidence and Identity Model

EngineeringOS must not collapse these states:

- `SOURCE_HEAD`: authoritative source-control state.
- `QUALIFIED_HEAD`: source identity with required deterministic checks passing.
- `ARTIFACT_ID`: immutable built/released artifact identity.
- `DEPLOYED_ID`: artifact/source identity reported by a target environment.
- `PRODUCTION_VERIFIED_ID`: deployed identity with current production evidence.

Transitions require evidence edges. An ancestor relationship is context, not proof that a newer descendant inherited qualification or production verification.

Missing edges are `UNKNOWN`, never implicit `PASS`.

## Workflow identity is not deployment identity

A CI/smoke workflow's checkout SHA identifies the code used to execute that workflow. It must not be treated as the deployed source SHA unless the runtime explicitly reports/binds that identity. Production evidence should reference the live release/artifact identity and then link that identity to source provenance.
