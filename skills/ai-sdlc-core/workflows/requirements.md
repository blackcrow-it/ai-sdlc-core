# Workflow 02: Requirements

**Purpose:** Thực thi giai đoạn SDLC bằng supervised tasks trong Orca; playbook này không tự chạy.

**Primary owner:** `business-analyst`

## Prerequisites
- Approved scope
- Discovery artifacts

## Orchestrator execution contract
1. Verify previous phase artifacts exist and the preceding gate has passed.
2. Read `agents/business-analyst.md` and applicable policies.
3. Create scoped tasks with explicit input paths, acceptance criteria, owner, reviewer and dependency IDs.
4. Dispatch worker via version-matched Orca CLI commands and isolated worktree when code changes are needed.
5. Collect artifacts and actual CI/tool evidence; reject bare “done” messages.
6. Record gate decision, review comments and next-stage dependencies.

## Required artifact templates
- `templates/PRD.md`
- `templates/SRS.md`

## Quality gate
Yêu cầu có nguồn gốc, user stories và acceptance criteria kiểm thử được; unresolved rules escalated.

Apply `references/DOCUMENTATION-CONTINUITY.md`: create/update the applicable canonical PRD/SRS at their existing
paths, stable IDs, revision/approval history and coverage matrix. Identify baseline gaps and downstream document
impacts; a feature spec alone does not complete the requirements baseline.

## Exception / failure policy
Requirements ambiguity must return to Product Owner.
- Failed gates create a remediation task, not a silent advance.
- After configured retry limit, escalate to human with exact blockers and evidence.

## Next phase
`workflows/design.md` (only after the gate is accepted).
