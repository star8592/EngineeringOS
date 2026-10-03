# ADR-005: Ingest provenance; do not replace release infrastructure
Status: Accepted

EngineeringOS will not build a parallel DevControl release manager. It will ingest and normalize deterministic provenance from DevControl's existing release pipeline, identify missing identity edges, and require those edges to be emitted by the system that owns the release/deployment action.

This preserves responsibility boundaries: DevControl owns release execution; EngineeringOS owns cross-system engineering state, evidence linkage, assurance, and convergence reasoning.
