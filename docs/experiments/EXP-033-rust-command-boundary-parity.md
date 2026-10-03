# EXP-033: Rust Command Boundary Parity

The durable command transaction boundary now has a Rust implementation in `eos-core` and is tested against the same event stream used by the Python research implementation.

Parity stages cover:
- durable intent recorded -> retry allowed before dispatch;
- dispatched side effect -> probe required;
- unknown completion -> probe required;
- proven not applied -> retry allowed;
- confirmed applied -> do not retry.

Rust also independently verifies that applied/not-applied outcomes require evidence.

Result: 21 Rust unit tests pass and 10 command Python↔Rust parity assertions pass. The command boundary is therefore migration-eligible but Python remains the reference research implementation until the integrated control loop is exercised in shadow mode.
