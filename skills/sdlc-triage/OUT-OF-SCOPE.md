# The `.out-of-scope/` knowledge base

`.out-of-scope/` at the repository root keeps durable records of **rejected enhancement requests**. It gives the
project institutional memory (why a feature was rejected, after the issue is closed) and deduplication (a new request
that matches a past rejection surfaces the earlier decision instead of re-litigating it).

It complements `scope.out_of_scope` in `.ai-sdlc/project.json`: the config lists the boundaries every role must
respect; this directory explains individual rejected requests in depth. When a rejection draws a lasting boundary,
suggest adding one line to `scope.out_of_scope` as well.

## Layout

One file per **concept**, not per issue; several requests for the same thing share a file.

```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

Name files in short kebab-case that someone browsing understands without opening them.

## File format

Write it like a short design note, not a database row: paragraphs, examples, a snippet when it clarifies.

```markdown
# Dark mode

This project does not support dark mode or user-facing theming.

## Why this is out of scope

The rendering pipeline assumes one colour palette resolved at build time. Theming would need a theme context around
the whole component tree, per-component theme-aware styles and persisted user preferences: a large architectural
change that does not serve the project's focus on content authoring. Theming belongs to downstream consumers who
embed the output.

## Prior requests

- #42: "Add dark mode support"
- #87: "Night theme for accessibility"
```

The reason must be substantive and durable: project scope, technical constraints or a strategic decision. "Too busy
right now" is a deferral, not a rejection; it does not belong here.

## Checking it during triage

Read every file in `.out-of-scope/` while gathering context. Match by **concept**, not keyword ("night theme"
matches `dark-mode.md`). On a match, tell the maintainer: "This resembles `.out-of-scope/dark-mode.md`, rejected
because ... Do you still feel the same?" They may:

- **confirm**: append the new issue to "Prior requests", then close it;
- **reconsider**: delete or update the file, and the issue continues through normal triage;
- **disagree that it matches**: continue normal triage.

## Writing to it

Only when an **enhancement** is rejected as `wontfix`:

1. Find a matching file; if one exists, append the issue to "Prior requests".
2. Otherwise create the file with the concept, the decision, the reason and the first request.
3. Commit it (`Record out-of-scope: <concept>`), then comment on the issue linking the file, and close it.

Never write here for an already-implemented request (that is a built feature, and recording it would poison future
dedup checks) or for a rejected bug.

## Changing your mind

Delete or update the file. Old issues stay closed as historical records; the request that triggered the
reconsideration continues through normal triage.
