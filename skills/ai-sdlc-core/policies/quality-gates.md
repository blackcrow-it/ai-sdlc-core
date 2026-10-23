# Policy: Evidence-Based Quality Gates

| Gate | Automated evidence | Human decision (when required) |
|---|---|---|
| Requirement | Completeness/traceability checklist, accepted criteria | Confirm uncertain business rules/scope |
| Design | Interface/ADR review, accessibility checklist | Accept material UX/architecture tradeoff |
| Planning | Task schema valid, dependencies acyclic, owner/reviewer distinct | Accept priority/budget constraints |
| Implementation | Build, lint, typecheck, unit/integration checks | None unless risk flagged |
| Review | Independent findings and required CI green | Code owner review per repository rules |
| Security | Secrets scan, dependency/authorization checks as applicable | Accept residual material risk |
| Release | Immutable artifact, UAT where needed, staging smoke, rollback | Explicit production release approval |

## Outcome semantics
- `pass`: requirements met **with verifiable evidence**.
- `fail`: verified failure; create fix task.
- `blocked`: missing prerequisite / environmental blocker.
- `not_run`: check not executed; never equate to `pass`.
- `waived`: an authorized human-approved exception with timestamp, rationale, scope and expiry.

## Minimum task closure evidence
- Task ID and commit/PR/diff identifier.
- Paths of artifacts and actual changed files.
- Commands executed, exit codes, environment and accessible test logs.
- Review decision by separate owner when required.
- Outstanding issues and their disposition.

Never rely on an LLM self-report as the sole source of pass/fail.
