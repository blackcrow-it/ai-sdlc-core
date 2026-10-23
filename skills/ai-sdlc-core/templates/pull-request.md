# Pull request body

Use this shape for every pull request an SDLC role opens. Skip preambles, keep prose short, use the glossary's terms,
and link the task (`TASK-NNN`, issue number or Jira key) in the title or first line. The shape follows the "show me"
pattern by Dex Horthy (HumanLayer), as adapted in mattpocock/skills.

```markdown
Task: TASK-NNN <title> (<tracker reference>)

## Summary

<the smallest visual that makes the change clear: a call tree, a shallow file tree, pseudocode, a Mermaid diagram or
a diff sketch of the shape that changed>

## Evidence

- **Before:** <failing test run, wrong output or screenshot>
  **After:** <passing test run, correct output or screenshot>
- Required checks: <command> → exit <code> (one line each, real runs only; anything not run is `not_run`)

## Merge danger

**Door:** <one-way or two-way>

<optional: why>

**Blast radius:** <one word>

<optional: what could break for whom>
```

## Choosing the summary visual

Pick the smallest view that makes the key point; one is usually enough.

- Logic or an algorithm → pseudocode.
- Runtime control flow → a call tree.
- UI structure → a component tree with the state and module boundaries that matter.
- File responsibilities or a broad refactor → a shallow file tree with one comment per entry.
- Interaction or data flow → a Mermaid sequence or flow diagram.
- What changed inside a shape that already exists → a `diff` of that shape (call tree, file tree, state flow).

## Evidence tiers

Screenshots are best for visual changes when the environment can take them. Execution evidence (test output, console
output) is next. A claim without a run is not evidence.

## Merge danger

A **two-way door** is cheap to walk back (revert the merge). A **one-way door** is not: data migrations, deleted data,
published APIs, sent messages. One-way doors need the human approval named in `policies/approval-rules.md`. The
**blast radius** names who or what is affected if it goes wrong (one screen, all API consumers, billing).
