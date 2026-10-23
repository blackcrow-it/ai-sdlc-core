# Logic prototype

One self-contained HTML file (a **shareable demo**) that lets anyone drive a state model by clicking buttons. Use it
when the question is about **business logic, state transitions or data shape**: things that look reasonable on paper
but only feel wrong once pushed through real cases. One file with nothing to install can go to a designer, a PM, a
Business Analyst or a domain expert, so it speaks their language, not the code's.

Right shape for: "does this state machine handle X then Y?", "can this data model represent the case where...?",
"what should the API feel like before we write it?". Wrong shape for "what should this look like": use [UI.md](UI.md).

## 1. State the question

Before any code, write one paragraph naming the state model and the question, at the top of the demo in a visible
intro (not only a comment), so whoever opens it later can check it answered the right question.

## 2. Isolate the logic in a portable module

Put the logic that answers the question in one `<script>` block written as a small, **pure** module that could be
lifted into the real codebase. Pick the shape the question needs, not the one easiest to wire to a page:

- a **pure reducer** `(state, action) => state` for discrete events over one value;
- a **state machine** with explicit states and transitions when "which actions are legal now" is part of the question;
- **pure functions** over a plain data type when there is no implicit current state;
- a **class or module with a clear method surface** when the logic genuinely owns ongoing state.

No DOM, no `document`, no button handlers inside it: the page calls into the module, never the reverse.

## 3. Build the HTML file

Plain HTML, CSS and JavaScript, everything inline: no framework, no bundler, no server. Every label uses **domain
language** from `GLOSSARY.md`, written in the project's reply language. Top to bottom:

1. **Title and one-line explanation** of what the demo explores (the question from step 1).
2. **Current state** as a readable panel of labelled fields (not a raw JSON dump), re-rendered after every click,
   highlighting what just changed.
3. **Free-play buttons**: one per action, always available, so anyone can poke the model in any order.
4. **Guided walkthroughs**: one tab per **scenario**, each with a plain-language description (the situation and what
   to watch for) and the ordered buttons to press. Starting a walkthrough resets to a known initial state. Choose the
   awkward cases: the happy path, a tricky edge case, an attempt at something that should be illegal.

Clean typography, generous spacing, one accent colour, no animations.

## 4. Hand it over

Send or open the file. The valuable moments are "wait, that should not be possible" and "I assumed X would differ":
those are bugs in the _idea_. Add actions or scenarios when asked.

## 5. Capture

The validated reducer, machine or functions lift into the real module (or the decision lands in the SRS business
rules or a task's acceptance criteria). The HTML shell goes to the throwaway `prototype/<name>` branch as the primary
source.

## Anti-patterns

- Tests: a prototype that needs tests is no longer a prototype.
- The real database: in-memory state unless persistence is the question.
- Generalising: it answers one question.
- Logic tangled with the page: keep the page a thin shell over a pure module.
- A framework, bundler or server: one double-clickable file.
- Shipping the shell: the logic module is the part worth keeping.
