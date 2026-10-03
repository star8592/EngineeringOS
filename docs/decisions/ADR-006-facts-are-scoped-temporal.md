# ADR-006: Engineering facts are scoped and temporal
Status: Accepted

EngineeringOS will not model project truth as unscoped key/value state. Facts carry scope, provenance, authority, confidence, and time. Two different values are a direct contradiction only when their subject, predicate, scope, and applicable time are compatible.

Cross-scope differences such as source version versus production version are drift/reconciliation problems and require provenance edges; they are not automatically errors.
