# Tool Surface Drift Acceptance — 2026-10-05

## Purpose

Prove that EngineeringOS detects a real ChatGPT Host tool-contract drift even when tool membership still looks healthy.

## Live observation

- Backend: DevControl
- Backend version: 3.1.28
- Public tool count: 26
- ChatGPT Host visible tool count: 26
- Gateway source ↔ public MCP: PASS
- Host observable contract: FAIL
- EngineeringOS surface state: TOOL_SURFACE_DRIFT
- EngineeringOS freshness state at detection: HOST_OBSERVATION_STALE
- Host acceptance: NOT_PROVEN_BY_SURFACE_OBSERVATION

DevControl's own Host verifier reported observable contract drift for 10 tools:

- agent_echo
- browser_snapshot
- browser_targets
- get_git_diff
- get_git_status
- list_devices
- list_directory
- list_processes
- read_file
- read_process_logs

## Acceptance result

EngineeringOS backend-surface admission returned DENY / TOOL_SURFACE_DRIFT. The browser Engineering Details surface displayed the same degraded state. Local EngineeringOS self-hosting remained independent because it does not execute through the ChatGPT DevControl Host surface.

## Invariant

Tool count is not acceptance evidence. Matching membership with stale descriptions or input contracts is still drift. An old Host observation cannot remain valid after the canonical tool contract changes. A new Host observation must be captured before Host-dependent autonomous execution resumes.
