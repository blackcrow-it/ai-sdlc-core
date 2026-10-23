---
name: sdlc-debugging
description: Disciplined diagnosis loop for hard bugs, flaky tests and performance regressions - build a feedback loop that goes red on this bug, reproduce and minimise, rank falsifiable hypotheses, instrument, fix with a regression test, clean up. Use when the user says "debug"/"diagnose", reports something broken, throwing, failing or slow, or when a required check fails and the cause is not obvious.
metadata:
  package: ai-sdlc-core
  version: "0.1.1"
---

A discipline for hard bugs. Skip a phase only when you can say why.

Read `GLOSSARY.md` (if it exists) for the domain model of the modules involved, and check the ADRs in `docs/adr/` that touch the area. Inside an SDLC task, every edit (including instrumentation and throwaway harnesses) stays inside the task's `allowed_paths`.

## Redact

You will show commands, output and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against environment variables so credentials stay in the environment, not in what you show. Captured artifacts carry auth headers and personal data: quote only the lines that carry the signal. If the redacted output is not enough to diagnose, say so and ask the user.

## Phase 1: Build a feedback loop

**This is the skill.** With a **tight** pass/fail signal that goes **red** on _this_ bug, you will find the cause; bisection, hypotheses and instrumentation only consume it. Without one, no amount of reading code will save you. Spend disproportionate effort here. Be aggressive, be creative, refuse to give up.

Ways to build one, roughly in this order:

1. **Failing test** at whatever seam reaches the bug (unit, integration, e2e), using the project's configured test command.
2. **HTTP script** (curl or similar) against a locally running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright, Puppeteer) asserting on DOM, console or network.
5. **Replay a captured trace**: save a real (redacted) request, payload or event log and replay it through the code path in isolation.
6. **Throwaway harness**: a minimal subset of the system (one service, mocked externals) that hits the bug path with one call.
7. **Property or fuzz loop**: for "sometimes wrong", run a thousand random inputs and look for the failure mode.
8. **Bisection harness**: when the bug appeared between two known states, automate "build at state X, check" and run `git bisect run`.
9. **Differential loop**: same input through old and new version (or two configs), diff the outputs.
10. **Human-in-the-loop script**, last resort: when a person must click, drive them with [scripts/hitl-loop.template.sh](scripts/hitl-loop.template.sh) so the loop stays structured and their observations come back to you.

**Tighten the loop.** Faster (cache setup, skip unrelated init, narrow the scope), sharper (assert on the exact symptom, not "did not crash"), more deterministic (pin time, seed randomness, isolate the filesystem, freeze the network). A 30-second flaky loop is barely better than none; a 2-second deterministic one is a superpower.

**Non-deterministic bugs**: aim for a higher reproduction rate, not a clean repro. Loop the trigger 100 times, parallelise, add stress, narrow timing windows. 50% is debuggable; 1% is not, so keep raising the rate.

**When you genuinely cannot build a loop**, stop and say so. List what you tried. Ask the human for access to an environment that reproduces it, or for a redacted artifact (log dump, HAR file, core dump, recording with timestamps). Anything in production (instrumentation, data access, config change) is a human decision outside this package's permissions. Do not hypothesise without a loop.

**Phase 1 is done** when you can name **one command** that you have **already run** (show it and its redacted output) and that is:

- [ ] **Red-capable**: it drives the real bug path and asserts the user's exact symptom, so it can go red on this bug and green once fixed;
- [ ] **Deterministic**: same verdict every run (flaky bugs: a pinned, high reproduction rate);
- [ ] **Fast**: seconds, not minutes;
- [ ] **Agent-runnable**: unattended; a human only through the HITL script.

If you catch yourself reading code to build a theory before this command exists, stop: jumping to a hypothesis is the exact failure this skill prevents.

## Phase 2: Reproduce and minimise

Run the loop and watch it go red. Confirm that:

- [ ] it shows the failure the **user** described, not a nearby different one (wrong bug, wrong fix);
- [ ] it reproduces across runs (or at a high enough rate);
- [ ] the exact symptom (message, wrong output, timing) is captured so later phases can verify the fix.

Then **minimise**: cut inputs, callers, config, data and steps one at a time, re-running after each cut, keeping only what is load-bearing. Done when removing any remaining element turns the loop green. A minimal repro shrinks the hypothesis space and becomes the clean regression test.

## Phase 3: Hypothesise

Write **3 to 5 ranked hypotheses** before testing any; a single hypothesis anchors on the first plausible idea. Each must be **falsifiable**:

> If <X> is the cause, then <changing Y> makes the bug disappear / <changing Z> makes it worse.

No prediction, no hypothesis: sharpen it or drop it. **Show the ranked list to the user before testing**; they often re-rank instantly ("we changed #3 yesterday") or have ruled some out. Do not block on it: if the user is away (or you are an Orca worker), proceed with your ranking and include the list in the handoff.

## Phase 4: Instrument

Each probe maps to one prediction from Phase 3. Change **one variable at a time**. Prefer a debugger or REPL over logs, and targeted logs at the boundaries that separate hypotheses over "log everything and grep".

**Tag every debug log** with a unique prefix such as `[DEBUG-a4f2]`, so cleanup is one search.

**Performance regressions**: logs usually mislead. Establish a baseline measurement (timing harness, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5: Fix and regression test

Write the regression test **before** the fix, but only at a **correct seam**: one where the test exercises the real bug pattern as it occurs at the call site. A seam too shallow (single-caller test for a multi-caller bug, a unit test that cannot replay the triggering chain) gives false confidence. **If no correct seam exists, that is the finding**: record it in the handoff as a candidate for `sdlc-codebase-design` deepening.

With a correct seam:

1. Turn the minimised repro into a failing test at that seam (call the Skill tool with "sdlc-tdd" for the test rules).
2. Watch it fail. If you forced red by mutating code or a fixture, diff against a pristine copy to prove the mutation landed.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 loop against the original, un-minimised scenario.

## Phase 6: Clean up and report

Required before declaring done:

- [ ] the original repro no longer reproduces (Phase 1 loop re-run, output shown);
- [ ] the regression test passes, or the missing seam is documented;
- [ ] every `[DEBUG-...]` line is removed (search for the prefix and show the empty result);
- [ ] throwaway harnesses are deleted or moved to a clearly marked debug location;
- [ ] the configured `commands.test` passes in full;
- [ ] the hypothesis that turned out correct is stated in the commit message and the handoff, so the next debugger learns.
