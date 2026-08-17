---
name: design-system
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to establish the project's design canon — docs/design-system.md: the design-tool choice
  (Figma MCP / Pencil MCP / code-only markdown), the platform posture (mobile-first /
  desktop-first / responsive), the token source, and the reusable component inventory. Once per
  repo, like survey. Triggers on "set up the design system", "design canon", "which design tool",
  "establish the UI foundation", "/sdd:design-system", "налаштуй дизайн-систему",
  "дизайн-канон проєкту", "яким інструментом малюємо". Read by ux-flows (posture) and screens
  (tool + inventory); implement registers NEW components back into it. Utility — not a backbone
  stage; run it before the first UI feature (ux-flows recommends it when absent).
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
5. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read
   the file from disk and verify **4 items**: (1) `tool` ∈ {figma, pencil, code}; (2) the tool ↔
   file fields agree — `figma` ⇒ `figma_file` non-empty, `pencil` ⇒ `pen_file` non-empty, `code` ⇒
   both `""`; (3) every inventory row carries a source anchor (`file:line` or node/URL); (4) no
   `<placeholder>` stubs survive. Fix + re-check ≤2 cycles; surface anything unresolved.
6. **Commit + handoff.** Propose commit `design-system: establish <tool> canon`. Then **emit the
   stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) —
   *What I did* (incl. «self-check: 4/4 pass») + *Review* (`docs/design-system.md`) + *Run next*:
   resume your backbone stage (typically `/sdd:ux-flows <slug>` for the UI feature in flight);
   `/clear` optional.

## Definition of Done

- `docs/design-system.md` exists with `tool` ∈ {figma, pencil, code}, a stated platform posture,
  a token source, and an inventory whose every row cites its source.
- The tool ↔ `figma_file`/`pen_file` fields are consistent; the file is committed (team-wide canon,
  not a local setting).

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

## References & template

- [`./templates/design-system.md`](./templates/design-system.md) — the canon scaffold; inline
  comments are the per-section generation contract.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — the design-tool MCP degradation row.
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — the explorer contract (step 2).
