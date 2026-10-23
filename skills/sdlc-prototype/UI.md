# UI prototype

Several **radically different UI variations** on one route, switched from a floating bottom bar. The user flips
between them in the browser, picks one (or steals parts of each), and the rest is thrown away. Wrong shape for logic
or state questions: use [LOGIC.md](LOGIC.md).

## Two sub-shapes: strongly prefer A

A variant judged next to the real app (real header, sidebar, data, density) is far easier to judge than one in a
vacuum.

- **A: adjustment to an existing page (default).** Render the variants on the existing route, gated by a `?variant=`
  URL parameter. Data fetching, params and auth stay; only the rendered subtree swaps. Something that would naturally
  live inside an existing page (a new section, card or step) is still sub-shape A.
- **B: a new page (last resort).** Only when there is genuinely no existing page to host it. Create a throwaway route
  following the project's routing convention, with `prototype` in its path or filename, same `?variant=` pattern.

## 1. State the question and pick N

Default to **three** variants, at most five. Write the plan in one line at the top of the switcher file:

> "Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route."

## 2. Generate radically different variants

Each variant respects the page's purpose and data, the project's component library and styling system, the UI spec
(`templates/UI-SPEC.md` artifacts) and accessibility basics, and exports a clear name (`VariantA`, `VariantB`, ...).
Variants must differ in **structure**: layout, information hierarchy, primary affordance. Not colour. If two drafts
look alike, redo one with an explicit constraint ("no card grid").

## 3. Wire them together

```tsx
// pseudo-code; adapt to the project's framework
const variant = searchParams.get("variant") ?? "A";
return (
  <>
    {variant === "A" && <VariantA {...data} />}
    {variant === "B" && <VariantB {...data} />}
    {variant === "C" && <VariantC {...data} />}
    <PrototypeSwitcher variants={["A", "B", "C"]} current={variant} />
  </>
);
```

## 4. The floating switcher

A small fixed bar at the bottom centre: **previous** arrow, **label** (`B (Sidebar layout)`), **next** arrow, both
wrapping around.

- Arrows update the URL parameter through the framework's router, so a variant is shareable and survives reload.
- `←` and `→` keys cycle too, except while an input, textarea or contenteditable element has focus.
- Visually distinct from the design under evaluation (high-contrast pill, subtle shadow).
- **Hidden in production builds** (for example gated on `NODE_ENV !== "production"`), so a stray merge cannot ship it.

## 5. Hand it over

Give the URL and the variant keys. The useful feedback is usually "the header from B with the sidebar from C": that
is the real design.

## 6. Capture and clean up

Record which variant won and why (in the UI spec or the task). Fold the winner into the real code, rewritten properly
with tests, then move the full set of variants and the switcher to the throwaway `prototype/<name>` branch. Main keeps
neither the losers nor the switcher.

## Anti-patterns

- Variants that differ only in colour or copy.
- Sharing a layout between variants (a shared header is fine).
- Wiring variants to real mutations: point them at stubs.
- Promoting prototype code straight to production.
