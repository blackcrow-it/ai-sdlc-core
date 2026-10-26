---
name: sdlc-spec
description: Turn the current conversation (usually a /sdlc-grill session) into a feature spec at docs/specs/<feature>.md - no new interview, only synthesis, plus one check that the test seams match your expectations - and commit it once you approve.
argument-hint: "Optional: feature name"
disable-model-invocation: true
metadata:
  package: ai-sdlc-core
  version: "0.1.7"
---

Write a feature spec from what this conversation and the codebase already establish. Do **not** interview the user about the feature again; synthesise.

1. `<CORE>` is the `ai-sdlc-core` skill directory next to this skill's base directory (otherwise look in `.claude/skills`, `.agents/skills`, `~/.claude/skills`, `~/.agents/skills`). The spec follows `<CORE>/templates/feature-spec.md`: same headings, same order. Write it in the project's reply language (`.ai-sdlc/project.json`, default Vietnamese).
2. Explore the code the feature touches if you have not already. Use the vocabulary of `GLOSSARY.md` throughout and respect the ADRs in `docs/adr/`. If the conversation contradicts an ADR, say so in the spec instead of silently overriding it. Read core `references/DOCUMENTATION-CONTINUITY.md`, the project's documentation map (or equivalent) and existing PRD/SRS, UI/API/data contracts and guides relevant to the change.
3. Sketch the **test seams**: the public interfaces the feature will be tested through. Prefer existing seams; place new ones at the highest point possible; the fewer the better, ideally one. Call the Skill tool with "sdlc-codebase-design" for the vocabulary. Show the seams to the user and ask whether they match their expectations; this is the only question this skill asks.
4. Write `docs/specs/<feature-slug>.md` with status `draft`. The user stories list is long and covers every aspect of the feature. Anything the conversation left undecided goes to **Open decisions** with an owner; never fill a gap with a guess.
   Fill **Documentation impact** for every category in the continuity reference: canonical path/section, stable
   requirement IDs, required change or no-impact reason, owner and verification. Record missing baselines as gaps
   to plan, not as completed documents. The spec links to the product baseline; it does not replace PRD/SRS updates.
5. Show the spec, apply the user's corrections, and when they approve set the status to `approved by <name> on <YYYY-MM-DD>` (their own words for the name). Commit only the spec with the message `Add spec: <feature>`. Orca worktrees only see committed files.

Then recommend `/sdlc-plan docs/specs/<feature-slug>.md`. If the spec needs requirements, design or architecture work first (new roles, a UI spec, an ADR), recommend `/sdlc-orchestrate docs/specs/<feature-slug>.md` instead.
