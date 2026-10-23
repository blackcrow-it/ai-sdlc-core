---
name: sdlc-smoke
description: Prove Orca orchestration works in this repository - supervise exactly one Business Analyst worker that drafts demo authentication requirements, then verify, settle and report.
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.0"
---

Run the AI SDLC Core smoke test as the supervised Orchestrator, in this session.

1. Locate `<CORE>`: the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). `SDLC` = `python "<CORE>/scripts/sdlc.py"`.
2. Run `SDLC validate`. If it fails, recommend /sdlc-setup and stop.
3. Run `SDLC activate --smoke`. It writes `.ai-sdlc/runs/smoke-test/ba-task-spec.md` and `.ai-sdlc/runs/smoke-test/orchestrator-prompt.md`. Read the prompt and follow the text after its `---` line as your instructions.
4. Do the read-only pre-flight and present the one-worker plan. **Stop.** Only the user's message `START-ORCA-SMOKE-TEST` authorizes creating the Run, Task and worker.
5. After approval:
   - create one Run;
   - create one Task whose `--spec` is the complete spec file content;
   - start one worker with `--worktree current`;
   - wait with `check`.
6. On `worker_done`:
   - match its task and dispatch IDs against the ones you created;
   - run `SDLC smoke check`;
   - read both outputs yourself for semantic quality;
   - confirm that no files outside `.ai-sdlc/runs/smoke-test/` changed;
   - then `worker-release` and ack the delivery.
7. Report Run, Task and Dispatch IDs, provider, files, pass/fail per criterion and the next step (/sdlc-orchestrate).
