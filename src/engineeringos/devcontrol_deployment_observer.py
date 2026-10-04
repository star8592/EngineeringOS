from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import shlex
import subprocess
from typing import Any


DEFAULT_REPO = pathlib.Path("/mnt/disk1/Code/DevControl2")
DEFAULT_AGENT_ROOT = pathlib.Path.home() / ".local/lib/devcontrol3"
DEFAULT_PRODUCTION_HOST = "23.94.143.205"
DEFAULT_SERVER_ROOT = pathlib.PurePosixPath("/opt/devcontrol3")

_REMOTE_TREE_SCRIPT = r'''
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1])
if not root.is_dir():
    raise SystemExit(3)
records=[]
for p in sorted(root.rglob("*"), key=lambda x:x.relative_to(root).as_posix()):
    rel=p.relative_to(root).as_posix()
    if p.is_symlink():
        records.append(("L",rel,p.readlink().as_posix()))
    elif p.is_file():
        h=hashlib.sha256()
        with p.open("rb") as f:
            while True:
                b=f.read(1024*1024)
                if not b: break
                h.update(b)
        records.append(("F",rel,h.hexdigest()))
manifest="".join(f"{kind}\t{rel}\t{value}\n" for kind,rel,value in records)
print(json.dumps({
    "root":str(root),
    "entry_count":len(records),
    "file_count":sum(1 for x in records if x[0]=="F"),
    "symlink_count":sum(1 for x in records if x[0]=="L"),
    "tree_sha256":hashlib.sha256(manifest.encode()).hexdigest(),
},sort_keys=True))
'''


class DeploymentObservationError(RuntimeError):
    pass


def canonical_tree_digest(root: pathlib.Path) -> dict[str, Any]:
    root = pathlib.Path(root)
    if not root.is_dir():
        raise DeploymentObservationError("TREE_ROOT_MISSING")

    records: list[tuple[str, str, str]] = []
    for path in sorted(
        root.rglob("*"),
        key=lambda value: value.relative_to(root).as_posix(),
    ):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            records.append(("L", rel, path.readlink().as_posix()))
        elif path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
            records.append(("F", rel, digest.hexdigest()))

    manifest = "".join(
        f"{kind}\t{rel}\t{value}\n"
        for kind, rel, value in records
    )
    return {
        "root": str(root),
        "entry_count": len(records),
        "file_count": sum(1 for row in records if row[0] == "F"),
        "symlink_count": sum(1 for row in records if row[0] == "L"),
        "tree_sha256": hashlib.sha256(manifest.encode()).hexdigest(),
    }


def _run(
    args: list[str],
    *,
    timeout: float = 12.0,
) -> str:
    try:
        return subprocess.check_output(
            args,
            text=True,
            stderr=subprocess.PIPE,
            timeout=timeout,
        ).strip()
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        raise DeploymentObservationError(
            f"COMMAND_FAILED:{args[0]}:{exc.returncode}:{detail[:300]}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise DeploymentObservationError(
            f"COMMAND_TIMEOUT:{args[0]}"
        ) from exc


def _remote_python_command(script: str, *args: str) -> str:
    parts = ["python3", "-c", script, *args]
    return " ".join(shlex.quote(part) for part in parts)


def _release_from_link(target: str) -> str | None:
    if not target:
        return None
    return pathlib.PurePosixPath(target).name or None


def observe_local_agent(
    release_id: str,
    *,
    agent_root: pathlib.Path = DEFAULT_AGENT_ROOT,
) -> dict[str, Any]:
    current = agent_root / "current"
    try:
        target = os.readlink(current)
    except OSError as exc:
        return {
            "state": "UNKNOWN",
            "reason": f"CURRENT_LINK_UNREADABLE:{type(exc).__name__}",
        }

    observed_release = _release_from_link(target)
    release_dir = agent_root / "releases" / release_id
    try:
        tree = canonical_tree_digest(release_dir)
    except DeploymentObservationError as exc:
        return {
            "state": "UNKNOWN",
            "current_target": target,
            "observed_release_id": observed_release,
            "reason": str(exc),
        }

    return {
        "state": (
            "RESOLVED"
            if observed_release == release_id and tree["file_count"] > 0
            else "MISMATCH"
        ),
        "current_target": target,
        "observed_release_id": observed_release,
        "release_dir": str(release_dir),
        **tree,
    }


def remote_tree_command(path: str) -> str:
    encoded = base64.b64encode(
        _REMOTE_TREE_SCRIPT.encode()
    ).decode()
    runner = (
        "import base64;"
        f"exec(base64.b64decode({encoded!r}))"
    )
    return (
        "python3 -c "
        + shlex.quote(runner)
        + " "
        + shlex.quote(path)
    )


def observe_remote_server(
    release_id: str,
    *,
    host: str = DEFAULT_PRODUCTION_HOST,
    server_root: str = str(DEFAULT_SERVER_ROOT),
) -> dict[str, Any]:
    ssh = [
        "ssh",
        "-F",
        "/dev/null",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=8",
        f"root@{host}",
    ]
    try:
        target = _run(
            ssh + ["readlink", f"{server_root}/current"],
            timeout=12,
        )
        observed_release = _release_from_link(target)
        tree_raw = _run(
            ssh
            + [
                remote_tree_command(
                    f"{server_root}/releases/{release_id}"
                )
            ],
            timeout=20,
        )
        tree = json.loads(tree_raw)
    except (DeploymentObservationError, json.JSONDecodeError) as exc:
        return {
            "state": "UNKNOWN",
            "host": host,
            "reason": f"{type(exc).__name__}:{exc}",
        }

    return {
        "state": (
            "RESOLVED"
            if observed_release == release_id
            and int(tree.get("file_count", 0)) > 0
            else "MISMATCH"
        ),
        "host": host,
        "current_target": target,
        "observed_release_id": observed_release,
        "release_dir": f"{server_root}/releases/{release_id}",
        **tree,
    }


def evaluate_deployment_binding(
    *,
    release_id: str,
    full_source_sha: str | None,
    server: dict[str, Any],
    agent: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    if not full_source_sha:
        reasons.append("SOURCE_IDENTITY_UNRESOLVED")
    elif not full_source_sha.startswith(release_id):
        reasons.append("RELEASE_SOURCE_MISMATCH")

    if server.get("state") != "RESOLVED":
        reasons.append("SERVER_DEPLOYMENT_UNRESOLVED")
    if agent.get("state") != "RESOLVED":
        reasons.append("AGENT_DEPLOYMENT_UNRESOLVED")

    for name, observed in (("server", server), ("agent", agent)):
        if observed.get("observed_release_id") != release_id:
            reasons.append(f"{name.upper()}_RELEASE_MISMATCH")
        if not observed.get("tree_sha256"):
            reasons.append(f"{name.upper()}_TREE_DIGEST_MISSING")

    resolved = not reasons
    binding_payload = {
        "release_id": release_id,
        "full_source_sha": full_source_sha,
        "server_tree_sha256": server.get("tree_sha256"),
        "agent_tree_sha256": agent.get("tree_sha256"),
    }
    binding_raw = json.dumps(
        binding_payload,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "state": "RESOLVED" if resolved else "PARTIAL",
        "binding_sha256": (
            hashlib.sha256(binding_raw.encode()).hexdigest()
            if resolved
            else None
        ),
        "reasons": reasons,
        "binding": binding_payload,
    }


def observe_deployment(
    *,
    release_id: str,
    full_source_sha: str | None,
    production_host: str | None = None,
) -> dict[str, Any]:
    host = (
        production_host
        or os.environ.get("DEVCONTROL3_PRODUCTION_HOST")
        or DEFAULT_PRODUCTION_HOST
    )
    server = observe_remote_server(
        release_id,
        host=host,
    )
    agent = observe_local_agent(release_id)
    evaluation = evaluate_deployment_binding(
        release_id=release_id,
        full_source_sha=full_source_sha,
        server=server,
        agent=agent,
    )
    return {
        "schema_version": 1,
        "release_id": release_id,
        "full_source_sha": full_source_sha,
        "production_host": host,
        "server": server,
        "agent": agent,
        "deployment_identity_state": evaluation["state"],
        "deployment_binding_sha256": evaluation["binding_sha256"],
        "binding": evaluation["binding"],
        "reasons": evaluation["reasons"],
        "observation_authority": "DEPLOYMENT_HOST_OBSERVATION",
        "target_mutation_authorized": False,
    }
