---
name: sdlc-task
description: Turn one piece of work into a validated AI SDLC task contract in the configured tracker plus a self-contained Orca worker spec, without dispatching anything.
argument-hint: "What the task should achieve"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.8"
---

Write **one** task contract for the work the user described. Do not create Orca Runs, tasks or workers. For a breakdown into several tasks, use /sdlc-plan instead.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`. Run `SDLC validate`; if there is no config, recommend /sdlc-setup and stop.
2. Read `<CORE>/references/TASK-AUTHORING.md` (the rules for every step below), `<CORE>/references/trackers/<tracker.provider>.md`, `.ai-sdlc/project.json`, `<CORE>/agents/registry.json`, the candidate role file in `<CORE>/agents/`, `GLOSSARY.md`, the ADRs in `docs/adr/` and the code the task touches. List the tracker's tasks so you neither duplicate one nor miss a dependency.
3. Check the size: if the work is not one tracer-bullet slice that fits one fresh context window, say so and recommend /sdlc-plan.
   Read core `references/DOCUMENTATION-CONTINUITY.md`; assess the documentation map and affected requirements,
   contracts and guides. Include `documentation` in this task and its owned updates in scope/deliverables/criteria.
   Missing baselines or larger documentation work may require prerequisite tasks and /sdlc-plan.
4. Draft the contract per TASK-AUTHORING: owner and a different reviewer, narrow `allowed_paths`, observable acceptance criteria, `test_seams` for implementation roles, required checks from the project commands, dependencies on existing task IDs only, deliverables, risk and priority. Call the Skill tool with "sdlc-grilling" for interactive review in small independent batches; request the contract/publication approval through the host/workflow's permitted channel.
5. Publish per TASK-AUTHORING: next free `TASK-NNN`, `SDLC task new`, replace every `REPLACE` placeholder, `SDLC validate --task <file>` until it passes, then publish to the tracker and verify the round trip (on a remote tracker, confirm with the user before the issue is created; on the local tracker the file is the record, commit it with `Add TASK-NNN: <title>`).
6. Run `SDLC spec --task <file-or-fetched-issue-body>` and give the user the task reference (file path, issue number or Jira key), the spec path and a two-line summary of scope and checks.

To execute it, recommend `/sdlc-implement <task>` (one task in this session) or /sdlc-orchestrate (Orca workers).
