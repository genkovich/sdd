---
status: Living
tool: code               # figma | pencil | code — the single committed source of the design-tool choice (never sdd.local.md: that file is per-developer + gitignored)
figma_file: ""           # tool: figma → the Figma file URL/key the canon lives in; else ""
pen_file: ""             # tool: pencil → the .pen library path (e.g. docs/design/library.pen); else ""
updated_at: "<YYYY-MM-DD>"
---

# Design system — <project name>

> The project's **design canon**, produced once per repo by `design-system` and read by
> `ux-flows` / `screens` / `implement` / `review`. Committed — the tool choice and the inventory
> are team-wide, not per-developer. `architecture-map.md` §Frontend / UI foundation stays the
> inventory of the **code**; this file is the **design-side** canon (tool, posture, tokens,
> component inventory, cross-screen conventions). Refresh via `/sdd:design-system` when the
> foundation changes.

## Platform posture

<!-- instruction: ONE primary posture + a one-line rationale. ux-flows reads this as the default
     platform assumption for every feature; a feature that deviates says so in its ux-flows.md. -->

- **Posture:** <mobile-first | desktop-first | responsive-both> — <why, one line>
- **Breakpoints / device classes:** <the named breakpoints or device classes, if fixed; else "-">

## Design tool

<!-- instruction: where screens are drawn, mirroring the frontmatter `tool`. figma → the file +
     how nodes are referenced; pencil → the .pen file; code → screens.md carries inline markdown
     wireframes. Downstream skills READ this choice — they never re-ask it per feature. -->

- **Tool:** <figma | pencil | code> — <one line why>
- **Library location:** <the Figma file URL / `<path>.pen` / «the in-repo components are the library»>

## Token source

<!-- instruction: where colors / spacing / typography come from. Cite a file (code) or the
     tool-side variables/styles. A screen never re-declares a token inline. -->

- **Colors:** <source> — `<file>` or <tool variables/node>
- **Spacing / sizing:** <source> — `<file>`
- **Typography:** <source> — `<file>`

## Component inventory

<!-- instruction: the reusable primitives screens compose. Brownfield: derived from
     architecture-map.md §Frontend + the code scan — cite file:line per component; tool-backed
     libraries cite the node/URL too. screens.md may only use these names, or declare
     `NEW: <name>` with a why-no-primitive-fits justification (then registered back here). -->

| Component | Source (`file:line` / node / URL) | States it supports | Notes |
|---|---|---|---|
| <Button> | `<path>:<line>` | default / hover / disabled / loading | <…> |

## Interaction & writing conventions

<!-- instruction: the cross-screen rules every new screen follows — one line each. -->

- **Errors:** <toast / inline / page-level — the one pattern this project uses>
- **Empty states:** <the pattern — illustration + CTA / plain text / …>
- **Loading:** <skeleton / spinner / progressive — the one pattern>
- **Validation:** <on-blur / on-submit; how errors attach to fields>
- **Microcopy tone:** <one line>
