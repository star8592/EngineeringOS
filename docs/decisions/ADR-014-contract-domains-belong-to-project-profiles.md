# ADR-014: Contract domains belong to project profiles
Status: Accepted

Semantic collision knowledge is project metadata, not EngineeringOS core logic. Core consumes a generic contract-domain manifest; project profiles declare domain names, paths, and eventually richer dependency/ownership edges.

This removes the bootstrap DevControl domain dictionary from core and preserves G1 genericity.
