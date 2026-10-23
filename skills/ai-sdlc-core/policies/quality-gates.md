# Policy: Evidence-Based Quality Gates

| Gate | Automated evidence | Human decision (when required) |
|---|---|---|
| Requirement | Completeness/traceability checklist, accepted criteria | Confirm uncertain business rules/scope |
| Design | Interface/ADR review, accessibility checklist | Accept material UX/architecture tradeoff |
| Planning | Task schema valid, graph check (`validate --task ...`) passes, owner/reviewer distinct, `test_seams` set for implementation roles | Accept priority/budget constraints |
| Implementation | Build, lint, typecheck, unit/integration checks; tests at the agreed seams seen red then green; `sdlc.py scope` passes | None unless risk flagged |
| Review | Independent Spec, Standards and Risk findings (`sdlc-code-review`) and required CI green | Code owner review per repository rules |
| Security | Secrets scan, dependency/authorization checks as applicable | Accept residual material risk |
| Release | Immutable artifact, UAT where needed, staging smoke, rollback | Explicit production release approval |

## Documentation gate (every project and change)

Apply core `references/DOCUMENTATION-CONTINUITY.md` at Requirements, Planning, Implementation, Review and Release.
The documentation map and impact assessment identify applicable baselines and gaps; tasks own all needed updates
with real dependencies and verification. Both `sdlc.py scope` and `sdlc.py docs-check` must pass before task closure.
Independent review checks semantic consistency, stable requirement IDs, actual traceability evidence and baseline
approvals. Feature/release acceptance additionally requires reconciliation of the integrated documents and all
owning tasks. Missing/stale required documents block closure; a named human exception is `waived`, never `pass`.

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
