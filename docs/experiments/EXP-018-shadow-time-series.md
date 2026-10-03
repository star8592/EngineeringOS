# EXP-018: Shadow Time Series and Decision Evaluation

## Goal

Turn repeated G2 observations into an evaluation dataset for EngineeringOS decisions.

For each run retain:
- exact observation/source/runtime identities;
- manager/queue/dispatch outputs;
- stable content digest;
- subsequent engineering outcome;
- whether findings persisted, resolved, reopened, or were false positives;
- eventual closure evidence.

This time series will support precision/recall and calibration evaluation for future System-One judges. Training labels must preferentially derive from later deterministic evidence and confirmed outcomes, not from the model judging its own earlier judgment.
