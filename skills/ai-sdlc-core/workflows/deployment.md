# Workflow 08: Deployment

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `devops-engineer`

## Prerequisites
- Reviewed build
- Human release decision

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/devops-engineer.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/release-notes.md`

## Quality gate
CI/gates pass; staging verified; rollback documented; production requires explicit human approval.

Apply `references/DOCUMENTATION-CONTINUITY.md`: final integrated reconciliation is accepted, applicable release
notes and user/operator/migration guidance match the build, and traceability/baseline approvals reference real
revisions and evidence. Pending required documentation blocks release unless a named human records an exception.

## Exception / failure policy
No destructive deployment without human approval.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/maintenance.md` (only after the gate is accepted).
