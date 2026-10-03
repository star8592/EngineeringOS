namespace EngineeringOS

inductive CommandState where
  | intentRecorded
  | dispatched
  | unknownCompletion
  | notApplied
  | succeeded
  deriving DecidableEq, Repr

inductive RetryDecision where
  | retryAllowed
  | probeRequired
  | doNotRetry
  deriving DecidableEq, Repr

def retryDecision : CommandState → RetryDecision
  | .intentRecorded => .retryAllowed
  | .notApplied => .retryAllowed
  | .dispatched => .probeRequired
  | .unknownCompletion => .probeRequired
  | .succeeded => .doNotRetry

def requiresOutcomeEvidence : CommandState → Bool
  | .notApplied => true
  | .succeeded => true
  | _ => false

theorem dispatched_requires_probe :
    retryDecision .dispatched = .probeRequired := rfl

theorem unknown_completion_requires_probe :
    retryDecision .unknownCompletion = .probeRequired := rfl

theorem succeeded_never_retries :
    retryDecision .succeeded = .doNotRetry := rfl

theorem retry_allowed_only_before_effect_or_after_proven_not_applied
    (s : CommandState)
    (h : retryDecision s = .retryAllowed) :
    s = .intentRecorded ∨ s = .notApplied := by
  cases s <;> simp [retryDecision] at h ⊢

theorem terminal_outcome_requires_evidence
    (s : CommandState)
    (h : s = .succeeded ∨ s = .notApplied) :
    requiresOutcomeEvidence s = true := by
  rcases h with rfl | rfl <;> rfl

end EngineeringOS
