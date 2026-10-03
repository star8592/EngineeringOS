use chrono::{TimeZone, Utc};
use eos_core::{SchedulerItem, schedule_at, validate_dependencies};
use serde_json::json;
use std::io::{self, Read};
fn main() {
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let items: Vec<SchedulerItem> = serde_json::from_str(&s).unwrap();
    let now = Utc.timestamp_opt(0, 0).unwrap();
    println!(
        "{}",
        json!({"errors":validate_dependencies(&items),"schedule":schedule_at(&items,now)})
    );
}
