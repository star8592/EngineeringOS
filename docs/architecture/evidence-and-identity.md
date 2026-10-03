# Evidence and Identity Model

EngineeringOS must not collapse these states:

- `SOURCE_HEAD`: authoritative source-control state.
- `QUALIFIED_HEAD`: source identity with required deterministic checks passing.
- `ARTIFACT_ID`: immutable built/released artifact identity.
- `DEPLOYED_ID`: artifact/source identity reported by a target environment.
- `PRODUCTION_VERIFIED_ID`: deployed identity with current production evidence.

Transitions require evidence edges. An ancestor relationship is context, not proof that a newer descendant inherited qualification or production verification.

Missing edges are `UNKNOWN`, never implicit `PASS`.
