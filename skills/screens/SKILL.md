---
name: screens
model: inherit
effort: high
agents: []
description: >
  Use to produce the canonical screen manifest for a UI feature — every screen in every state
  (default / loading / empty / error / success / validation), with reuse-first component picks —
  written to docs/features/{slug}/screens.md between api and tasks. Draws per the design-system
  tool: Figma MCP into the canon file, Pencil MCP into screens.pen, or inline markdown wireframes
  (code mode — also the degradation when an MCP is unavailable). Triggers on "screens for {slug}",
  "screen states for {slug}", "draw the screens", "mockups for {slug}", "/sdd:screens {slug}",
  "екрани для {slug}", "стани екранів {slug}", "намалюй екрани". States derive from §5 ACs +
  sad.md §6 branches + contract error responses; tasks/implement/review read ONLY the manifest.
  Hard-refuse if sad.md is missing; skipped when target_surfaces declares no UI surface.
---

# Skill: screens

Turns the approved architecture into the **screen manifest** — the one artifact `tasks`,
`implement` and `review` read for what every screen shows in every state. It runs **between `api`
and `tasks`**: by then the states are *derivable*, not invented — `default` plus every state the
spec §5 ACs, the `sad.md` §6 `alt`/`else` branches, and the contract error responses imply
(loading / empty / error / success / validation). Per state it names the **components to reuse**
from the `docs/design-system.md` inventory — a `NEW:` component only with a
why-no-primitive-fits justification. The visuals are drawn per the canon's `tool`; whatever the
tool, **the manifest is the contract** — downstream never reads the raw Figma/`.pen` file.

**Optional by surface:** its N/A condition (no UI surface in `sad.md` `target_surfaces`) lives in
[`../_shared/size-matrix.md`](../_shared/size-matrix.md) and is evaluated by `api`'s handoff
(carried forward when `api` itself is N/A). Invoked directly, it always runs.

Question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md). Manifest prose follows
`artifact_language` — state tokens (`default`/`loading`/…), SCR ids, component names and
source-refs stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Designer + frontend lead. The PM confirms the states match the ACs; `review` later checks the
built screens against this manifest.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/sad.md` — `target_surfaces` + the §6
  branches feed the state derivation. Absent → STOP: «run `design <slug>` first».
- (Expected) `docs/features/<slug>/ux-flows.md` — the SCR inventory this manifest details.
  **Absent → soft**: offer `/sdd:ux-flows <slug>` first, or derive the inventory from spec §4 +
  the SAD with a **noted gap** in the manifest — never a silent invention.
- (Expected) `docs/design-system.md` — the `tool` + the component inventory. Absent → `code` mode
  + recommend `/sdd:design-system` in the handoff.
- (Read) `docs/features/<slug>/contracts/` (error responses → error states), `spec.md` §5 (ACs →
  states), `.size`/`.route` (depth + handoff resolution; defaults stated loudly when missing).

## Protocol

1. **Gate + read.** `test -f docs/features/<slug>/sad.md` → missing = refuse with the pointer
   above. Read `target_surfaces` (no UI surface declared → say so and STOP — this stage is for UI
   features; the upstream handoff normally skips it). Read `ux-flows.md` (or run the soft fallback
   above), `docs/design-system.md` (`tool` + inventory), `sad.md` §6, `contracts/`, spec §5. Read
   `interview_depth` (else medium; `--depth=` wins) — it governs the per-screen confirm volume.
2. **Derive states per screen.** For each `SCR-NN` from the inventory, list the **full state set**:
   `default` + every state the ACs / §6 branches / contract errors imply; a state class that
   genuinely doesn't apply gets one explicit `N/A: <reason>` row. Pick the components per state —
   **from the design-system inventory by name**; a `NEW: <name>` only when no existing primitive
   fits, with the one-line why. Confirm per screen Socratically (medium/hard: one
   `AskUserQuestion` per screen — Accept / Fix / Save-as-OQ / Drop; easy: derive + ledger, ask
   only where the AC↔state mapping is genuinely ambiguous).
3. **Draw per the canon's `tool`.** `figma` → draw into the canon's `figma_file` via the Figma MCP,
   record the node-id per state; `pencil` → `batch_design` into
   `docs/features/<slug>/screens.pen`, record node ids; `code` → inline markdown wireframes in the
   manifest. **Degrade, don't block**: the tool's MCP unavailable in this session → fall back to
   `code` mode and name the degradation in the manifest §Source + the handoff
   (→ [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md)).
4. **Write the manifest + commit.** Fill [`./templates/screens.md`](./templates/screens.md) →
   `docs/features/<slug>/screens.md` (frontmatter `tool` copied from the canon; §Source; one
   `### SCR-NN` section per screen; §New components). Stamp `updated_at`; propose commit
   `screens: <slug> manifest`.
5. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read
   the manifest from disk and verify **4 items**: (1) every `SCR-NN` from `ux-flows.md` has a
   section (inventory fully covered — or the noted-gap fallback is stated); (2) every screen shows
   ≥ `default` + (`error` or `empty`) — or carries the explicit `N/A: <reason>` row; (3) every
   component name exists in the design-system inventory or sits in §New components with a
   justification; (4) for `figma`/`pencil`, every state row carries a source-ref (node-id) — for
   `code`, the wireframes are present. Fix + re-check ≤2 cycles; surface anything unresolved.
6. **Handoff.** Emit the **stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   — *What I did* (tool used or the degradation, «self-check: 4/4 pass») + *Review*
   (`docs/features/<slug>/screens.md`, + `screens.pen` / the Figma file when tool-drawn) + *Run
   next*: `/clear`, then `/sdd:tasks <slug>` (each `ui` task will cite these SCR ids + states).

## Definition of Done

- `docs/features/<slug>/screens.md` exists: §Source per the canon's tool, one section per SCR with
  the derived state table, components reuse-first (`NEW:` only justified), §New components filled
  or explicitly «None».
- States are **derived** — every error/empty state traces to an AC, a §6 branch, or a contract
  error response; nothing invented, nothing silently missing.
- For `figma`/`pencil`: every state has its node source-ref; for `code`: the wireframes are inline.
- The manifest is the only thing downstream needs — `tasks`/`implement`/`review` never open the
  raw design file.

## Anti-patterns

- **Happy-path-only screens.** A screen with just `default` hides exactly the states users hit —
  the error/empty derivation is the point of this stage.
- **Inventing states with no source.** Every non-default state traces to an AC / branch / contract
  error; a state with no origin is scope creep in a costume.
- **Hand-rolling a component the inventory already has** — the reuse rule this pipeline exists to
  enforce; `NEW:` requires the why-no-primitive-fits line.
- **Blocking on a missing MCP.** `code` mode is always available — degrade with a named
  degradation, never refuse the stage over tooling.
- **Making downstream read the design file.** Node-ids are source-refs for humans; the manifest
  carries everything `tasks`/`implement`/`review` consume.
- **Architecture decisions here.** The surface set, SSR-vs-SPA, state management — all `design`'s;
  screens details what was declared, it never re-decides.

## References & template

- [`./templates/screens.md`](./templates/screens.md) — the manifest scaffold; inline comments are
  the generation contract.
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — the N/A condition (no UI surface)
  evaluated by `api`'s handoff.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — the design-tool MCP degradation
  rule (fall back to code mode, named).
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — the surface declaration this stage gates on.
