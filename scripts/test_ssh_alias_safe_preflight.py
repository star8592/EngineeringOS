#!/usr/bin/env python3
"""Pure regression tests for the sanitized SSH preflight; no shell/network."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ssh_alias_safe_preflight import evaluate


def main() -> None:
    sample = "\n".join([
        "hostname 192.0.2.4",
        "user operator-fixture",
        "identityfile /do/not/read/SECRET_PATH_MARKER",
        "identitiesonly yes",
        "stricthostkeychecking yes",
    ])
    good = evaluate("approved-project-alias", sample)
    assert good["status"] == "CONFIG_PREFLIGHT_OK_NOT_CONNECTED", good
    assert good["ssh_network_connection_attempted"] is False
    assert good["remote_execution_attempted"] is False
    assert good["configured_identity_candidates"] == 1
    assert "192.0.2.4" not in json.dumps(good)
    assert "SECRET_PATH_MARKER" not in json.dumps(good)
    assert "operator-fixture" not in json.dumps(good)

    raw = evaluate("192.0.2.4", sample)
    assert "RAW_IP_INPUT_REVIEW_PROJECT_ALIAS" in raw["findings"]
    many = evaluate("approved-project-alias", sample.replace("identitiesonly yes", "identitiesonly no"))
    assert "SSH_AGENT_CAN_OFFER_EXTRA_IDENTITIES" in many["findings"]
    unsafe = evaluate("approved-project-alias", sample.replace("stricthostkeychecking yes", "stricthostkeychecking no"))
    assert "HOST_KEY_VERIFICATION_DISABLED" in unsafe["findings"]

    with TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "AGENTS.md").write_text(
            "https://github.com/star8592/EngineeringOS/blob/main/docs/operations/"
            "CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md\n",
            encoding="utf-8",
        )
        assert evaluate("approved-project-alias", sample, root)["status"] == "CONFIG_PREFLIGHT_OK_NOT_CONNECTED"
        (root / "AGENTS.md").write_text("missing link\n", encoding="utf-8")
        assert "PROJECT_CANONICAL_RUNBOOK_LINK_MISSING" in evaluate("approved-project-alias", sample, root)["findings"]
    print("SSH_ALIAS_SAFE_PREFLIGHT=PASS (alias, identities, hostkey, redaction, project anchor)")


if __name__ == "__main__":
    main()
