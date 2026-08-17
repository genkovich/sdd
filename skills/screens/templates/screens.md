---
status: draft            # draft | approved
feature_size: "<XS|S|M|L|XL — mirror of .size>"
tool: "<figma | pencil | code — copied from docs/design-system.md frontmatter at generation>"
updated_at: "<YYYY-MM-DD>"
---

# Screens — <feature>

> The canonical **screen manifest** — every screen in every state — produced by `screens` (between
> `api` and `tasks`) and read by `tasks` (each `ui` task cites SCR ids + states), `implement`
> (builds the screen to the declared states) and `review` (the built screen must match this).
> Downstream stages reference **only this manifest** — never the raw Figma / `.pen` file.

## Source

<!-- instruction: where the visuals live, per the design-system tool: figma → the file URL;
     pencil → docs/features/<slug>/screens.pen; code → the wireframes are inline below. Note a
     degradation here if the chosen tool's MCP was unavailable and the run fell back to code. -->

- **Tool:** <figma | pencil | code> (from `docs/design-system.md`)
- **File:** <Figma file URL / `screens.pen` / «inline wireframes below»>

## Screens

<!-- instruction: one ### SCR-NN section per inventory row from ux-flows.md. The states table is
     DERIVED, not invented: default + every state the §5 ACs, the sad.md §6 alt/else branches and
     the contract error responses imply (loading / empty / error / success / validation / …). A
     state class that genuinely doesn't apply → one explicit `N/A: <reason>` row, never silence.
     Components: names from the design-system inventory, or `NEW: <name> — <why no existing
     primitive fits>`. Source-ref per state: figma → node-id; pencil → node id in screens.pen;
     code → the wireframe block below the table. -->

### SCR-01 — <screen name>

| State | Trigger / condition | Components (from the inventory) | Source-ref |
|---|---|---|---|
| default | <…> | <Button, Card, …> | <node-id / «wireframe below»> |
| loading | <…> | <Skeleton> | <…> |
| empty | <…> | <EmptyState> | <…> |
| error | <contract error / AC it shows> | <ErrorBanner> | <…> |

```text
+--------------------------------------+
| <wireframe: SCR-01 default — only in |
|  tool: code mode; one per state that |
|  needs a distinct layout>            |
+--------------------------------------+
```

## New components

<!-- instruction: every `NEW:` component named above — one row each; implement registers each back
     into docs/design-system.md §Component inventory. If none: «None — all screens compose the
     existing inventory.» -->

| Component | Why no existing primitive fits | Registered in design-system |
|---|---|---|
| <name> | <one line> | <pending / done> |
