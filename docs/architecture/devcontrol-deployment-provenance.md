# DevControl Deployment Provenance Observer

EngineeringOS needs to distinguish three different identities:

1. **source identity** — the full Git commit that produced a release;
2. **deployment identity** — the exact bytes currently installed as the production server and local Agent for that release;
3. **build artifact identity** — the immutable staged package/tarball manifest created during release qualification.

These must not be collapsed.

## Read-only deployment binding

For the live DevControl release, EngineeringOS observes:

- public runtime `release_id`;
- unique full Git source SHA matching that release id;
- production server `/opt/devcontrol3/current`;
- local Agent `~/.local/lib/devcontrol3/current`;
- a canonical content digest of each resolved release tree.

The canonical tree digest covers regular-file SHA-256 values and symlink targets in stable relative-path order. It does not mutate the release tree.

A deployment identity is `RESOLVED` only when:

- the release id uniquely prefixes the full source SHA;
- server current release equals the runtime release id;
- Agent current release equals the runtime release id;
- both deployed trees contain files;
- both canonical tree digests are available.

EngineeringOS then creates a deployment binding SHA over:

`release_id + full_source_sha + server_tree_sha256 + agent_tree_sha256`.

The deployment binding is evidence, not an execution token.

## Artifact identity remains separate

DevControl already computes `SHA256SUMS` for staged server and Agent packages, but the successful release workflow currently uses a temporary qualification directory and does not durably persist the original server artifact manifest/tarball digest in release evidence.

Therefore EngineeringOS may resolve **deployment identity** while keeping **artifact identity = PARTIAL**.

Observed deployed-tree digests are not retroactively relabeled as build-artifact digests.

## Authority and failure behavior

The observer is project-specific and read-only:

- local filesystem inspection only for Agent release trees;
- read-only SSH commands for the production server release tree;
- no deployment, restart, cleanup, rollback, or file writes on DevControl;
- SSH or tree-observation failure degrades identity to PARTIAL/UNKNOWN;
- missing evidence never becomes permission to infer a digest.

The generic EngineeringOS core remains free of DevControl host/path semantics.
