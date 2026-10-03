# ADR-023: Project policy and host approval are distinct; approval has one authority
Status: Accepted

EngineeringOS policy may return `ALLOW`, `DENY`, or `REQUIRE_HOST_APPROVAL`. It does not implement a parallel approval UI/state machine.

When approval is required, the host/tool protocol owns collection and resumption of that approval. The Control Room may display pending approval state but must not manufacture an independent approval decision.

Tool annotations are classification hints only. They cannot authorize an action. A tool or UI surface must not silently widen approval, authentication, filesystem, network, or execution permissions.
