use chrono::{TimeZone,Utc};
use eos_core::{claim,renew,request_resolution,resolve,WorkItem};
use serde_json::json;
fn t(sec:i64)->chrono::DateTime<Utc>{Utc.timestamp_opt(sec,0).unwrap()}
fn main(){
 let mut x=WorkItem::default();
 claim(&mut x,"agent-a",60,t(0)).unwrap();
 renew(&mut x,"agent-a",60,t(30)).unwrap();
 claim(&mut x,"agent-b",60,t(91)).unwrap();
 request_resolution(&mut x,"agent-b", &["ci:123".into()]).unwrap();
 resolve(&mut x,"manager", &["runtime:456".into()]).unwrap();
 println!("{}",json!({"state":"RESOLVED","owner":x.owner,"lease":x.lease,"resolved_by":x.resolved_by,"resolution_evidence_refs":x.resolution_evidence_refs}));
}
