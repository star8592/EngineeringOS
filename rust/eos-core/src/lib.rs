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

pub fn claim(item: &mut WorkItem, owner: &str, lease_seconds: i64, now: DateTime<Utc>) -> Result<(), QueueError> {
    if let Some(l) = &item.lease {
        if l.expires_at > now && l.owner != owner {
            return Err(QueueError::LeaseHeld);
        }
    }
    item.owner = Some(owner.to_string());
    item.state = WorkState::InProgress;
    item.lease = Some(Lease { owner: owner.to_string(), acquired_at: now, expires_at: now + Duration::seconds(lease_seconds) });
    Ok(())
}

pub fn renew(item: &mut WorkItem, owner: &str, lease_seconds: i64, now: DateTime<Utc>) -> Result<(), QueueError> {
    match &mut item.lease {
        Some(l) if l.owner == owner && l.expires_at > now => {
            l.expires_at = now + Duration::seconds(lease_seconds);
            Ok(())
        }
        _ => Err(QueueError::LeaseNotOwned),
    }
}

pub fn request_resolution(item: &mut WorkItem, owner: &str, evidence: &[String]) -> Result<(), QueueError> {
    match &item.lease {
        Some(l) if l.owner == owner => {},
        _ => return Err(QueueError::LeaseNotOwned),
    }
    if evidence.is_empty() { return Err(QueueError::EvidenceRequired); }
    item.state = WorkState::PendingResolution;
    item.closure_evidence_refs = evidence.to_vec();
    Ok(())
}

pub fn resolve(item: &mut WorkItem, verifier: &str, evidence: &[String]) -> Result<(), QueueError> {
    if item.state != WorkState::PendingResolution { return Err(QueueError::NotPendingResolution); }
    let mut refs = item.closure_evidence_refs.clone();
    refs.extend_from_slice(evidence);
    refs.sort(); refs.dedup();
    if refs.is_empty() { return Err(QueueError::EvidenceRequired); }
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

    fn t(sec: i64) -> DateTime<Utc> { Utc.timestamp_opt(sec, 0).unwrap() }

    #[test]
    fn unexpired_lease_blocks_second_owner() {
        let mut x = WorkItem::default(); claim(&mut x, "a", 60, t(0)).unwrap();
        assert_eq!(claim(&mut x, "b", 60, t(1)), Err(QueueError::LeaseHeld));
    }

    #[test]
    fn expired_lease_can_be_reclaimed() {
        let mut x = WorkItem::default(); claim(&mut x, "a", 60, t(0)).unwrap(); claim(&mut x, "b", 60, t(61)).unwrap();
        assert_eq!(x.owner.as_deref(), Some("b"));
    }

    #[test]
    fn closure_requires_evidence() {
        let mut x = WorkItem::default(); claim(&mut x, "a", 60, t(0)).unwrap();
        assert_eq!(request_resolution(&mut x, "a", &[]), Err(QueueError::EvidenceRequired));
    }

    #[test]
    fn renew_requires_live_owned_lease() {
        let mut x = WorkItem::default(); claim(&mut x, "a", 60, t(0)).unwrap();
        renew(&mut x, "a", 60, t(30)).unwrap();
        assert_eq!(x.lease.as_ref().unwrap().expires_at, t(90));
        assert_eq!(renew(&mut x, "b", 60, t(31)), Err(QueueError::LeaseNotOwned));
        assert_eq!(renew(&mut x, "a", 60, t(91)), Err(QueueError::LeaseNotOwned));
    }

    #[test]
    fn resolution_preserves_evidence_and_releases_lease() {
        let mut x = WorkItem::default(); claim(&mut x, "a", 60, t(0)).unwrap();
        request_resolution(&mut x, "a", &["ci:1".into()]).unwrap(); resolve(&mut x, "manager", &["runtime:2".into()]).unwrap();
        assert_eq!(x.state, WorkState::Resolved); assert!(x.lease.is_none()); assert_eq!(x.resolution_evidence_refs.len(), 2); assert_eq!(x.resolved_by.as_deref(), Some("manager"));
    }
}
