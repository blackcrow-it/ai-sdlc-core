# Workflow 09: Maintenance

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `technical-writer`

## Prerequisites
- Monitoring data
- Incident/user feedback

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/technical-writer.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/incident-report.md`

## Quality gate
Alerts/issues recorded, root cause investigated for incidents, follow-up backlog created.

## Exception / failure policy
Treat production incidents with incident commander/human override.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/discovery.md` (only after the gate is accepted).
