# Code-smell baseline

A fixed set of smells from Fowler's _Refactoring_ (chapter 3) that the Standards axis applies even when a project
documents no rules. Two rules bind it:

- **The project overrides.** A documented project rule always wins; where it endorses something the baseline would
  flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation.
  Skip anything a configured linter or formatter already enforces.

Each entry: what it is → how to fix. Match it against the diff only, not the untouched code around it.

- **Mysterious Name**: a function, variable or type whose name does not reveal what it does or holds, or that
  ignores the glossary's term. → Rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape in more than one hunk or file of the change. → Extract the shared shape
  and call it from both.
- **Feature Envy**: a function that reaches into another object's data more than its own. → Move it onto the data it
  envies.
- **Data Clumps**: the same few fields or parameters keep travelling together. → Bundle them into one type.
- **Primitive Obsession**: a primitive or string standing in for a domain concept. → Give the concept its own small
  type.
- **Repeated Switches**: the same switch or if-cascade on the same type recurs across the change. → Polymorphism, or
  one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. → Gather what changes together
  into one module.
- **Divergent Change**: one file or module edited for several unrelated reasons. → Split it so each module changes
  for one reason.
- **Speculative Generality**: abstraction, parameters or hooks for needs the task does not have. → Delete it; inline
  until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. → Hide the walk behind one
  function on the first object.
- **Middle Man**: a class or function that mostly delegates onward. → Remove it and call the real target.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → Replace the
  inheritance with composition.
