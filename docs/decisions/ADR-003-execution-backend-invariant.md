# ADR-003: Execution backend invariant
Status: Accepted

Normal EngineeringOS development and machine operations use DevControl. Other remote-control products may be researched as competitors or references but must not silently become execution dependencies.

Any future backend change requires an explicit architecture decision and evidence. Tool availability alone is not authorization to drift the execution surface.
