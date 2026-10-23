# Workflow 07: Testing

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `qa-engineer`

## Prerequisites
- Built artifact
- Acceptance criteria

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/qa-engineer.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/test-report.md`

## Quality gate
Required checks pass or failures are triaged; blocker security issues resolved.

Apply `references/DOCUMENTATION-CONTINUITY.md`: reconcile changed requirements with canonical acceptance criteria,
test methods and actual run evidence at the reviewed revision; expose missing coverage, stale docs and `not_run`.

## Exception / failure policy
Do not report PASS for skipped/not-run tests.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/deployment.md` (only after the gate is accepted).
