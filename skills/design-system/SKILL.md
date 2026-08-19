---
name: design-system
model: inherit
effort: medium
agents: [explorer, pen-keeper]
description: >
  Use to establish the project's design canon — docs/design-system.md: the design-tool choice
  (Figma MCP / Pencil MCP / code-only markdown), the platform posture (mobile-first /
  desktop-first / responsive), the token source, and the reusable component inventory. Once per
  repo, like survey. Triggers on "set up the design system", "design canon", "which design tool",
  "establish the UI foundation", "/sdd:design-system", "налаштуй дизайн-систему",
  "дизайн-канон проєкту", "яким інструментом малюємо". Read by ux-flows (posture) and screens
  (tool + inventory); implement registers NEW components back into it. On tool: pencil it also
  bootstraps the .pen library itself — creates the file, walks the user through opening it, and
  seeds tokens + a foundations frame via the pen-keeper agent. Utility — not a backbone stage;
  run it before the first UI feature (ux-flows recommends it when absent).
---

# Skill: design-system

The design-side twin of `survey`: **once per repo** it fixes the **design canon** in
`docs/design-system.md` — which tool screens are drawn with (`figma` / `pencil` / `code`), the
platform posture, where tokens come from, and the component inventory new screens must compose.
`architecture-map.md` §Frontend stays the inventory of the **code**; this file is the **design**
canon the design pipeline (`ux-flows` → `screens`) and `implement`/`review` read. The tool choice
is **committed here** — never in `.claude/sdd.local.md` (that file is per-developer and gitignored;
the canon is team-wide).

Question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md). Canon prose follows
`artifact_language` — frontmatter keys/values (`tool:`, `figma_file:`, …), component names and
file anchors stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Whoever owns the product's look (designer / frontend lead / the solo maintainer).

## Inputs

- (Optional) `docs/architecture-map.md` §Frontend / UI foundation + the `frontend:` machine key —
  the code-side inventory this canon cites.
- (Optional) an existing `docs/design-system.md` — updated, never silently overwritten.
- The design-tool MCPs available in this session (Figma / Pencil), if any → detected in step 3.

## Protocol

1. **Check existing.** If `docs/design-system.md` exists, show its `tool` + posture + inventory
   summary and ask: reuse as-is (STOP — nothing to do) / update (continue, edits land in place) /
   rebuild. Never overwrite silently.
2. **Scan the code side.** Read `architecture-map.md` §Frontend / UI foundation + the `frontend:`
   key. Map absent, stale, or `frontend: ""` on a repo that visibly has UI code → dispatch the
   [`explorer`](../../agents/explorer.md) agent — `subagent_type: "sdd:explorer"` (fallback
   `subagent_type: "Explore"`, per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) —
   for the component library / tokens / styling approach / shared primitives, each with a
   `file:line`. A repo with no UI code at all is fine — the canon can start tool-side or empty
   (greenfield: the inventory grows as `implement` registers components).
3. **Detect tools + ask ONE question set.** Detect which design-tool MCPs the session actually has
   (Figma / Pencil — probe the available tools, don't assume). Then **one `AskUserQuestion` call**
   (up to 3 questions in it, phrased per [`../_shared/ask-style.md`](../_shared/ask-style.md)):
   **(a) tool** — options from what's detected, the detected one first as «(Recommended)»; `code`
   (markdown wireframes in `screens.md`) is **always** offered — it needs no MCP and never blocks;
   **(b) platform posture** — mobile-first / desktop-first / responsive-both;
   **(c) token source** — the code file(s) found in step 2 / the tool's variables / «none yet».
4. **Write the canon.** Fill [`./templates/design-system.md`](./templates/design-system.md) →
   `docs/design-system.md`: frontmatter `tool` + `figma_file`/`pen_file` (the one matching the
   tool; the other stays `""`), posture, token source, the component inventory — each row citing
   `file:line` (code) or the node/URL (tool-side) — and the cross-screen conventions.
5. **Bootstrap the tool library** (`tool: pencil` only — figma links an existing file, `code`
   needs nothing). The canon naming a `pen_file` that doesn't exist or is an empty stub is the
   #1 way this skill «did nothing» — so materialize it:
   a. **File.** Absent → write the minimal stub to `pen_file` (`{"version": "2.17", "children": []}`).
   b. **Open + verify.** The Pencil MCP **ignores `filePath`** — it writes into whatever document
      is active in the app. Ask the user to open the file (macOS: `open -a Pen <pen_file>`), then
      verify via `get_app_state` that the active canvas IS `pen_file`. Mismatch → stop and repeat
      the ask; **never write into a foreign document**.
   c. **Seed.** Dispatch the [`pen-keeper`](../../agents/pen-keeper.md) agent —
      `subagent_type: "sdd:pen-keeper"` (no fallback: without the Pencil MCP this step degrades
      to `code` mode per [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md)) — with the
      canon path, `pen_file`, and the token source files. It re-checks the active document, seeds
      the variables (light + dark), ensures the foundations frame, and returns a reconcile report.
   d. **Persist.** Relay the report's user actions — always «**Cmd+S in Pencil**»: the app holds
      changes in memory and the MCP cannot save; confirm the file on disk actually changed
      (size/mtime) before calling the canon done.
6. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read
   the file from disk and verify **5 items**: (1) `tool` ∈ {figma, pencil, code}; (2) the tool ↔
   file fields agree — `figma` ⇒ `figma_file` non-empty, `pencil` ⇒ `pen_file` non-empty, `code` ⇒
   both `""`; (3) every inventory row carries a source anchor (`file:line` or node/URL); (4) no
   `<placeholder>` stubs survive; (5) `tool: pencil` ⇒ the `pen_file` exists on disk and is larger
   than the empty stub (step 5 ran and the user saved). Fix + re-check ≤2 cycles; surface anything
   unresolved.
7. **Commit + handoff.** Propose commit `design-system: establish <tool> canon` (on pencil —
   including the seeded `pen_file`). Then **emit the
   stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) —
   *What I did* (incl. «self-check: 4/4 pass») + *Review* (`docs/design-system.md`) + *Run next*:
   resume your backbone stage (typically `/sdd:ux-flows <slug>` for the UI feature in flight);
   `/clear` optional.

## Definition of Done

- `docs/design-system.md` exists with `tool` ∈ {figma, pencil, code}, a stated platform posture,
  a token source, and an inventory whose every row cites its source.
- The tool ↔ `figma_file`/`pen_file` fields are consistent; the file is committed (team-wide canon,
  not a local setting).
- `tool: pencil` ⇒ the `.pen` library exists on disk, holds the seeded token variables, and the
  user has saved it (the canon never points at a file that was never created).

## Anti-patterns

- **The tool choice in `sdd.local.md`.** That file is per-developer and gitignored — two teammates
  would draw in different tools. The canon is committed, in this one file.
- **Re-asking the tool per feature.** `ux-flows`/`screens` read the canon; the question is asked
  once, here.
- **Duplicating `architecture-map.md` §Frontend.** The map inventories the code; this file cites it
  and adds the design-side canon — never a second copy of the same rows.
- **Blocking on a missing MCP.** No Figma/Pencil in the session → `code` mode is always available;
  degrade, don't block (→ [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md)).
- **An inventory with no anchors.** A component row that cites nothing is a guess — cite `file:line`
  or the tool node, or leave it out.
- **A canon that names a `pen_file` nobody created.** `tool: pencil` without step 5 is a dangling
  pointer — downstream `screens` opens nothing and silently degrades.
- **Writing into whatever document is open.** The Pencil MCP targets the ACTIVE document and
  ignores `filePath` — skipping the `get_app_state` identity check pollutes a foreign file.
- **Assuming the MCP saved to disk.** It edits in-memory; only the user's Cmd+S persists. Verify
  the file changed before committing.

## References & template

- [`./templates/design-system.md`](./templates/design-system.md) — the canon scaffold; inline
  comments are the per-section generation contract.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — the design-tool MCP degradation row.
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — the explorer contract (step 2).
- [`../../agents/pen-keeper.md`](../../agents/pen-keeper.md) — the .pen reconcile contract (step 5).
