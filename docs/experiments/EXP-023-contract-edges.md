# EXP-023: Contract Graph Edges

The project contract graph now supports typed semantic edges: `depends_on`, `generates`, `implements`, `consumes`, `owns`, and `runtime_binding`.

DevControl's profile now expresses packaging -> artifacts, components -> contracts, artifacts -> integrity contracts, and release manifest -> production runtime binding. A generic forward impact closure can therefore identify downstream engineering objects affected by a changed component.

This is the basis for later selective assurance: a changed component should trigger checks because of the contracts/artifacts it impacts, not because a hard-coded script name says so.
