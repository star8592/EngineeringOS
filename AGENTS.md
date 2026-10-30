# EngineeringOS · Agent entrypoint

This is the root entrypoint for engineering agents working in this repository.

## Mandatory cross-project access and authentication preflight

**Before touching SSH, remote execution, login/OAuth, browser control, device enrollment, payments, production environment or secret management**, read:

- [Canonical cross-project access and authentication lessons](docs/operations/CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md)
- [Engineering memory principle](docs/principles/engineering-memory.md)
- [ADR-033 — no hard-coded or fabricated business data](docs/decisions/ADR-033-no-hardcoded-or-fabricated-business-data.md)

Do not infer that a prior successful SSH handshake authorizes remote command execution. Confirm the **project-specific** last-known-good host alias and deployment target before any login. Do not copy any private keys/credentials into chats, repository files or logs. A tool-layer denial is not permission to circumvent controls.

This central runbook is one shared protocol, **not** a substitute for narrower project-specific instructions or proof of authorization. Product-specific AGENTS.md rules remain binding; use scoped PRs and actual tests for modifications. After a real incident, update the canonical runbook and relevant regression evidence instead of creating parallel memory files.
