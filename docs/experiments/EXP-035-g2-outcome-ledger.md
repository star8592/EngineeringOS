# EXP-035: G2 Outcome Ledger

G2 decisions are now retained with later outcome labels rather than silently disappearing when the manager changes its mind.

The former `RESOLVE_PRODUCTION_VERIFICATION` P1 item is recorded as `FALSE_POSITIVE`, with EXP-034, ADR-024, and the evidence-plane artifact as closure evidence. The queue item is resolved through the same evidence-gated closure model used elsewhere.

This ledger is intended to become ground truth for decision precision/recall and System-One judge calibration. Labels require external/deterministic evidence; model self-judgment alone is insufficient.
