---
name: sdlc-prototype
description: Build a throwaway prototype that answers one design question - a single shareable HTML file to push a state model or business logic through hard cases, or several radically different UI variations switchable on one route. Use when a requirement, state machine, data shape or screen is hard to settle on paper and the user (or a designer, PM or domain expert) needs something concrete to react to.
metadata:
  package: ai-sdlc-core
  version: "0.1.2"
---

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify the question from the user's prompt, the task contract or the surrounding code, or ask if the user is around:

- **"Does this logic or state model feel right?"** → [LOGIC.md](LOGIC.md): one self-contained HTML file with free-play buttons and guided walkthroughs that push the model through cases hard to reason about on paper, drivable by a non-developer.
- **"What should this look like?"** → [UI.md](UI.md): several radically different variations on one route, switched by a URL parameter and a floating bar.

The two branches produce very different artifacts, so choosing wrong wastes the prototype. If the question is ambiguous and nobody can answer, pick the branch that matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules for both

1. **Throwaway from day one, and visibly so.** Put it next to where the real code will live so context is obvious, but name it so any reader sees it is a prototype (`prototype-checkout-states.html`, `?variant=`). Follow the project's routing and layout conventions; do not invent a new top-level structure. Inside an SDLC task, stay inside the task's `allowed_paths`.
2. **Trivial to run.** One command from the project's task runner, or one HTML file to double-click.
3. **No persistence by default.** State lives in memory. If the question is about persistence, use a scratch database or file named `PROTOTYPE-wipe-me`, never shared or production data.
4. **Skip the polish.** No tests, no error handling beyond what keeps it runnable, no abstractions.
5. **Surface the state.** After every action (logic) or variant switch (UI), show the full relevant state.
6. **Capture it.** Fold the validated decision into the real artifact (SRS rule, UI spec, ADR, task acceptance criterion). Keep the prototype as a **primary source** on a throwaway branch `prototype/<name>` (never merged), and point at that branch from the task, spec or issue. Record the verdict and the question it settled. The main branch keeps only the decision.
