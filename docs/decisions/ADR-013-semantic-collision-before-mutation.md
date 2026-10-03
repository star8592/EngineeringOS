# ADR-013: Semantic collision is checked before target mutation
Status: Accepted

A planned mutation may be blocked even with zero exact path overlap when an active development line changes files in the same engineering contract domain. For contract-sensitive work, semantic collision takes precedence over exact-path clearance.

Bootstrap domain maps may be explicit, but long-term domain ownership/dependency metadata belongs to project adapters/manifests, not hard-coded project conditionals in EngineeringOS core.
