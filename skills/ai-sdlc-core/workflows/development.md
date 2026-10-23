# Workflow 06: Development

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `backend-developer`

## Prerequisites
- Approved tasks
- Architecture and API contract

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/backend-developer.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/task.md`

## Quality gate
Implementation exists, built test-first at the task's test seams, focused checks pass, `sdlc.py scope` passes, changes traceable, independent three-axis review (`sdlc-code-review`) requested.

Apply `references/DOCUMENTATION-CONTINUITY.md`: complete owned canonical document updates, run `sdlc.py docs-check`
with the recorded base commit and hand off actual requirement-to-evidence links plus pending sibling updates.

## Exception / failure policy
Parallel workers must use nonconflicting scope / worktrees.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/testing.md` (only after the gate is accepted).
