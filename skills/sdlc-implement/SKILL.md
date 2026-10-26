---
name: sdlc-implement
description: Carry out exactly one task contract in this session, without Orca - act as its owner role, build at the agreed test seams, run the required checks and a scope check, get an independent review, commit to a task branch and hand it over for acceptance.
argument-hint: "TASK-NNN, issue number or Jira key (optional: pick from the frontier)"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.7"
---

Carry out **one** task contract in the repository at the current working directory. One task per invocation: never start a sibling task, and clear the context (`/clear`) before the next one. Each contract is self-contained, so the previous task's context is disposable.

## 1. Load the task

1. `<CORE>` is the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`. Run `SDLC validate`; without a config, recommend /sdlc-setup and stop.
2. Follow `<CORE>/references/trackers/<tracker.provider>.md`. Without an argument, list the **frontier** (status `ready` or `changes_requested`, every dependency `accepted`) and ask which task to take. With an argument, read that task. If the reference is ambiguous, ask.
3. Save the contract (remote trackers: the fetched issue body in `.ai-sdlc/runs/tasks/TASK-NNN.md`) and run `SDLC validate --task <file>`. State the task's ID and title.
4. Stop and report instead of working when the contract is invalid, its status is not `ready` or `changes_requested`, a dependency is not `accepted`, or it has no `test_seams` while its owner is an implementation role.
   Read core `references/DOCUMENTATION-CONTINUITY.md`. An unassessed legacy contract needs its `documentation`
   assessment reviewed and recorded in the tracker before execution; resolve any new scope/dependency decisions.
5. Run `SDLC spec --task <file> --stdout` and read the spec in full, then every reference file it lists. The spec is your brief: role, write ceiling, protected paths, forbidden actions, checks and handoff format.

## 2. Prepare the branch

The working tree must be clean; otherwise ask the user what to do with the changes. If the current branch is the default branch, create `task/<task-id-lowercase>-<slug>` from it. Record the base commit (`git rev-parse HEAD`) for the scope check and the review.

Set the task to `in_progress` with the tracker's "Set status" recipe.

## 3. Do the work as the owner role

Act as `owner_agent`: call the Skill tool with that role's `primary_skill` from `<CORE>/agents/registry.json` (for example "sdlc-implementation" for a developer role, "sdlc-requirements-analysis" for the Business Analyst) and follow it. Implementation roles build test-first at the contract's `test_seams` with "sdlc-tdd"; a check that fails for an unclear reason goes through "sdlc-debugging".

Questions about requirements or scope use the `sdlc-grilling` skill's interactive batches and actual-answer tracking.
Anything outside the contract (a needed path outside `allowed_paths`, a new seam, a changed acceptance criterion)
is the user's decision: ask through a channel permitted for that decision, and if they agree, change the contract
first (validate, update it in the tracker), then continue.

## 4. Verify

1. Run every entry of `required_checks` with the configured commands, exactly as written. Record command, exit code and a log path for each. A check you could not run is `not_run` with the reason.
2. Run `SDLC scope --task <file> --base <base commit>`. It must report no path outside `allowed_paths` and none inside a protected path.
3. Map each acceptance criterion to the test or artifact that proves it.
4. Complete the owned documentation updates and run `SDLC docs-check --task <file> --base <base commit>`.
   Check canonical requirement-to-evidence links and report linked documentation tasks still pending; a structural
   pass does not establish completeness or acceptance of the whole feature.

## 5. Independent review

The author never reviews its own change. Start a sub-agent with a fresh context (if the harness has none, tell the user and ask them to review) and give it only pointers: the contract file, the base commit, the diff command `git diff <base>...HEAD` and the role `reviewer_agent`. Tell it to call the Skill tool with that role's `primary_skill` (usually "sdlc-code-review") and return its report.

Fix every blocker and major finding, re-run the affected checks and the scope check, and repeat the review while attempts remain (`max_attempts`). Minor findings: fix or list them in the handoff.

## 6. Commit and hand over

1. Commit only the task's changes to the task branch with the message `TASK-NNN: <title>`; for a bug, add the hypothesis that turned out correct to the message body. Do not push, merge or open a pull request unless the user asks; a pull request body follows `<CORE>/templates/pull-request.md`.
2. Write the handoff in the format of `<CORE>/references/HANDOFF.md` (status `submitted_for_review`, real commands and exit codes, changed paths, the review outcome, risks, `next_owner`) and record it with the tracker's "Record evidence" recipe. Set the status to `submitted_for_review`.
3. `accepted` is a human decision: set it only when the user explicitly accepts the task in this session, and record their name and the date. When `human_approval_required` is true, the acceptance must come from the approver named in `sdlc.approvers` for that gate.

Report the branch, commit, checks with exit codes, scope check result, review verdict and the next frontier task. Suggest `/sdlc-retro` if the task went sideways.
