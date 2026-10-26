---
name: sdlc-plan
description: Break a spec, brief, SRS or the current conversation into tracer-bullet task contracts with blocking edges, review the breakdown with you, then publish them to the configured tracker - planning only, nothing is dispatched.
argument-hint: "Path or tracker reference of the spec, brief or SRS (optional)"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.8"
---

Plan the work as a set of task contracts. Do not create Orca Runs, tasks or workers, and do not write product code.

1. `<CORE>` is the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`. Run `SDLC validate`; if there is no config, recommend /sdlc-setup and stop.
2. Read `<CORE>/references/TASK-AUTHORING.md` (the rules for every step below), `<CORE>/references/trackers/<tracker.provider>.md`, `<CORE>/agents/registry.json` and `.ai-sdlc/project.json`.
3. Gather the source. With an argument, read that file, or fetch that issue with its body and comments. Without one, use this conversation; if it holds no plan, ask for the spec or recommend /sdlc-grill. List the tasks already in the tracker and do not duplicate work they cover.
4. Explore the code the work touches, with `GLOSSARY.md` and the ADRs in `docs/adr/`. Look for **prefactoring** that makes the work easy.
5. Draft the breakdown per TASK-AUTHORING: tracer-bullet slices (prefactors first, expand-contract for wide refactors), owner and a different reviewer per task, blocking edges, `test_seams` for implementation roles, acceptance criteria from the spec's user stories. Every user story in the source must land in some task's acceptance criteria, or in the plan's explicit out-of-scope list; show that mapping.
   Read core `references/DOCUMENTATION-CONTINUITY.md` and map every documentation impact row to owned updates
   or an explicit no-impact decision. Include `documentation` in every contract. Plan missing canonical baselines,
   changed PRD/SRS approval before dependent implementation, single ownership of shared files and a final
   integrated reconciliation of traceability, test evidence and guides before feature acceptance. Show this
   documentation coverage with the story-to-task mapping; inspect legacy inputs when no impact table exists.
6. Review the breakdown with the user (the "Review with the user" section) and iterate until they approve it.
7. Publish per TASK-AUTHORING: draft, validate each contract and the whole graph, confirm before creating remote issues, publish blockers first, verify each round trip.

Report the task references in dependency order and the current **frontier**. Recommend `/sdlc-implement <first frontier task>` to build one task in this repository, or `/sdlc-orchestrate` to have Orca workers build the plan in parallel worktrees.
