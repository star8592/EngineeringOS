---- MODULE CommandTransaction ----
EXTENDS Naturals

CONSTANT MaxAttempts

VARIABLES state, outcomeEvidence, attempts

vars == <<state, outcomeEvidence, attempts>>

States == {
  "INTENT_RECORDED",
  "DISPATCHED",
  "UNKNOWN_COMPLETION",
  "NOT_APPLIED",
  "SUCCEEDED"
}

Init ==
  /\ state = "INTENT_RECORDED"
  /\ outcomeEvidence = FALSE
  /\ attempts = 0

Dispatch ==
  /\ state \in {"INTENT_RECORDED", "NOT_APPLIED"}
  /\ attempts < MaxAttempts
  /\ state' = "DISPATCHED"
  /\ outcomeEvidence' = FALSE
  /\ attempts' = attempts + 1

LoseCompletion ==
  /\ state = "DISPATCHED"
  /\ state' = "UNKNOWN_COMPLETION"
  /\ UNCHANGED <<outcomeEvidence, attempts>>

ConfirmApplied ==
  /\ state \in {"DISPATCHED", "UNKNOWN_COMPLETION"}
  /\ state' = "SUCCEEDED"
  /\ outcomeEvidence' = TRUE
  /\ UNCHANGED attempts

ConfirmNotApplied ==
  /\ state \in {"DISPATCHED", "UNKNOWN_COMPLETION"}
  /\ state' = "NOT_APPLIED"
  /\ outcomeEvidence' = TRUE
  /\ UNCHANGED attempts

Next ==
  \/ Dispatch
  \/ LoseCompletion
  \/ ConfirmApplied
  \/ ConfirmNotApplied

Spec == Init /\ [][Next]_vars

RetryAllowed == state \in {"INTENT_RECORDED", "NOT_APPLIED"}

TypeOK ==
  /\ state \in States
  /\ outcomeEvidence \in BOOLEAN
  /\ attempts \in 0..MaxAttempts

OutcomeEvidenceRequired ==
  state \in {"SUCCEEDED", "NOT_APPLIED"} => outcomeEvidence

NoBlindRetryAfterDispatch ==
  state \in {"DISPATCHED", "UNKNOWN_COMPLETION"} => ~RetryAllowed

RetryFromNotAppliedIsEvidenceBacked ==
  state = "NOT_APPLIED" => outcomeEvidence

AttemptBound == attempts <= MaxAttempts

====
