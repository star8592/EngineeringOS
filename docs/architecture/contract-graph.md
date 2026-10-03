# Contract Graph

Project profiles may describe engineering semantics as a graph rather than a flat file list.

`domain -> components -> paths/contracts/artifacts`

A contract represents a compatibility or identity obligation. An artifact represents a produced object whose provenance may matter. Components group implementation surfaces. Domains group related engineering concerns.

EngineeringOS core interprets this schema generically. Project profiles own the project-specific graph.

The graph is initially declarative and conservative. Future edges may include `depends_on`, `generates`, `implements`, `consumes`, `owns`, and runtime bindings. Those edges must remain evidence-bearing rather than inferred from names alone.
