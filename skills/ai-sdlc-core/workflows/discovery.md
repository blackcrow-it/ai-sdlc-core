# Workflow 01: Discovery

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `product-manager`

## Prerequisites
- Project brief
- User problem

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/product-manager.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/PRD.md`

## Quality gate
Mục tiêu, đối tượng, MVP, success metrics và điều chưa biết đã được ghi; human duyệt scope.

## Exception / failure policy
Unclear market/user assumptions must be written as open questions.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/requirements.md` (only after the gate is accepted).
