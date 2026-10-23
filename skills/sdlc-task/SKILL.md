---
name: sdlc-task
description: Turn one piece of work into a validated AI SDLC task contract and a self-contained Orca worker spec, without dispatching anything.
argument-hint: "What the task should achieve"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.0"
---

Write one task contract for the work the user described. Do not create Orca Runs, tasks or workers.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`. Run `SDLC validate`; if there is no config, recommend /sdlc-setup and stop.
2. Read `.ai-sdlc/project.json`, `<CORE>/agents/registry.json`, the candidate role file in `<CORE>/agents/`, and the code the task touches.
3. Draft the contract:
   - owner: one enabled role;
   - reviewer: a different enabled role;
   - `allowed_paths`: as narrow as the change allows, inside `scope.allowed_paths` and outside protected paths;
   - acceptance criteria: observable, Given/When/Then where possible;
   - dependencies: existing task IDs only;
   - deliverables, risk and priority.
   Show the draft as one round of numbered decisions, each with your recommendation, and wait for the user.
4. Use the next free `TASK-NNN` id in `.ai-sdlc/tasks/`. Run `SDLC task new --id <id> --title "<title>" --role <owner> [--reviewer <role>]`. Replace every `REPLACE` placeholder in the JSON with the agreed values, then run `SDLC validate --task <file>` until it passes.
5. Run `SDLC spec --task <file>` and give the user the spec path, plus a two-line summary of the task's scope and checks.

To execute the task, the user runs /sdlc-orchestrate.
