---
name: sdlc-setup
description: Set up AI SDLC Core in the current repository - detect the stack, interview the user for what cannot be detected, write .ai-sdlc/project.json and the AGENTS.md/CLAUDE.md blocks, validate and commit.
argument-hint: "Optional: one line about the project"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.2"
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

Call the Skill tool with "sdlc-grilling" and use its permitted interactive question tool and small independent
batches. Reuse facts/decisions already established; track actual answers and defer dependent questions until their
prerequisites are settled. Tool/mode restrictions and fallback follow that skill, not a Markdown question format. Cover:

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
11. **Triage labels** (only for a remote tracker): "Keep the default triage labels?" (recommended: yes). The defaults equal the role names: `bug`, `enhancement`, `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Only when the tracker already uses other strings, collect the overrides as `--triage-label ROLE=LABEL` so /sdlc-triage applies the existing labels instead of creating duplicates.

Domain docs need no question: the skills use a root `GLOSSARY.md` and `docs/adr/` (or a `GLOSSARY-MAP.md` in a multi-context repository) and create them lazily.

## 4. Write and validate

Run `SDLC init` with the agreed answers: `--name --id --description --reply-language --language --framework --package-manager --runtime --architecture-style --architecture-summary --architecture-doc --install-cmd --build-cmd --lint-cmd --typecheck-cmd --test-cmd --e2e-cmd --security-cmd --rule --rule-file --in-scope --out-of-scope --allowed-path --protected-path --approver ROLE=NAME --agent --phase --role --tracker --tracker-project --tracker-notes --triage-label ROLE=LABEL`. Repeat a flag for several values; quote every value.

Run `SDLC validate`. Fix each error by re-running init with `--force` and corrected flags. Do not hand-edit around the validator.

Read core `references/DOCUMENTATION-CONTINUITY.md`. Reuse the project's documentation map or write
`docs/documentation-map.md` from core `templates/documentation-map.md`, using existing artifact paths and assessed
applicability. List missing/stale baselines as gaps for planning, with owners; mark future PRD/SRS/design/test/guide
artifacts as planned. Setup does not fabricate requirements or approvals to fill the inventory.

## 5. Review and commit

Show the user a short summary of the config, documentation map/gaps and `git diff --stat`. On their approval,
commit only `.ai-sdlc/project.json AGENTS.md CLAUDE.md .gitignore` and the documentation map written in step 4
with the message `Adopt AI SDLC Core`. Orca worktrees are created from commits, so uncommitted inputs are invisible
to workers.

## 6. Hand over

Run `SDLC doctor` and report every FAIL and WARN with its fix, including the `tracker` line (CLI installed and logged in). Suggest /sdlc-smoke to prove Orca orchestration end to end, then `/sdlc-orchestrate docs/brief.md`. If there is no brief yet, suggest /sdlc-brief first. For feature work in an existing product, the flow is /sdlc-grill → /sdlc-spec → /sdlc-plan → /sdlc-implement; /sdlc-help maps every flow.

When the tracker is GitHub or GitLab and the user kept or set triage labels, offer to create the missing labels (`gh label create` / `glab label create`); creating labels is visible to others, so only on their go-ahead.
