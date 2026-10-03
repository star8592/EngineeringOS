# EXP-005: Release and deployment provenance

Read-only investigation of how DevControl records build, release, deployment, and live production identity.

Questions:
- What immutable identifier is attached to a built artifact?
- Can deployment report the exact source/artifact identity it is running?
- Can production smoke bind its result to that exact identity?
- Where is release history durably recorded if GitHub Releases is not used?
- Can rollback targets be reconstructed from evidence rather than operator memory?

No deployment is triggered by this experiment.
