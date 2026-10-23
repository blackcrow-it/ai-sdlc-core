# Workflow 05: Planning

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `project-manager`

## Prerequisites
- Approved design/architecture
- Acceptance criteria

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/project-manager.md` and applicable policies.
3. Create scoped tasks per `references/TASK-AUTHORING.md` (tracer-bullet slices, prefactors first, expand-contract for wide refactors) with explicit input paths, acceptance criteria, test seams, owner, reviewer and dependency IDs; run the graph check over the whole breakdown.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/task.md`

## Quality gate
Tasks have owner, genuine dependencies (graph check passes), file scope, test seams, reviewer and budget; every requirement maps to a task; critical path understood.

## Exception / failure policy
Reject tasks without acceptance criteria.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/development.md` (only after the gate is accepted).
