# Design it twice

For a significant interface (a new module, a deepening candidate, a public API), explore several radically different
designs before committing. Based on "Design It Twice" (Ousterhout): the first idea is rarely the best. Uses the
vocabulary in [SKILL.md](SKILL.md).

## 1. Frame the problem space

Before spawning anything, write a short explanation for the user (or, in an Orca worker, for the design document):

- the constraints any interface must satisfy;
- its dependencies and their category (see [DEEPENING.md](DEEPENING.md));
- a rough illustrative sketch that grounds the constraints; not a proposal.

Show it, then go straight to step 2; the reader thinks while the designs are produced.

## 2. Produce the designs in parallel

Spawn three or more sub-agents in parallel when the harness supports it (otherwise draft the designs one after another
without letting earlier ones constrain later ones). Each must produce a **radically different** interface. Give each a
separate technical brief (paths, coupling, dependency category, what sits behind the seam), the vocabulary of
[SKILL.md](SKILL.md) and the project's `GLOSSARY.md` terms, plus one constraint:

- Design 1: minimise the interface: one to three entry points, maximum leverage per entry point.
- Design 2: maximise flexibility: support many use cases and extension.
- Design 3: optimise the most common caller: make the default case trivial.
- Design 4 (when cross-seam dependencies matter): design around ports and adapters.

Each design states:

1. the interface: types, entry points, parameters, invariants, ordering, error modes;
2. a usage example from a caller's point of view;
3. what the implementation hides behind the seam;
4. the dependency strategy and adapters;
5. trade-offs: where leverage is high and where it is thin.

## 3. Compare and recommend

Present the designs one after another, then compare them in prose by **depth**, **locality** and **seam placement**.
Finish with your own recommendation and, when parts combine well, a hybrid. Be opinionated: the reader wants a strong
read, not a menu. Record the chosen design and the non-obvious rejected ones as an ADR when the ADR criteria in the
`sdlc-domain-modeling` skill hold.
