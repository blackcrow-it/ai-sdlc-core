# ADR format

ADRs live in `docs/adr/` (or the context's `docs/adr/` in a multi-context repository) and are numbered sequentially:
`0001-slug.md`, `0002-slug.md`. Take the highest existing number plus one. Create the directory lazily.

## Template

```md
# {Short title of the decision}

{One to three sentences: the context, what was decided, and why.}
```

That is enough. An ADR may be a single paragraph: its value is recording _that_ a decision was made and _why_.

## Optional sections

Add them only when they carry real information:

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`), when decisions get revisited.
  An ADR that needs an approver from `sdlc.approvers` (for example `tech_lead`) stays `proposed` until that person
  accepts it; record their name and the date, never assume acceptance.
- **Considered options**, when the rejected alternatives are worth remembering.
- **Consequences**, when non-obvious downstream effects must be called out.

## When to write one

All three must hold:

1. **Hard to reverse**: changing your mind later has a meaningful cost.
2. **Surprising without context**: a future reader will wonder "why on earth was it done this way?"
3. **The result of a real trade-off**: there were genuine alternatives and one was picked for specific reasons.

Easy to reverse: skip it, you will just reverse it. Not surprising: nobody will ask. No real alternative: nothing to
record beyond "we did the obvious thing".

### What usually qualifies

- **Architectural shape**: "monorepo"; "write model event-sourced, read model projected into Postgres".
- **Integration patterns between contexts**: "Ordering and Billing talk through domain events, not synchronous HTTP".
- **Technology with lock-in**: database, message bus, auth provider, deployment target; not every library.
- **Boundary and scope decisions**: "Customer data is owned by the Customer context; others reference it by ID".
  Explicit no-s are as valuable as yes-s.
- **Deliberate deviations from the obvious path**: "manual SQL instead of an ORM because X". These stop the next
  engineer from "fixing" something that was deliberate.
- **Constraints invisible in the code**: "no AWS for compliance reasons"; "p95 under 200 ms by partner contract".
- **Non-obvious rejected alternatives**: if GraphQL lost to REST for subtle reasons, record it before someone
  proposes GraphQL again.
