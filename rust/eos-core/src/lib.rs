pub mod storage;
use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Lease {
    pub owner: String,
    pub acquired_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum WorkState {
    Discovered,
    InProgress,
    PendingResolution,
    Resolved,
    Reopened,
    Blocked,
    Superseded,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkItem {
    pub state: WorkState,
    pub owner: Option<String>,
    pub lease: Option<Lease>,
    pub closure_evidence_refs: Vec<String>,
    pub resolution_evidence_refs: Vec<String>,
    pub resolved_by: Option<String>,
}

impl Default for WorkItem {
    fn default() -> Self {
        Self {
            state: WorkState::Discovered,
            owner: None,
            lease: None,
            closure_evidence_refs: vec![],
            resolution_evidence_refs: vec![],
            resolved_by: None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum QueueError {
    LeaseHeld,
    LeaseNotOwned,
    EvidenceRequired,
    NotPendingResolution,
}

pub fn claim(
    item: &mut WorkItem,
    owner: &str,
    lease_seconds: i64,
    now: DateTime<Utc>,
) -> Result<(), QueueError> {
    if let Some(l) = &item.lease {
        if l.expires_at > now && l.owner != owner {
            return Err(QueueError::LeaseHeld);
        }
    }
    item.owner = Some(owner.to_string());
    item.state = WorkState::InProgress;
    item.lease = Some(Lease {
        owner: owner.to_string(),
        acquired_at: now,
        expires_at: now + Duration::seconds(lease_seconds),
    });
    Ok(())
}

pub fn renew(
    item: &mut WorkItem,
    owner: &str,
    lease_seconds: i64,
    now: DateTime<Utc>,
) -> Result<(), QueueError> {
    match &mut item.lease {
        Some(l) if l.owner == owner && l.expires_at > now => {
            l.expires_at = now + Duration::seconds(lease_seconds);
            Ok(())
        }
        _ => Err(QueueError::LeaseNotOwned),
    }
}

pub fn request_resolution(
    item: &mut WorkItem,
    owner: &str,
    evidence: &[String],
) -> Result<(), QueueError> {
    match &item.lease {
        Some(l) if l.owner == owner => {}
        _ => return Err(QueueError::LeaseNotOwned),
    }
    if evidence.is_empty() {
        return Err(QueueError::EvidenceRequired);
    }
    item.state = WorkState::PendingResolution;
    item.closure_evidence_refs = evidence.to_vec();
    Ok(())
}

pub fn resolve(item: &mut WorkItem, verifier: &str, evidence: &[String]) -> Result<(), QueueError> {
    if item.state != WorkState::PendingResolution {
        return Err(QueueError::NotPendingResolution);
    }
    let mut refs = item.closure_evidence_refs.clone();
    refs.extend_from_slice(evidence);
    refs.sort();
    refs.dedup();
    if refs.is_empty() {
        return Err(QueueError::EvidenceRequired);
    }
    item.state = WorkState::Resolved;
    item.resolution_evidence_refs = refs;
    item.resolved_by = Some(verifier.to_string());
    item.lease = None;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;

    fn t(sec: i64) -> DateTime<Utc> {
        Utc.timestamp_opt(sec, 0).unwrap()
    }

    #[test]
    fn unexpired_lease_blocks_second_owner() {
        let mut x = WorkItem::default();
        claim(&mut x, "a", 60, t(0)).unwrap();
        assert_eq!(claim(&mut x, "b", 60, t(1)), Err(QueueError::LeaseHeld));
    }

    #[test]
    fn expired_lease_can_be_reclaimed() {
        let mut x = WorkItem::default();
        claim(&mut x, "a", 60, t(0)).unwrap();
        claim(&mut x, "b", 60, t(61)).unwrap();
        assert_eq!(x.owner.as_deref(), Some("b"));
    }

    #[test]
    fn closure_requires_evidence() {
        let mut x = WorkItem::default();
        claim(&mut x, "a", 60, t(0)).unwrap();
        assert_eq!(
            request_resolution(&mut x, "a", &[]),
            Err(QueueError::EvidenceRequired)
        );
    }

    #[test]
    fn renew_requires_live_owned_lease() {
        let mut x = WorkItem::default();
        claim(&mut x, "a", 60, t(0)).unwrap();
        renew(&mut x, "a", 60, t(30)).unwrap();
        assert_eq!(x.lease.as_ref().unwrap().expires_at, t(90));
        assert_eq!(
            renew(&mut x, "b", 60, t(31)),
            Err(QueueError::LeaseNotOwned)
        );
        assert_eq!(
            renew(&mut x, "a", 60, t(91)),
            Err(QueueError::LeaseNotOwned)
        );
    }

    #[test]
    fn resolution_preserves_evidence_and_releases_lease() {
        let mut x = WorkItem::default();
        claim(&mut x, "a", 60, t(0)).unwrap();
        request_resolution(&mut x, "a", &["ci:1".into()]).unwrap();
        resolve(&mut x, "manager", &["runtime:2".into()]).unwrap();
        assert_eq!(x.state, WorkState::Resolved);
        assert!(x.lease.is_none());
        assert_eq!(x.resolution_evidence_refs.len(), 2);
        assert_eq!(x.resolved_by.as_deref(), Some("manager"));
    }
}

// --- Dependency graph + scheduler parity core ---
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulerItem {
    pub id: String,
    pub state: String,
    #[serde(default)]
    pub depends_on: Vec<String>,
    #[serde(default = "default_automation")]
    pub automation: String,
    #[serde(default = "default_assurance")]
    pub required_assurance: String,
    #[serde(default)]
    pub lease: Option<Lease>,
}
fn default_automation() -> String {
    "REVIEW".into()
}
fn default_assurance() -> String {
    "A1".into()
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DependencyError {
    pub kind: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub item: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub dependency: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub path: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Readiness {
    pub state: String,
    pub blocked_by: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ScheduleDecision {
    pub id: String,
    pub schedule_state: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub blocked_by: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub lane: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub required_assurance: Option<String>,
}

pub fn validate_dependencies(items: &[SchedulerItem]) -> Vec<DependencyError> {
    let ids: HashSet<&str> = items.iter().map(|x| x.id.as_str()).collect();
    let mut errors = Vec::new();
    for x in items {
        for d in &x.depends_on {
            if !ids.contains(d.as_str()) {
                errors.push(DependencyError {
                    kind: "MISSING_DEPENDENCY".into(),
                    item: Some(x.id.clone()),
                    dependency: Some(d.clone()),
                    path: vec![],
                });
            }
            if d == &x.id {
                errors.push(DependencyError {
                    kind: "SELF_DEPENDENCY".into(),
                    item: Some(x.id.clone()),
                    dependency: Some(d.clone()),
                    path: vec![],
                });
            }
        }
    }
    let graph: HashMap<&str, Vec<&str>> = items
        .iter()
        .map(|x| {
            (
                x.id.as_str(),
                x.depends_on
                    .iter()
                    .filter_map(|d| ids.contains(d.as_str()).then_some(d.as_str()))
                    .collect(),
            )
        })
        .collect();
    let mut visiting: HashSet<String> = HashSet::new();
    let mut done: HashSet<String> = HashSet::new();
    fn dfs(
        node: &str,
        graph: &HashMap<&str, Vec<&str>>,
        visiting: &mut HashSet<String>,
        done: &mut HashSet<String>,
        path: &mut Vec<String>,
        errors: &mut Vec<DependencyError>,
    ) {
        if visiting.contains(node) {
            let mut p = path.clone();
            p.push(node.to_string());
            errors.push(DependencyError {
                kind: "DEPENDENCY_CYCLE".into(),
                item: None,
                dependency: None,
                path: p,
            });
            return;
        }
        if done.contains(node) {
            return;
        }
        visiting.insert(node.to_string());
        path.push(node.to_string());
        if let Some(deps) = graph.get(node) {
            for d in deps {
                dfs(d, graph, visiting, done, path, errors);
            }
        }
        path.pop();
        visiting.remove(node);
        done.insert(node.to_string());
    }
    for x in items {
        let mut path = Vec::new();
        dfs(
            &x.id,
            &graph,
            &mut visiting,
            &mut done,
            &mut path,
            &mut errors,
        );
    }
    errors
}

pub fn dependency_readiness(
    item: &SchedulerItem,
    by_id: &HashMap<String, SchedulerItem>,
) -> Readiness {
    let blocked_by: Vec<String> = item
        .depends_on
        .iter()
        .filter(|d| match by_id.get(*d) {
            Some(dep) => dep.state != "RESOLVED" && dep.state != "SUPERSEDED",
            None => true,
        })
        .cloned()
        .collect();
    if !blocked_by.is_empty() {
        return Readiness {
            state: "BLOCKED".into(),
            blocked_by,
        };
    }
    if item.state == "DISCOVERED" || item.state == "REOPENED" {
        return Readiness {
            state: "READY".into(),
            blocked_by: vec![],
        };
    }
    Readiness {
        state: if item.state.is_empty() {
            "UNKNOWN".into()
        } else {
            item.state.clone()
        },
        blocked_by: vec![],
    }
}

pub fn schedule_at(items: &[SchedulerItem], now: DateTime<Utc>) -> Vec<ScheduleDecision> {
    let by_id: HashMap<String, SchedulerItem> =
        items.iter().map(|x| (x.id.clone(), x.clone())).collect();
    items
        .iter()
        .map(|x| {
            let r = dependency_readiness(x, &by_id);
            if r.state != "READY" {
                return ScheduleDecision {
                    id: x.id.clone(),
                    schedule_state: r.state,
                    blocked_by: r.blocked_by,
                    lane: None,
                    required_assurance: None,
                };
            }
            if x.lease
                .as_ref()
                .map(|l| l.expires_at > now)
                .unwrap_or(false)
            {
                return ScheduleDecision {
                    id: x.id.clone(),
                    schedule_state: "LEASED".into(),
                    blocked_by: vec![],
                    lane: None,
                    required_assurance: None,
                };
            }
            let lane = if x.automation == "BLOCK_UNTIL_RESOLVED" {
                "POLICY_GATE"
            } else if matches!(x.required_assurance.as_str(), "A3" | "A4" | "A5") {
                "FORMAL_OR_HIGH_ASSURANCE"
            } else if x.automation == "DETERMINISTIC" {
                "DETERMINISTIC"
            } else {
                "REASONING_REVIEW"
            };
            ScheduleDecision {
                id: x.id.clone(),
                schedule_state: "DISPATCHABLE".into(),
                blocked_by: vec![],
                lane: Some(lane.into()),
                required_assurance: Some(x.required_assurance.clone()),
            }
        })
        .collect()
}

#[cfg(test)]
mod scheduler_tests {
    use super::*;
    use chrono::TimeZone;
    fn t(sec: i64) -> DateTime<Utc> {
        Utc.timestamp_opt(sec, 0).unwrap()
    }
    fn item(
        id: &str,
        state: &str,
        deps: &[&str],
        automation: &str,
        assurance: &str,
    ) -> SchedulerItem {
        SchedulerItem {
            id: id.into(),
            state: state.into(),
            depends_on: deps.iter().map(|x| x.to_string()).collect(),
            automation: automation.into(),
            required_assurance: assurance.into(),
            lease: None,
        }
    }
    #[test]
    fn dependency_blocks_until_resolved() {
        let a = item("a", "DISCOVERED", &["b"], "REVIEW", "A1");
        let b = item("b", "DISCOVERED", &[], "REVIEW", "A1");
        let by = [a.clone(), b.clone()]
            .into_iter()
            .map(|x| (x.id.clone(), x))
            .collect();
        assert_eq!(dependency_readiness(&a, &by).state, "BLOCKED");
    }
    #[test]
    fn dependency_cycle_detected() {
        let c = item("c", "DISCOVERED", &["d"], "REVIEW", "A1");
        let d = item("d", "DISCOVERED", &["c"], "REVIEW", "A1");
        assert!(
            validate_dependencies(&[c, d])
                .iter()
                .any(|e| e.kind == "DEPENDENCY_CYCLE")
        );
    }
    #[test]
    fn deterministic_lane_selected() {
        let a = item("a", "DISCOVERED", &[], "DETERMINISTIC", "A1");
        assert_eq!(
            schedule_at(&[a], t(0))[0].lane.as_deref(),
            Some("DETERMINISTIC")
        );
    }
    #[test]
    fn high_assurance_precedes_determinism() {
        let a = item("a", "DISCOVERED", &[], "DETERMINISTIC", "A4");
        assert_eq!(
            schedule_at(&[a], t(0))[0].lane.as_deref(),
            Some("FORMAL_OR_HIGH_ASSURANCE")
        );
    }
    #[test]
    fn policy_gate_precedes_assurance() {
        let a = item("a", "DISCOVERED", &[], "BLOCK_UNTIL_RESOLVED", "A5");
        assert_eq!(
            schedule_at(&[a], t(0))[0].lane.as_deref(),
            Some("POLICY_GATE")
        );
    }
}

// --- Append-only event replay parity core ---
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventEnvelope {
    pub seq: u64,
    pub event_id: String,
    #[serde(rename = "type")]
    pub event_type: String,
    #[serde(default)]
    pub payload: serde_json::Value,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]
pub struct ReplayLease {
    pub owner: String,
    pub acquired_at: String,
    pub expires_at: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]
pub struct ReplayState {
    pub id: Option<String>,
    pub state: Option<String>,
    pub owner: Option<String>,
    pub lease: Option<ReplayLease>,
    #[serde(default)]
    pub closure_evidence_refs: Vec<String>,
    #[serde(default)]
    pub resolution_evidence_refs: Vec<String>,
    pub resolved_by: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReplayError {
    DuplicateEventId,
    SequenceGapOrReorder,
    WorkAlreadyExists,
    WorkNotCreated,
    LeaseNotOwned,
    EvidenceRequired,
    UnknownEventType,
}

fn payload_str<'a>(p: &'a serde_json::Value, k: &str) -> &'a str {
    p.get(k).and_then(|v| v.as_str()).unwrap_or("")
}
fn payload_strings(p: &serde_json::Value, k: &str) -> Vec<String> {
    p.get(k)
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|v| v.as_str().map(str::to_string))
                .collect()
        })
        .unwrap_or_default()
}

pub fn replay_events(events: &[EventEnvelope]) -> Result<ReplayState, ReplayError> {
    let mut s = ReplayState::default();
    let mut expected = 1u64;
    let mut seen = HashSet::new();
    for e in events {
        if !seen.insert(e.event_id.clone()) {
            return Err(ReplayError::DuplicateEventId);
        }
        if e.seq != expected {
            return Err(ReplayError::SequenceGapOrReorder);
        }
        expected += 1;
        match e.event_type.as_str() {
            "WORK_DISCOVERED" => {
                if s.id.is_some() {
                    return Err(ReplayError::WorkAlreadyExists);
                }
                s.id = Some(payload_str(&e.payload, "id").to_string());
                s.state = Some("DISCOVERED".into());
            }
            _ if s.id.is_none() => return Err(ReplayError::WorkNotCreated),
            "LEASE_CLAIMED" => {
                let owner = payload_str(&e.payload, "owner").to_string();
                s.state = Some("IN_PROGRESS".into());
                s.owner = Some(owner.clone());
                s.lease = Some(ReplayLease {
                    owner,
                    acquired_at: payload_str(&e.payload, "acquired_at").into(),
                    expires_at: payload_str(&e.payload, "expires_at").into(),
                });
            }
            "LEASE_RENEWED" => {
                let owner = payload_str(&e.payload, "owner");
                match &mut s.lease {
                    Some(l) if l.owner == owner => {
                        l.expires_at = payload_str(&e.payload, "expires_at").into()
                    }
                    _ => return Err(ReplayError::LeaseNotOwned),
                }
            }
            "RESOLUTION_REQUESTED" => {
                let refs = payload_strings(&e.payload, "evidence_refs");
                if refs.is_empty() {
                    return Err(ReplayError::EvidenceRequired);
                }
                s.state = Some("PENDING_RESOLUTION".into());
                s.closure_evidence_refs = refs;
            }
            "WORK_RESOLVED" => {
                let mut refs = s.closure_evidence_refs.clone();
                refs.extend(payload_strings(&e.payload, "evidence_refs"));
                let mut dedup = Vec::new();
                for r in refs {
                    if !dedup.contains(&r) {
                        dedup.push(r)
                    }
                }
                if dedup.is_empty() {
                    return Err(ReplayError::EvidenceRequired);
                }
                s.state = Some("RESOLVED".into());
                s.resolved_by = Some(payload_str(&e.payload, "verifier").into());
                s.resolution_evidence_refs = dedup;
                s.lease = None;
            }
            "WORK_REOPENED" => {
                s.state = Some("REOPENED".into());
                s.resolved_by = None;
                s.resolution_evidence_refs.clear();
            }
            _ => return Err(ReplayError::UnknownEventType),
        }
    }
    Ok(s)
}

#[cfg(test)]
mod event_replay_tests {
    use super::*;
    use serde_json::json;
    fn ev(seq: u64, id: &str, t: &str, p: serde_json::Value) -> EventEnvelope {
        EventEnvelope {
            seq,
            event_id: id.into(),
            event_type: t.into(),
            payload: p,
        }
    }
    #[test]
    fn replay_recovers_resolved_state() {
        let e = vec![
            ev(1, "e1", "WORK_DISCOVERED", json!({"id":"w1"})),
            ev(
                2,
                "e2",
                "LEASE_CLAIMED",
                json!({"owner":"a","acquired_at":"t0","expires_at":"t1"}),
            ),
            ev(
                3,
                "e3",
                "RESOLUTION_REQUESTED",
                json!({"evidence_refs":["ci:1"]}),
            ),
            ev(
                4,
                "e4",
                "WORK_RESOLVED",
                json!({"verifier":"manager","evidence_refs":["runtime:2"]}),
            ),
        ];
        let s = replay_events(&e).unwrap();
        assert_eq!(s.state.as_deref(), Some("RESOLVED"));
        assert!(s.lease.is_none());
        assert_eq!(s.resolution_evidence_refs, vec!["ci:1", "runtime:2"]);
    }
    #[test]
    fn sequence_gap_is_rejected() {
        let e = vec![
            ev(1, "e1", "WORK_DISCOVERED", json!({"id":"w1"})),
            ev(3, "e3", "WORK_REOPENED", json!({})),
        ];
        assert_eq!(replay_events(&e), Err(ReplayError::SequenceGapOrReorder));
    }
    #[test]
    fn duplicate_event_is_rejected() {
        let e = vec![
            ev(1, "e1", "WORK_DISCOVERED", json!({"id":"w1"})),
            ev(2, "e1", "WORK_REOPENED", json!({})),
        ];
        assert_eq!(replay_events(&e), Err(ReplayError::DuplicateEventId));
    }
    #[test]
    fn resolved_work_can_reopen() {
        let e = vec![
            ev(1, "e1", "WORK_DISCOVERED", json!({"id":"w1"})),
            ev(
                2,
                "e2",
                "LEASE_CLAIMED",
                json!({"owner":"a","acquired_at":"t0","expires_at":"t1"}),
            ),
            ev(
                3,
                "e3",
                "RESOLUTION_REQUESTED",
                json!({"evidence_refs":["ci:1"]}),
            ),
            ev(
                4,
                "e4",
                "WORK_RESOLVED",
                json!({"verifier":"m","evidence_refs":[]}),
            ),
            ev(5, "e5", "WORK_REOPENED", json!({})),
        ];
        assert_eq!(
            replay_events(&e).unwrap().state.as_deref(),
            Some("REOPENED")
        );
    }
}

// --- Command transaction boundary parity core ---
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CommandReplayState {
    pub command_id: String,
    pub idempotency_key: String,
    pub action_kind: String,
    pub side_effecting: bool,
    pub state: String,
    pub attempts: u64,
    #[serde(default)]
    pub evidence_refs: Vec<String>,
    pub outcome: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CommandReplayError {
    CommandAlreadyExists,
    CommandNotFound,
    OutcomeEvidenceRequired,
    UnknownCommandEvent,
}

pub fn replay_command_events(
    events: &[EventEnvelope],
    command_id: &str,
) -> Result<Option<CommandReplayState>, CommandReplayError> {
    let mut s: Option<CommandReplayState> = None;
    for e in events {
        let p = &e.payload;
        if payload_str(p, "command_id") != command_id {
            continue;
        }
        match e.event_type.as_str() {
            "COMMAND_INTENT_RECORDED" => {
                if s.is_some() {
                    return Err(CommandReplayError::CommandAlreadyExists);
                }
                s = Some(CommandReplayState {
                    command_id: command_id.to_string(),
                    idempotency_key: payload_str(p, "idempotency_key").into(),
                    action_kind: payload_str(p, "action_kind").into(),
                    side_effecting: p
                        .get("side_effecting")
                        .and_then(|v| v.as_bool())
                        .unwrap_or(true),
                    state: "INTENT_RECORDED".into(),
                    attempts: 0,
                    evidence_refs: vec![],
                    outcome: None,
                });
            }
            _ if s.is_none() => return Err(CommandReplayError::CommandNotFound),
            "COMMAND_DISPATCHED" => {
                let x = s.as_mut().unwrap();
                x.state = "DISPATCHED".into();
                x.attempts += 1;
            }
            "COMMAND_COMPLETION_UNKNOWN" => s.as_mut().unwrap().state = "UNKNOWN_COMPLETION".into(),
            "COMMAND_EFFECT_CONFIRMED" => {
                let refs = payload_strings(p, "evidence_refs");
                if refs.is_empty() {
                    return Err(CommandReplayError::OutcomeEvidenceRequired);
                }
                let x = s.as_mut().unwrap();
                for r in refs {
                    if !x.evidence_refs.contains(&r) {
                        x.evidence_refs.push(r);
                    }
                }
                x.state = "SUCCEEDED".into();
                x.outcome = Some("APPLIED".into());
            }
            "COMMAND_EFFECT_NOT_APPLIED" => {
                let refs = payload_strings(p, "evidence_refs");
                if refs.is_empty() {
                    return Err(CommandReplayError::OutcomeEvidenceRequired);
                }
                let x = s.as_mut().unwrap();
                for r in refs {
                    if !x.evidence_refs.contains(&r) {
                        x.evidence_refs.push(r);
                    }
                }
                x.state = "NOT_APPLIED".into();
                x.outcome = Some("NOT_APPLIED".into());
            }
            "COMMAND_FAILED_PRE_EFFECT" => s.as_mut().unwrap().state = "FAILED_PRE_EFFECT".into(),
            _ => return Err(CommandReplayError::UnknownCommandEvent),
        }
    }
    Ok(s)
}

pub fn command_retry_decision(state: Option<&CommandReplayState>) -> &'static str {
    let Some(s) = state else {
        return "NO_COMMAND";
    };
    if !s.side_effecting {
        return if s.state == "SUCCEEDED" {
            "DO_NOT_RETRY"
        } else {
            "RETRY_ALLOWED"
        };
    }
    match s.state.as_str() {
        "INTENT_RECORDED" | "FAILED_PRE_EFFECT" | "NOT_APPLIED" => "RETRY_ALLOWED",
        "SUCCEEDED" => "DO_NOT_RETRY",
        "DISPATCHED" | "UNKNOWN_COMPLETION" => "PROBE_REQUIRED",
        _ => "PROBE_REQUIRED",
    }
}

#[cfg(test)]
mod command_replay_tests {
    use super::*;
    use serde_json::json;
    fn ev(seq: u64, id: &str, t: &str, p: serde_json::Value) -> EventEnvelope {
        EventEnvelope {
            seq,
            event_id: id.into(),
            event_type: t.into(),
            payload: p,
        }
    }
    #[test]
    fn dispatched_side_effect_requires_probe() {
        let e = vec![
            ev(
                1,
                "e1",
                "COMMAND_INTENT_RECORDED",
                json!({"command_id":"c1","idempotency_key":"k1","action_kind":"DEPLOY","side_effecting":true}),
            ),
            ev(2, "e2", "COMMAND_DISPATCHED", json!({"command_id":"c1"})),
        ];
        let s = replay_command_events(&e, "c1").unwrap().unwrap();
        assert_eq!(command_retry_decision(Some(&s)), "PROBE_REQUIRED");
    }
    #[test]
    fn proven_not_applied_allows_retry() {
        let e = vec![
            ev(
                1,
                "e1",
                "COMMAND_INTENT_RECORDED",
                json!({"command_id":"c1","idempotency_key":"k1","action_kind":"DEPLOY","side_effecting":true}),
            ),
            ev(2, "e2", "COMMAND_DISPATCHED", json!({"command_id":"c1"})),
            ev(
                3,
                "e3",
                "COMMAND_EFFECT_NOT_APPLIED",
                json!({"command_id":"c1","evidence_refs":["probe:none"]}),
            ),
        ];
        let s = replay_command_events(&e, "c1").unwrap().unwrap();
        assert_eq!(command_retry_decision(Some(&s)), "RETRY_ALLOWED");
    }
    #[test]
    fn confirmed_applied_never_retries() {
        let e = vec![
            ev(
                1,
                "e1",
                "COMMAND_INTENT_RECORDED",
                json!({"command_id":"c1","idempotency_key":"k1","action_kind":"DEPLOY","side_effecting":true}),
            ),
            ev(2, "e2", "COMMAND_DISPATCHED", json!({"command_id":"c1"})),
            ev(
                3,
                "e3",
                "COMMAND_EFFECT_CONFIRMED",
                json!({"command_id":"c1","evidence_refs":["runtime:r1"]}),
            ),
        ];
        let s = replay_command_events(&e, "c1").unwrap().unwrap();
        assert_eq!(s.outcome.as_deref(), Some("APPLIED"));
        assert_eq!(command_retry_decision(Some(&s)), "DO_NOT_RETRY");
    }
    #[test]
    fn outcome_requires_evidence() {
        let e = vec![
            ev(
                1,
                "e1",
                "COMMAND_INTENT_RECORDED",
                json!({"command_id":"c1","idempotency_key":"k1","action_kind":"DEPLOY","side_effecting":true}),
            ),
            ev(
                2,
                "e2",
                "COMMAND_EFFECT_CONFIRMED",
                json!({"command_id":"c1","evidence_refs":[]}),
            ),
        ];
        assert_eq!(
            replay_command_events(&e, "c1"),
            Err(CommandReplayError::OutcomeEvidenceRequired)
        );
    }
}
