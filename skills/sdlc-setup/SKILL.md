---
name: sdlc-setup
description: Set up AI SDLC Core in the current repository - detect the stack, interview the user for what cannot be detected, write .ai-sdlc/project.json and the AGENTS.md/CLAUDE.md blocks, validate and commit.
argument-hint: "Optional: one line about the project"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.0"
---

Set up AI SDLC Core in the repository at the current working directory. You run every command; never ask the user to type one.

## 1. Locate the engine

`<CORE>` is the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise look in `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). The engine is `python "<CORE>/scripts/sdlc.py"` (use `python3` or `py -3` if `python` is missing); call it `SDLC` below. Confirm with `SDLC where`.

If `.ai-sdlc/project.json` already exists, stop and use /sdlc-status instead. Re-initialise with `--force` only when the user explicitly asks.

## 2. Find the facts yourself

- `SDLC init --dry-run` prints `DETECTED` lines (each with its evidence) and the draft config.
- Read `docs/brief.md` if present, README, CONTRIBUTING, package manifests, lockfiles, CI workflows and any existing `AGENTS.md` / `CLAUDE.md`. The brief's scope, constraints and product owner are the starting answers for step 3.

From this, prepare a recommended answer for every question in step 3. Facts are your job; only decisions go to the user.

## 3. Interview in rounds

Ask the open decisions as numbered questions, each with your recommended answer, then wait. Ask follow-ups in later rounds only when an answer opens new questions. Cover:

1. Project id and name, description, reply language (default Vietnamese).
2. Languages, frameworks, package manager, runtimes.
3. Architecture style, a one-paragraph summary, architecture docs.
4. Commands: install, build, lint, typecheck, **test (required)**, e2e, security. Never invent a test command; if the repository has none, the user must give one.
5. Coding rules and rule files.
6. Functional scope: in scope and out of scope.
7. Write ceiling (`allowed_paths`) and extra protected paths. Core protections (`.ai-sdlc/project.json`, CI workflows, `.env*`, keys, secrets) always apply.
8. Human approvers: product_owner, tech_lead, security_owner, release_owner. Use real names only; an empty role keeps its gate blocked.
9. Worker agent (`claude` or `codex`) and any phases or roles to disable (default: all enabled).
10. **Issue tracker:** the single place task contracts will live. Options are `local` (JSON files in `.ai-sdlc/tasks/`, committed), `github` (`gh`), `gitlab` (`glab`), `jira` (through `orca jira`; needs the project key), or `other` (the user describes the workflow in one paragraph). Recommend the tracker named in the `tracker suggestion` line from `init --dry-run` when there is one; otherwise recommend `local`. Tasks are never mirrored to a second place.

## 4. Write and validate

Run `SDLC init` with the agreed answers: `--name --id --description --reply-language --language --framework --package-manager --runtime --architecture-style --architecture-summary --architecture-doc --install-cmd --build-cmd --lint-cmd --typecheck-cmd --test-cmd --e2e-cmd --security-cmd --rule --rule-file --in-scope --out-of-scope --allowed-path --protected-path --approver ROLE=NAME --agent --phase --role --tracker --tracker-project --tracker-notes`. Repeat a flag for several values; quote every value.

Run `SDLC validate`. Fix each error by re-running init with `--force` and corrected flags. Do not hand-edit around the validator.

## 5. Review and commit

Show the user a short summary of the config plus `git diff --stat`. On their approval, commit only `.ai-sdlc/project.json AGENTS.md CLAUDE.md .gitignore` with the message `Adopt AI SDLC Core`. Orca worktrees are created from commits, so an uncommitted config is invisible to workers.

## 6. Hand over

Run `SDLC doctor` and report every FAIL and WARN with its fix, including the `tracker` line (CLI installed and logged in). Suggest /sdlc-smoke to prove Orca orchestration end to end, then `/sdlc-orchestrate docs/brief.md`. If there is no brief yet, suggest /sdlc-brief first.
