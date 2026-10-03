# EXP-022: Project Contract Graph

DevControl's bootstrap semantic-collision profile has been upgraded from flat domain/path sets to a graph-shaped profile containing components, contracts, paths, and artifacts.

For `release_identity`, expansion now reaches source identity, server packaging, Agent packaging, the `release-source-identity` and `artifact-integrity` contracts, and package/checksum artifacts. This gives later collision and provenance logic a shared semantic model without adding DevControl-specific rules to core.
