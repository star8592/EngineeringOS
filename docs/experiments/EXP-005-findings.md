# EXP-005 Initial Findings: DevControl Release Provenance

Date: 2026-10-03

Read-only inspection found that DevControl already has several strong provenance primitives, but they are not yet joined into one durable end-to-end identity chain.

## Existing evidence primitives

1. Package staging exports `DEVCONTROL_GIT_SHA` from the repository HEAD.
2. Built DevControl executables expose product version and build SHA, and `check_package_build_identity.sh` verifies both.
3. Server packages include `SHA256SUMS`; the public Agent archive has a separately published SHA-256 checksum.
4. Production deployment refuses dirty trees and refuses a source HEAD that differs from `origin/main`.
5. Production release orchestration uses a release ID and preserves previous server/Agent release targets for rollback.
6. Successful qualification writes local release evidence under `~/.local/state/devcontrol3/release-evidence/<release>.json`, including qualification time, previous releases, and passed gates.
7. The scheduled Production Smoke reads the live `release_id` from `/readyz`, verifies OAuth/browser/Agent/hygiene gates, and checks the local Agent release matches the live release.
8. Release-manager state tracks `active_release` and `last_known_good_release`.

## Provenance gap

The system currently has the pieces of provenance but no single immutable manifest that binds all of them:

`full source SHA -> product version -> release ID -> server package digest -> Agent package digest -> qualification evidence -> deployed server identity -> deployed Agent identity -> production smoke run`.

The current release ID defaults to a short Git SHA. This is useful operationally but is weaker than preserving the full source SHA plus immutable artifact digests as first-class fields.

GitHub Actions Production Smoke checks the live release ID, but its GitHub run `headSha` describes the workflow checkout, not necessarily the exact deployed source identity. EngineeringOS must not equate those two identities without an explicit evidence edge.

## Architecture consequence

EngineeringOS should ingest existing DevControl evidence rather than inventing a parallel release system. DevControl should eventually emit a signed or otherwise tamper-evident release manifest containing exact source and artifact identities; EngineeringOS should consume that manifest and link external CI/runtime evidence to it.

No deployment changes are made by this experiment.
