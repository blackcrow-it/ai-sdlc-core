---
name: sdlc-brief
description: Turn a product or feature idea into docs/brief.md - interview the user in rounds, record only what they decided, list the rest as open decisions, and commit the brief that /sdlc-orchestrate starts from.
argument-hint: "One line about the idea"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.4"
---

Write the project brief for the idea the user described. The brief feeds the discovery phase of /sdlc-orchestrate. It records decisions, not designs.

## 1. Prepare

- `<CORE>` is the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise look in `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). The brief must follow `<CORE>/templates/project-brief.md` exactly: same headings, same order.
- If `docs/brief.md` already exists, read it and offer to refine it. Overwrite only if the user explicitly asks.
- Gather facts yourself: README, existing code and docs, and `.ai-sdlc/project.json` if present (reply language, `scope`, `approvers`). Write the brief in the project's reply language (default Vietnamese).

## 2. Interview in rounds

Call the Skill tool twice, for "sdlc-grilling" and "sdlc-domain-modeling", and use the grilling skill's permitted
interactive question tool, small independent batches and answer tracking. Domain terms the user settles go into
`GLOSSARY.md` as they are resolved. Typical order of the frontier:

1. **Objective and users:** the problem, who has it, the user roles and what each needs to do.
2. **Scope:** what the MVP must deliver and what is deferred or out of scope.
3. **Success criteria:** how the user will know it worked, in observable terms.
4. **Known constraints:** required technology or platform, deadline, budget, data, compliance, environments.
5. **Product owner:** who approves the brief and later the PRD and SRS.

Rules:
- Never invent numbers, legal or compliance duties, integrations or technology choices.
- When the user is unsure or says "later", record an open decision with its owner and what it blocks, and move on.
- Leave architecture and stack choices to the Software Architect. Record them only as constraints the user explicitly states.
- Stop when every template section has either a decided answer or an open decision.

## 3. Write, review, commit

1. Write `docs/brief.md` from the template, keeping the status `draft`.
2. Show the user the full brief and apply their corrections.
3. When the user approves, set the status to `approved by <name> on <YYYY-MM-DD>`, using their own words for the name. Then commit only `docs/brief.md` (and `GLOSSARY.md` if the interview created or changed it) with the message `Add project brief`. Orca worktrees only see committed files.

## 4. Hand over

- No `.ai-sdlc/project.json` yet → recommend /sdlc-setup. Its interview reuses the brief's scope, constraints and owner.
- Otherwise → recommend `/sdlc-orchestrate docs/brief.md` for the full SDLC with Orca workers, or `/sdlc-spec` then `/sdlc-plan` when the brief describes one feature of an existing product.
