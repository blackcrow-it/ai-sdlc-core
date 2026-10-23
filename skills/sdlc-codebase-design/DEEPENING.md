# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Uses the vocabulary in
[SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**.

## Dependency categories

Classify the candidate's dependencies first: the category decides how the deepened module is tested across its seam.

1. **In-process**: pure computation, in-memory state, no I/O. Always deepenable: merge the modules and test through
   the new interface directly. No adapter needed.
2. **Local-substitutable**: dependencies with a local stand-in (an embedded or containerised database, an in-memory
   filesystem). Deepenable when the stand-in exists; the suite runs against the stand-in. The seam is internal; there
   is no port at the module's external interface.
3. **Remote but owned (ports and adapters)**: your own services across a network. Define a **port** at the seam; the
   deep module owns the logic and the transport is injected as an adapter. Tests use an in-memory adapter, production
   an HTTP/gRPC/queue adapter. Shape of the recommendation: _"Define a port at the seam, implement an HTTP adapter for
   production and an in-memory adapter for tests, so the logic sits in one deep module even though it is deployed
   across a network."_
4. **True external (mock)**: third-party services you do not control (payments, e-mail, SMS). The module takes the
   dependency as an injected port; tests provide a mock adapter.

## Seam discipline

- **One adapter means a hypothetical seam; two mean a real one.** Do not add a port unless at least two adapters are
  justified. A single-adapter seam is just indirection.
- **Internal versus external seams.** Keep internal seams private to the implementation and its own tests; do not
  expose them through the interface because tests happen to use them.

## Testing: replace, don't layer

- Once tests exist at the deepened module's interface, the old unit tests on the shallow modules are waste: delete
  them in the same task.
- Write the new tests at the deepened interface; it is the test surface.
- Assert on observable outcomes through the interface, never on internal state.
- A test that must change when only the implementation changes is testing past the interface.

## As SDLC tasks

A deepening is a refactor: plan it as its own task (or the prefactor that blocks a feature task) whose acceptance
criteria state that behaviour is unchanged and whose `test_seams` name the new interface. If its blast radius fans
across the codebase, sequence it as expand-contract (see `references/TASK-AUTHORING.md` in the `ai-sdlc-core` skill).
