---
name: sdlc-tdd
description: Test-driven development with a red-green loop, one vertical slice at a time, at pre-agreed test seams. Use when building a feature or fixing a bug test-first, when the user mentions "TDD" or "red-green-refactor", when implementing an SDLC task contract, or when writing integration tests.
metadata:
  package: ai-sdlc-core
  version: "0.1.6"
---

TDD is the **red → green** loop. This skill is the reference that makes the loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns and the rules of the loop. Consult every section before and during the loop, not after.

Read `GLOSSARY.md` (if it exists) so test names and interface vocabulary use the project's domain language, and respect the ADRs in `docs/adr/` that touch the area.

## What a good test is

Tests verify **behaviour through public interfaces**, not implementation details. The code may change entirely; the tests should not. A good test reads like a specification: "user can check out with a valid cart" names a capability and survives refactors because it does not care about internal structure. Examples: [tests.md](tests.md). Mocking: [mocking.md](mocking.md).

## Seams: where tests go

A **seam** is the public boundary you test at. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing a test, know the seams under test:

- **Implementing an SDLC task contract**: its `test_seams` field is the agreement. Need a seam it does not list? In an Orca worker, ask the Orchestrator; in a session with the user, ask the user. Never test at an unconfirmed seam.
- **Otherwise**: write down the seams you propose, each with a one-line note on what it catches and what it misses, and confirm them with the user first.

When the shape of the interface itself is in question (how deep the module is, where the seam belongs), call the Skill tool with "sdlc-codebase-design" for the vocabulary.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks on a refactor although behaviour did not change.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`), so it passes by construction. Expected values come from an independent source of truth: a known-good literal, a worked example, the acceptance criterion.
- **Horizontal slicing**: all tests first, then all implementation. Bulk tests verify _imagined_ behaviour and the _shape_ of things, go insensitive to real change, and lock in structure before you understand it. Work in **vertical slices**: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test, run it and watch it fail **for the expected reason** (the assertion, not an import or syntax error). Then write only enough code to pass it. No speculative features, no anticipating future tests.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Run what the project configured.** Use the commands in `.ai-sdlc/project.json` (`commands.test`, `commands.typecheck`, `commands.lint`) exactly as written; narrow them to one test file while cycling, and run the full configured suite once at the end.
- **Keep the evidence.** For each slice, note the red run and the green run (command and exit code). The handoff cites real runs only; a test you did not run is `not_run`, never `pass`.
- **Refactoring is not part of the loop.** It belongs to review (the `sdlc-code-review` skill) or to its own task, not to the red → green cycle.

## Done

Every acceptance criterion of the task (or every behaviour the user asked for) is covered by at least one test at an agreed seam that you have seen go red and then green, and the full configured test command passes.
