use crate::EventEnvelope;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug)]
pub enum StoreError {
    Io(std::io::Error),
    CorruptCompleteRecord,
    SequenceMismatch,
    DuplicateEventId,
    VersionConflict,
    CorruptSnapshot,
    UnsupportedSnapshotSchema,
    SnapshotDigestMismatch,
}
impl From<std::io::Error> for StoreError {
    fn from(e: std::io::Error) -> Self {
        Self::Io(e)
    }
}
impl std::fmt::Display for StoreError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let s = match self {
            Self::Io(_) => "IO_ERROR",
            Self::CorruptCompleteRecord => "CORRUPT_COMPLETE_RECORD",
            Self::SequenceMismatch => "SEQUENCE_MISMATCH",
            Self::DuplicateEventId => "DUPLICATE_EVENT_ID",
            Self::VersionConflict => "VERSION_CONFLICT",
            Self::CorruptSnapshot => "CORRUPT_SNAPSHOT",
            Self::UnsupportedSnapshotSchema => "UNSUPPORTED_SNAPSHOT_SCHEMA",
            Self::SnapshotDigestMismatch => "SNAPSHOT_DIGEST_MISMATCH",
        };
        write!(f, "{s}")
    }
}
impl std::error::Error for StoreError {}

fn decode_complete_lines(data: &[u8]) -> Result<Vec<EventEnvelope>, StoreError> {
    let mut out = Vec::new();
    let mut start = 0usize;
    for i in 0..data.len() {
        if data[i] == b'\n' {
            let raw = &data[start..i];
            start = i + 1;
            if raw.iter().all(|b| b.is_ascii_whitespace()) {
                continue;
            }
            let e = serde_json::from_slice(raw).map_err(|_| StoreError::CorruptCompleteRecord)?;
            out.push(e);
        }
    }
    // bytes after the final newline are a torn final append and are ignored.
    Ok(out)
}

pub fn read_events(path: impl AsRef<Path>) -> Result<Vec<EventEnvelope>, StoreError> {
    let p = path.as_ref();
    if !p.exists() {
        return Ok(vec![]);
    }
    let data = std::fs::read(p)?;
    decode_complete_lines(&data)
}

pub fn current_version(path: impl AsRef<Path>) -> Result<u64, StoreError> {
    Ok(read_events(path)?.last().map(|e| e.seq).unwrap_or(0))
}

pub fn append_event_cas(
    path: impl AsRef<Path>,
    event: &EventEnvelope,
    expected_version: Option<u64>,
) -> Result<(), StoreError> {
    let p = path.as_ref();
    if let Some(parent) = p.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut f = OpenOptions::new()
        .create(true)
        .read(true)
        .append(true)
        .open(p)?;
    f.lock()?;
    let result = (|| {
        f.seek(SeekFrom::Start(0))?;
        let mut data = Vec::new();
        f.read_to_end(&mut data)?;
        let events = decode_complete_lines(&data)?;
        let current = events.last().map(|e| e.seq).unwrap_or(0);
        if expected_version.is_some() && expected_version != Some(current) {
            return Err(StoreError::VersionConflict);
        }
        if event.seq != current + 1 {
            return Err(StoreError::SequenceMismatch);
        }
        let ids: HashSet<&str> = events.iter().map(|e| e.event_id.as_str()).collect();
        if ids.contains(event.event_id.as_str()) {
            return Err(StoreError::DuplicateEventId);
        }
        let mut payload =
            serde_json::to_vec(event).map_err(|_| StoreError::CorruptCompleteRecord)?;
        payload.push(b'\n');
        f.write_all(&payload)?;
        f.sync_all()?;
        Ok(())
    })();
    let _ = f.unlock();
    result
}

fn canonical_json(v: &Value) -> Vec<u8> {
    serde_json::to_vec(v).expect("serializable JSON value")
}
pub fn state_digest(v: &Value) -> String {
    Sha256::digest(canonical_json(v))
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect()
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Snapshot {
    pub schema_version: u64,
    pub last_seq: u64,
    pub state: Value,
    pub state_sha256: String,
}

fn temp_path(p: &Path) -> PathBuf {
    let n = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    let name = format!(
        "{}.{}.{}.tmp",
        p.file_name().and_then(|x| x.to_str()).unwrap_or("snapshot"),
        std::process::id(),
        n
    );
    p.with_file_name(name)
}

pub fn write_snapshot(
    path: impl AsRef<Path>,
    last_seq: u64,
    state: &Value,
) -> Result<Snapshot, StoreError> {
    let p = path.as_ref();
    let parent = p.parent().unwrap_or_else(|| Path::new("."));
    std::fs::create_dir_all(parent)?;
    let body = Snapshot {
        schema_version: 1,
        last_seq,
        state: state.clone(),
        state_sha256: state_digest(state),
    };
    let tmp = temp_path(p);
    {
        let mut f = OpenOptions::new().create_new(true).write(true).open(&tmp)?;
        serde_json::to_writer(&mut f, &body).map_err(|_| StoreError::CorruptSnapshot)?;
        f.write_all(b"\n")?;
        f.sync_all()?;
    }
    std::fs::rename(&tmp, p)?;
    File::open(parent)?.sync_all()?;
    Ok(body)
}

pub fn read_snapshot(path: impl AsRef<Path>) -> Result<Option<Snapshot>, StoreError> {
    let p = path.as_ref();
    if !p.exists() {
        return Ok(None);
    }
    let raw = std::fs::read(p)?;
    let body: Snapshot = serde_json::from_slice(&raw).map_err(|_| StoreError::CorruptSnapshot)?;
    if body.schema_version != 1 {
        return Err(StoreError::UnsupportedSnapshotSchema);
    }
    if body.state_sha256 != state_digest(&body.state) {
        return Err(StoreError::SnapshotDigestMismatch);
    }
    Ok(Some(body))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::fs;
    fn ev(seq: u64, id: &str) -> EventEnvelope {
        EventEnvelope {
            seq,
            event_id: id.into(),
            event_type: "WORK_DISCOVERED".into(),
            payload: json!({"id":"w1"}),
        }
    }
    fn td() -> PathBuf {
        let p = std::env::temp_dir().join(format!(
            "eos-store-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&p).unwrap();
        p
    }
    #[test]
    fn stale_writer_rejected() {
        let d = td();
        let p = d.join("e.jsonl");
        append_event_cas(&p, &ev(1, "e1"), Some(0)).unwrap();
        assert!(matches!(
            append_event_cas(
                &p,
                &EventEnvelope {
                    seq: 2,
                    event_id: "e2".into(),
                    event_type: "WORK_REOPENED".into(),
                    payload: json!({})
                },
                Some(0)
            ),
            Err(StoreError::VersionConflict)
        ));
    }
    #[test]
    fn torn_tail_ignored() {
        let d = td();
        let p = d.join("e.jsonl");
        append_event_cas(&p, &ev(1, "e1"), Some(0)).unwrap();
        let mut f = OpenOptions::new().append(true).open(&p).unwrap();
        f.write_all(b"{\"seq\":2").unwrap();
        assert_eq!(read_events(&p).unwrap().len(), 1);
    }
    #[test]
    fn snapshot_roundtrip_and_digest() {
        let d = td();
        let p = d.join("s.json");
        let s = json!({"state":"IN_PROGRESS","owner":"a"});
        write_snapshot(&p, 3, &s).unwrap();
        let x = read_snapshot(&p).unwrap().unwrap();
        assert_eq!(x.last_seq, 3);
        assert_eq!(x.state, s);
    }
}
