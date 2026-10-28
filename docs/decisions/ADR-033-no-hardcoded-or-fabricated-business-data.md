# ADR-033 — Zero fabricated business data; configuration-driven software

Status: ACCEPTED (owner directive, 2026-10-28)

## Binding scope
This rule applies to **all current and future projects managed by EngineeringOS**,
including internal tools, applications, customer services, agents, data factories,
education projects and their CI/automation scripts. It is a release-blocking policy,
not a documentation preference.

## R1. No hard-coded operating or business values
Runtime years, regions, school/program eligibility, prices, billing products,
tenants, branch identities, admin accounts, credentials, API URLs, ports, disk
paths, service IDs, provider endpoints, machine names, task schedules, model
choices, and quota/limit policies must come from explicit validated configuration
or versioned source-of-truth records. Missing configuration **fails closed**.
No implicit local defaults that masquerade as live production behavior.

Technical constants that define an actual protocol or security invariant
(e.g. HTTP status codes, SQL enum values, a cryptographic algorithm, strict input
bounds) are not business hard-coding. They must still be documented, reviewed,
and adjustable where their operational policy may change.

## R2. No fabricated facts or records
Do not invent, auto-seed, or silently replace absent customers, students,
schools, enrollment history, scores, financial transactions, balances, device
status, product inventory, revenue, performance, reservations, jobs, or any
business-domain data. Production and development must reflect **real verified
records only**. No placeholder/filler content masquerading as fact.

When a real source cannot be reached, preserve an explicit state such as
UNAVAILABLE, NOT_VERIFIED, MISSING, UNKNOWN, or STALE with provenance. Never
synthesize plausible data to make a page, chart, API or report appear complete.

## R3. Explicit exception only
The owner may **explicitly request** a fictional case, UI demo or artificial
test dataset for a particular named task. Such an exception must be scoped to
that task and environment, labeled unambiguously, excluded from production
reports, and removed or isolated when the authorized task is finished. Prior
permission is not standing permission for unrelated repos or later work.

## R4. Existing code is in scope
Prior defaults, code-generated demos, hardcoded snapshots, canned content,
unsafe development seeds and SQLite-like throwaway production stand-ins must be
identified and remediated. Merely appending this ADR is not compliance.

## R5. Engineering enforcement
Each governed repo needs:
- project-specific inventory of runtime configuration and factual inputs;
- automated pre-commit / CI guard checking prohibited literals, fake seed data,
  and implicit fallbacks;
- read-only source provenance tests using verified external/official records;
- no data-writing synthetic fixture tests unless explicitly authorized;
- immutable source/observation metadata (source URI, checksum, effective year,
  scope, verified status) for decisions or published claims;
- migration and rollback evidence where existing business data is changed;
- release checklist with evidence of passing checks and no unapproved exceptions.

## R6. Respect project ownership
Central policy does not authorize unsupervised rewriting, deleting, restarting,
or deploying unrelated projects. Enforce via isolated branches, reviewed PRs
and documented evidence. Flag deviations as **OPEN** until verified remediation,
not as magically fixed by a policy file.

## Acceptance
A project is **compliant** only after repository-specific checks and real-data
tests pass on the relevant code, and the release evidence confirms that no
unreviewed fake data or business hardcoding remains. An audit scanner can
identify likely violations but cannot prove universal absence.

Source: direct owner directive. Supersedes any older EngineeringOS defaults
that suggested generated customers, placeholder transactions or fabricated
user scenarios as routine substitutes for production evidence.
