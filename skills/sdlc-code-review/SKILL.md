---
name: sdlc-code-review
description: Independently review the changes since a fixed point on three separate axes - Spec (does it do what the task contract asked, inside its scope?), Standards (does it follow the project's coding rules plus a code-smell baseline?) and Risk (correctness, security, compatibility, data, test quality) - with findings backed by evidence and a single approve or request-changes verdict. Use before accepting a task, merging a branch or releasing, or when asked to review a branch, PR or "changes since X".
metadata:
  package: ai-sdlc-core
  version: "0.1.3"
---

# Code review

Primary skill of the Code Reviewer. The reviewer is never the author of the change: if you wrote any of it, stop and say so. `SDLC` = `python "<CORE>/scripts/sdlc.py"` (locate `<CORE>` with `sdlc.py where`).

## 1. Pin the fixed point

Use the base the task or user gives (a commit, branch, tag, `main`). Without one, use the merge-base with the default branch from `.ai-sdlc/project.json` and say so. Confirm it resolves (`git rev-parse <base>`) and the diff is not empty (`git diff <base>...HEAD --stat`) before anything else: a bad ref or an empty diff fails here, not inside three sub-reviews. Note the commits (`git log <base>..HEAD --oneline`).

## 2. Gather the sources

- **Spec source**, in order: the task contract named by the task or the commit messages (`TASK-NNN`, issue references), fetched with the tracker's "Read" recipe; a path the user gives; a spec under `docs/specs/` matching the branch. If none exists, the Spec axis reports "no spec available" instead of guessing.
- **Standards sources**: `coding_rules.rules` and `coding_rules.files` in `.ai-sdlc/project.json`, plus `CODING_STANDARDS.md`, `CONTRIBUTING.md` and similar files when present, and the code-smell baseline in [SMELLS.md](SMELLS.md).
- **Evidence**: CI results for the head commit, or run the contract's `required_checks` yourself with the configured commands. A claim in the author's handoff is not evidence until a check output backs it.
- **Documentation**: read core `references/DOCUMENTATION-CONTINUITY.md`, the documentation map, impact assessment,
  canonical baselines and changed requirement-to-evidence links. Run `SDLC docs-check --task <contract> --base <base>`.
  Give these sources and the result to the Spec reviewer: check omitted impacts, no-impact reasoning, actual owned
  updates, stable IDs, approvals/revisions and integrated reconciliation. Missing/stale required documentation or
  broken traceability is a blocker/major finding; passing structural checks alone cannot justify approval.

## 3. Review the three axes separately

Run each axis as its own sub-agent with a fresh context when the harness supports it (in parallel, in the foreground), so no axis pollutes another; otherwise review them one after another and finish each report before starting the next. Give each one the diff command, the commit list and only its own sources (paste SMELLS.md into the Standards brief in full).

**Spec**: "Report (a) acceptance criteria missing or only partly implemented; (b) behaviour in the diff nobody asked for (scope creep); (c) criteria that look implemented but wrongly; (d) the result of `SDLC scope --task <contract> --base <base>` (paths outside `allowed_paths` or inside protected paths are blockers); (e) whether each acceptance criterion is proven by a test at one of the contract's `test_seams`. Quote the criterion for each finding. Under 400 words."

**Standards**: "Report, per file or hunk, (a) every violation of a documented project rule, citing the file and rule; (b) each smell from the baseline that you spot, named and quoted. Documented rules may be hard violations; baseline smells are always judgement calls, and a documented project rule overrides the baseline. Skip anything a configured linter or formatter already enforces. Under 400 words."

**Risk**: "Report (a) correctness bugs with a concrete failing input or sequence; (b) security: authentication, authorisation, input validation, injection, secrets or personal data in code, logs or tests; (c) backwards compatibility of public interfaces, APIs, schemas and configuration; (d) data risks: migrations, deletions, irreversible operations (one-way doors); (e) test quality against the `sdlc-tdd` anti-patterns (implementation-coupled, tautological, mocks of internal collaborators) and checks that were skipped or reported without a run. Under 400 words."

## 4. Report

Present the three reports under `## Spec`, `## Standards` and `## Risk`, verbatim or lightly cleaned. Do **not** merge or rerank findings across axes: a change can pass one axis and fail another, and separate reports stop one axis masking the other.

Inside each axis, classify every finding as **blocker**, **major** or **minor**, with `path:line`, the evidence and a concrete fix.

Finish with:

- one line per axis: number of findings and the worst one;
- the checks you relied on, with command and exit code (or CI run reference);
- the verdict: **request changes** if any axis has a blocker or a major finding, a hard standards violation, a failed or `not_run` required check, or a failed scope check; otherwise **approve**, with the residual risks listed.

Hand off per core `references/HANDOFF.md`. Approving moves the task towards acceptance; it is not the acceptance itself, which belongs to the gate owner.

## Rules

- Never approve your own work, and never override required CI or branch protection.
- Review the code, not the author's narrative; quote what you saw.
- Apply core `policies/permissions.md`, `policies/approval-rules.md` and `policies/quality-gates.md` of the `ai-sdlc-core` skill and the project rules in `.ai-sdlc/project.json`.
