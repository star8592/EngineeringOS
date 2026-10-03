# DevControl Evidence Contract Gap

Current evidence is strong but fragmented. EngineeringOS can resolve live release ID -> qualification record -> unique source commit, but cannot yet prove exact runtime artifact bytes.

Target producer contract:

```text
release_id
full_source_sha
product_version
server_artifact_sha256
agent_artifact_sha256
qualification_evidence_id
qualified_at
deployment_environment
runtime_identity_binding
```

The producer (DevControl release pipeline) owns these facts. EngineeringOS owns ingestion/reconciliation. This avoids tool-surface and responsibility drift.
