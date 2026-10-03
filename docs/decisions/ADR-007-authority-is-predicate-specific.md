# ADR-007: Authority is predicate- and scope-specific
Status: Accepted

EngineeringOS resolves facts using authority appropriate to the question. `origin/main` is authoritative for current source state; a live runtime endpoint is authoritative for what that environment reports it is running; CI is authoritative for its check result; release manifests should be authoritative for artifact provenance.

A higher/newer source version does not invalidate a lower production version. Their difference is deployment drift until provenance and deployment policy say otherwise.
