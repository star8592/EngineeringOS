# ADR-016: Rust migration requires executable semantic parity
Status: Accepted

A stable EngineeringOS behavior may move from Python research code to Rust control-plane code only when executable parity tests demonstrate equivalent externally relevant semantics.

A successful Rust compile is insufficient. Migration requires:
1. source-layer invariants remain green;
2. Rust-layer invariants are green;
3. cross-language scenario outputs agree on the contract fields;
4. any intentional semantic difference is recorded as a contract/version change rather than hidden inside the rewrite.
