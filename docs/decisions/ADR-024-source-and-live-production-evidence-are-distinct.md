# ADR-024: Source-head and live-production verification are distinct
Status: Accepted

EngineeringOS must not infer live-production verification from current source-head CI/smoke state, nor infer current source deployment from a qualified older/live release.

Source qualification, source-head production verification, live release qualification, deployment identity, and artifact identity are separate predicates with separate evidence authorities.
