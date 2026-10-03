# Provenance Chain

A release is a graph of immutable identities, not a version string.

Minimum target chain:

`SOURCE_SHA_FULL`
→ `PRODUCT_VERSION`
→ `RELEASE_ID`
→ `SERVER_ARTIFACT_SHA256`
→ `AGENT_ARTIFACT_SHA256`
→ `QUALIFICATION_EVIDENCE_ID`
→ `DEPLOYED_SERVER_ID`
→ `DEPLOYED_AGENT_ID`
→ `PRODUCTION_SMOKE_EVIDENCE_ID`.

Every arrow requires explicit evidence. Similar names, ancestry, timestamps, or a successful workflow on another SHA are not identity proof.

## Ingestion before invention

EngineeringOS should first normalize provenance already emitted by target projects. It should not become a second release manager. Missing evidence contracts should be added at the producing system boundary, then ingested into the World Model.
