---
name: sdlc-codebase-design
description: Shared vocabulary and principles for designing deep modules - a lot of behaviour behind a small interface, at a clean seam, testable through that interface. Use when designing or reviewing a module's interface, deciding where a seam goes, choosing test seams for a task, looking for deepening opportunities, or making code easier for agents to navigate.
metadata:
  package: ai-sdlc-core
  version: "0.1.4"
---

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. The aim is **leverage** for callers, **locality** for maintainers and testability for everyone. Examples below are TypeScript; apply the same shapes in the project's languages.

## Vocabulary

Use these terms exactly; do not substitute "component", "service", "API" or "boundary". Consistent language is the point.

- **Module**: anything with an interface and an implementation, at any scale: a function, class, package or a slice across tiers. _Avoid_: unit, component, service.
- **Interface**: everything a caller must know to use the module correctly: the signature, but also invariants, ordering constraints, error modes, required configuration and performance characteristics. _Avoid_: API, signature (both too narrow).
- **Implementation**: the code inside a module. Distinct from **adapter**: a small adapter can have a large implementation (a Postgres repository) and a large adapter a small one (an in-memory fake).
- **Depth**: leverage at the interface, the behaviour a caller or test can exercise per unit of interface it has to learn. **Deep**: much behaviour behind a small interface. **Shallow**: the interface is nearly as complex as the implementation.
- **Seam** (Michael Feathers): a place where behaviour can be altered without editing in that place; the _location_ of a module's interface. Where the seam goes is its own decision. _Avoid_: boundary (overloaded with DDD's bounded context).
- **Adapter**: a concrete thing that satisfies an interface at a seam. It names a _role_, not substance.
- **Leverage**: what callers get from depth: more capability per unit of interface learned; one implementation pays back across N call sites and M tests.
- **Locality**: what maintainers get from depth: change, bugs, knowledge and verification concentrate in one place. Fix once, fixed everywhere.

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module may be built from small, swappable internal parts; they are just not part of its interface. It may have **internal seams** used by its own tests as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. Wanting to test _past_ the interface means the module is the wrong shape.
- **One adapter means a hypothetical seam; two adapters mean a real one.** Introduce a seam only when something actually varies across it (typically production plus test).

When designing an interface ask: can I reduce the number of entry points, simplify the parameters, hide more inside?

## Designing for testability

1. **Accept dependencies, do not create them.**
   ```ts
   function processOrder(order, paymentGateway) {}            // testable
   function processOrder(order) { const g = new StripeGateway() } // hard to test
   ```
2. **Return results, do not produce side effects.**
   ```ts
   function calculateDiscount(cart): Discount {}  // testable
   function applyDiscount(cart): void { cart.total -= discount } // hard to test
   ```
3. **Small surface area.** Fewer entry points need fewer tests; fewer parameters need simpler setup.

## Test seams in task contracts

A task contract's `test_seams` names the public interfaces its tests exercise, highest seam first; the fewer seams the better, ideally one. Prefer existing seams to new ones. Give each a one-line note on what it catches and what it misses.

## Going deeper

- **Deepening a cluster of shallow modules given its dependencies**: [DEEPENING.md](DEEPENING.md) (dependency categories, seam discipline, replace-don't-layer testing).
- **Exploring alternative interfaces** for a significant module: [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) (parallel radically different designs, then compare).

## Rejected framings

- Depth as the ratio of implementation lines to interface lines: rewards padding. Depth here is leverage.
- "Interface" as a language keyword or a class's public methods: too narrow; it includes every fact a caller must know.
