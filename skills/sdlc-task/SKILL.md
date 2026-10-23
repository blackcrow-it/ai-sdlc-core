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
4. Read `<CORE>/references/trackers/<tracker.provider>.md`. Task contracts live only in that tracker; follow its recipes for every step below.
5. Take the next free `TASK-NNN` id as that document describes. Run `SDLC task new --id <id> --title "<title>" --role <owner> [--reviewer <role>]`. Replace every `REPLACE` placeholder with the agreed values, then run `SDLC validate --task <file>` until it passes.
6. Publish the task to the tracker and verify the round trip, unless the tracker is `local`, where the file is already the record. Creating an issue is visible to others, so confirm with the user first.
7. Run `SDLC spec --task <file-or-fetched-issue-body>` and give the user the task reference (file path, issue number or Jira key), the spec path and a two-line summary of scope and checks.

To execute the task, the user runs /sdlc-orchestrate.
