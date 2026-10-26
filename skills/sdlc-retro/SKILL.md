---
name: sdlc-retro
description: Run a retrospective on a coding session or an SDLC Run and propose improvements to the agents' environment - navigation pointers, automated checks, coding rules, steering files, tooling, information access - most severe first; nothing changes until you approve.
argument-hint: "Optional: which session, Run or task to look back on"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.6"
---

Run a **retrospective**: suggest improvements to the agents' **environment** so future sessions and Runs go better. The subject is the environment, not the code that was written.

## 1. Read the primary sources

Default to the current session. When the user names another session, Run or task, read its sources: the session log on this machine, the Orca Run (`orca orchestration` read-only commands), the task contracts and their tracker comments, handoff reports, review reports, commits and CI output. Note every point where an agent was slow, wrong, blocked, corrected by the human, or spent a retry.

Locate `<CORE>` (the `ai-sdlc-core` skill directory next to this skill's base directory, otherwise `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`) and read `.ai-sdlc/project.json`, `AGENTS.md`, `CLAUDE.md` and the project's rule files so you know what the environment already says.

## 2. Find candidates

- **Navigation**: did agents struggle to find the right files or hit hidden dependencies between files? A one-line **navigation pointer** (in `architecture.docs`, a rule file, or a component entry in `architecture.components`) may fix it.
- **Automated checks**: could a check have caught a mistake an agent made: lint, typecheck, tests, a filesystem rule? Read the repository's own check commands and CI first: a check that exists but is not in `.ai-sdlc/project.json` `commands`, or is silently broken, is the finding, not a reinvention. A repository with **no guardrail** (no pre-commit hook and no CI job running lint, typecheck and tests) is itself a finding.
- **Coding rules**: should the reviewer enforce a new rule, or drop or clarify one? Classify first. A **mechanical** violation (a banned API, an import shape, a file-location rule) gets a deterministic check in the repository's linter, a pre-commit hook or CI: build the check rather than write the rule. Only **judgement calls** (cross-file consistency, matching the surrounding style) go into `coding_rules` or a rule file, because review reads those.
- **Task contracts**: were acceptance criteria vague, test seams missing or wrong, `allowed_paths` too wide or too narrow, dependencies false? Propose the authoring rule that would have prevented it.
- **Steering files**: is `AGENTS.md` or `CLAUDE.md` (outside the managed AI SDLC block) large? Move instructions into rule files or automated checks and keep the steering file to pointers.
- **No-ops**: instructions agents already follow by default, which only cost context.
- **Tool economy**: expensive or token-hungry tool calls that a narrower command or script would replace.
- **Information access**: a crucial fact the agent could not see (dev server logs, read-only access to a service, a missing doc).
- **Core gaps**: a problem in AI SDLC Core itself (a role, workflow, policy or skill). Draft an issue text for the core repository instead of patching the installed copy, which is replaced on upgrade.

## 3. Present

List the candidates **most severe first**. For each: what happened (quote the evidence), the proposed change, where it goes, and whether it is a check, a rule, a pointer or a deletion.

## 4. Apply only what the user approves

Implementation agents carry the most context pressure and reviewers the least, so standards belong to review and to automated checks, not to longer implementation prompts.

- `.ai-sdlc/project.json` is protected from workers; edit it here only with the user's approval, then run `SDLC validate` (`SDLC` = `python "<CORE>/scripts/sdlc.py"`) and `SDLC upgrade` if the managed blocks need refreshing.
- Never edit the managed block between `<!-- ai-sdlc-core:begin -->` and `<!-- ai-sdlc-core:end -->` by hand.
- CI workflow files are protected paths: propose the change as a diff for the human to apply.
- Commit each approved change separately with a message that names the problem it prevents.
