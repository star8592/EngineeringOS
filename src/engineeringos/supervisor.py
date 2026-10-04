#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import pathlib
import subprocess
import tempfile
import time
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
from state_paths import runtime
STATE = runtime()


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()
    fd, tmp = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def append_jsonl_once(path: pathlib.Path, row: dict, unique_key: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a+', encoding='utf-8') as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        for line in handle:
            if not line.strip():
                continue
            old = json.loads(line)
            if old.get(unique_key) == row.get(unique_key):
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                return False
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return True


def build_action_brief(queue: dict, dispatch: dict, snapshot: dict, limit: int = 5) -> dict:
    by_dispatch = {row['id']: row for row in dispatch.get('items', [])}
    active = [
        item for item in queue.get('items', [])
        if item.get('state') not in {'RESOLVED', 'SUPERSEDED'}
    ]
    active.sort(key=lambda x: (x.get('priority', 99), x.get('kind', ''), x.get('id', '')))
    actions = []
    for item in active[:limit]:
        sched = by_dispatch.get(item['id'], {})
        actions.append({
            'item_id': item['id'],
            'priority': item.get('priority'),
            'kind': item.get('kind'),
            'state': item.get('state'),
            'reason': item.get('reason'),
            'required_assurance': item.get('required_assurance'),
            'automation': item.get('automation'),
            'schedule_state': sched.get('schedule_state', 'UNKNOWN'),
            'lane': sched.get('lane'),
            'target_mutation_authorized': False,
        })
    return {
        'schema_version': 1,
        'generated_at': utcnow(),
        'mode': 'G2_SHADOW',
        'project': 'DevControl',
        'snapshot_content_sha256': snapshot['content_sha256'],
        'active_work_items': len(active),
        'actions': actions,
        'guardrail': 'Advisory only. No DevControl mutation is authorized by this brief.',
    }


def make_timeseries_row(snapshot: dict, queue: dict, dispatch: dict, loop: dict) -> dict:
    queue_states = Counter(item.get('state', 'UNKNOWN') for item in queue.get('items', []))
    schedule_states = Counter(item.get('schedule_state', 'UNKNOWN') for item in dispatch.get('items', []))
    return {
        'schema_version': 1,
        'run_id': snapshot['run_id'],
        'observed_at': snapshot['observed_at'],
        'snapshot_content_sha256': snapshot['content_sha256'],
        'source_head': snapshot['source_head'],
        'manager_summary': snapshot['manager_summary'],
        'debt_counts': snapshot['debt_counts'],
        'queue_states': dict(sorted(queue_states.items())),
        'schedule_states': dict(sorted(schedule_states.items())),
        'dispatchable_count': snapshot['dispatchable_count'],
        'control_loop_summary': loop.get('summary', {}),
        'target_mutation_authorized': False,
    }


def read_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def make_timeseries_summary(rows: list[dict], limit: int = 50) -> dict:
    recent = rows[-limit:]
    if not recent:
        return {'schema_version': 1, 'observations': 0, 'recent': []}
    first, last = recent[0], recent[-1]
    keys = sorted(set(first.get('debt_counts', {})) | set(last.get('debt_counts', {})))
    deltas = {}
    for key in keys:
        a, b = first.get('debt_counts', {}).get(key), last.get('debt_counts', {}).get(key)
        if isinstance(a, int) and isinstance(b, int):
            deltas[key] = b - a
    return {
        'schema_version': 1,
        'generated_at': utcnow(),
        'observations': len(rows),
        'window_observations': len(recent),
        'window_start': first.get('observed_at'),
        'window_end': last.get('observed_at'),
        'debt_delta': deltas,
        'latest_snapshot_content_sha256': last.get('snapshot_content_sha256'),
        'latest_queue_states': last.get('queue_states', {}),
        'latest_schedule_states': last.get('schedule_states', {}),
        'recent': recent,
    }


def run_checked(args: list[str], timeout: int = 240) -> None:
    subprocess.run(args, cwd=ROOT, check=True, timeout=timeout, stdout=subprocess.DEVNULL)


def run_optional(args: list[str], timeout: int = 60) -> tuple[bool, str | None]:
    try:
        run_checked(args, timeout=timeout)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def run_cycle() -> dict:
    started = time.monotonic()
    started_at = utcnow()
    status_path = STATE / 'supervisor/status.json'
    try:
        run_checked(['python3', 'src/engineeringos/shadow_run.py'])
        snapshot = read_json(STATE / 'shadow/latest.json')
        queue = read_json(STATE / 'work-queue.json')
        dispatch = read_json(ROOT / 'artifacts/dispatch-plan.json')
        loop = read_json(STATE / 'control-loop/projection.json')

        row = make_timeseries_row(snapshot, queue, dispatch, loop)
        series_path = STATE / 'time-series.jsonl'
        appended = append_jsonl_once(series_path, row, 'run_id')
        series = read_jsonl(series_path)
        brief = build_action_brief(queue, dispatch, snapshot)
        summary = make_timeseries_summary(series)
        atomic_json(STATE / 'action-brief.json', brief)
        atomic_json(STATE / 'time-series-summary.json', summary)
        run_checked(['python3', 'src/engineeringos/action_details.py'], timeout=60)
        run_checked(['python3', 'src/engineeringos/system_one_shadow.py'], timeout=90)
        system_one = read_json(STATE / 'system-one/projection.json')
        run_checked(['python3', 'src/engineeringos/system_one_observations.py'], timeout=30)
        system_one_observations = read_json(STATE / 'system-one/observation-summary.json')
        run_checked(['python3', 'src/engineeringos/system_one_admission.py'], timeout=30)
        system_one_admission = read_json(STATE / 'system-one/admission.json')

        candidate_path = STATE / 'system-one/candidates/decis-kev-0.8b.json'
        candidate_summary_path = STATE / 'system-one/candidates/decis-kev-0.8b-summary.json'
        provider_matrix_path = STATE / 'system-one/provider-matrix.json'

        candidate_ok, candidate_error = run_optional(
            ['python3', 'src/engineeringos/system_one_candidate_shadow.py'],
            timeout=60,
        )
        if candidate_ok and candidate_path.exists():
            system_one_candidate = read_json(candidate_path)
        else:
            system_one_candidate = {
                'schema_version': 1,
                'generated_at': utcnow(),
                'candidate_id': 'decis-kev-0.8b',
                'provider': 'decis-kev-candidate',
                'role': 'PARALLEL_SHADOW_CANDIDATE',
                'status': 'ERROR',
                'advisory_only': True,
                'authorization': 'UNAVAILABLE',
                'influence_routing': False,
                'items': [],
                'errors': [{'error': candidate_error or 'candidate projection unavailable'}],
            }
            atomic_json(candidate_path, system_one_candidate)

        observations_ok, observations_error = run_optional(
            ['python3', 'src/engineeringos/system_one_candidate_observations.py'],
            timeout=30,
        )
        if observations_ok and candidate_summary_path.exists():
            system_one_candidate_observations = read_json(candidate_summary_path)
        else:
            system_one_candidate_observations = {
                'schema_version': 1,
                'generated_at': utcnow(),
                'candidate_id': 'decis-kev-0.8b',
                'provider': 'decis-kev-candidate',
                'candidate_status': system_one_candidate.get('status'),
                'observations': 0,
                'fresh': False,
                'error': observations_error or 'candidate observation summary unavailable',
            }
            atomic_json(candidate_summary_path, system_one_candidate_observations)

        matrix_ok, matrix_error = run_optional(
            ['python3', 'src/engineeringos/system_one_provider_matrix.py'],
            timeout=30,
        )
        if matrix_ok and provider_matrix_path.exists():
            system_one_matrix = read_json(provider_matrix_path)
        else:
            system_one_matrix = {
                'schema_version': 1,
                'generated_at': utcnow(),
                'items_compared': 0,
                'provider_agreement_rate': None,
                'candidate_influence_routing': False,
                'authorization': 'UNAVAILABLE',
                'fresh': False,
                'error': matrix_error or 'provider matrix unavailable',
            }
            atomic_json(provider_matrix_path, system_one_matrix)

        run_checked(['python3', 'src/engineeringos/g3_controller.py'], timeout=300)

        completed_at = utcnow()
        status = {
            'schema_version': 1,
            'health': 'HEALTHY',
            'mode': 'G2_SHADOW_G3_PILOT',
            'started_at': started_at,
            'completed_at': completed_at,
            'duration_seconds': round(time.monotonic() - started, 3),
            'last_run_id': snapshot['run_id'],
            'last_snapshot_content_sha256': snapshot['content_sha256'],
            'timeseries_appended': appended,
            'observations': len(series),
            'active_work_items': brief['active_work_items'],
            'top_action_count': len(brief['actions']),
            'system_one_status': system_one.get('status', 'UNKNOWN'),
            'system_one_provider': system_one.get('provider'),
            'system_one_advisory_items': len(system_one.get('items', [])),
            'system_one_admission': system_one_admission.get('state'),
            'system_one_observations': system_one_observations.get('observations', 0),
            'system_one_scheduler_agreement': system_one_observations.get('scheduler_agreement_rate'),
            'system_one_influence_routing': False,
            'system_one_candidate_status': system_one_candidate.get('status', 'UNKNOWN'),
            'system_one_candidate_provider': system_one_candidate.get('provider'),
            'system_one_candidate_items': len(system_one_candidate.get('items', [])),
            'system_one_candidate_observations': system_one_candidate_observations.get('observations', 0),
            'system_one_candidate_scheduler_agreement': system_one_candidate_observations.get('scheduler_agreement_rate'),
            'system_one_provider_agreement': system_one_matrix.get('provider_agreement_rate'),
            'system_one_candidate_influence_routing': False,
            'target_mutation_authorized': False,
        }
        atomic_json(status_path, status)
        run_checked(['python3', 'src/engineeringos/dashboard_projector.py'], timeout=60)
        return status
    except Exception as exc:
        status = {
            'schema_version': 1,
            'health': 'DEGRADED',
            'mode': 'G2_SHADOW',
            'started_at': started_at,
            'failed_at': utcnow(),
            'duration_seconds': round(time.monotonic() - started, 3),
            'error_type': type(exc).__name__,
            'error': str(exc),
            'target_mutation_authorized': False,
        }
        atomic_json(status_path, status)
        raise


def acquire_singleton_lock() -> object:
    STATE.mkdir(parents=True, exist_ok=True)
    handle = open(STATE / 'supervisor.lock', 'a+', encoding='utf-8')
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise SystemExit('EngineeringOS supervisor is already running') from exc
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()) + '\n')
    handle.flush()
    return handle


def main() -> int:
    parser = argparse.ArgumentParser(description='EngineeringOS continuous G2 project supervisor')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--interval', type=int, default=300)
    args = parser.parse_args()
    if args.interval < 30:
        raise SystemExit('interval must be >= 30 seconds')
    lock = acquire_singleton_lock()
    try:
        while True:
            status = run_cycle()
            print(json.dumps(status, ensure_ascii=False), flush=True)
            if args.once:
                return 0
            time.sleep(args.interval)
    finally:
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
