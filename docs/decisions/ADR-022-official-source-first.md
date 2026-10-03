# ADR-022: Official sources precede protocol and tool-surface changes
Status: Accepted

For OpenAI, MCP, tool surface, approval, authentication, authorization, and host integration behavior, EngineeringOS must consult current official documentation/specifications before implementation. Secondary implementations and competitors may inform product design but cannot redefine protocol semantics.

Any deliberate divergence from the official baseline must be explicit, scoped, tested, and documented rather than introduced as a workaround.
