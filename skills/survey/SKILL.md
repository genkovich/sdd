---
name: survey
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to establish the repo's architecture map the rest of the pipeline reads. Two modes: on an
  EXISTING codebase it scans once and persists what's there; on an EMPTY/greenfield repo it runs a
  short, level-adaptive foundation session — picks the stack / folder structure / data approach /
  conventions WITH you (defaults-heavy), fixes them as the foundation + foundational ADRs, and emits
  a scaffold tasks.json that implement materializes into a real skeleton. Triggers on "survey the
  codebase", "map the architecture", "set up a new project", "bootstrap the foundation",
  "/sdd-survey", "вивчи кодову базу", "карта архітектури", "новий проєкт", "заклади фундамент".
  Output: docs/architecture-map.md (+ adr/ + scaffold tasks.json on greenfield). Records
  reflects_commit for staleness; reads, never overwrites, an authored architecture doc.
---

# Skill: survey

The pipeline's anchor on architecture. It produces `docs/architecture-map.md` — the single source of "what the system is" that `specify` (constraints), `design` (matches against it), `data-model`, and `implement` all read instead of re-discovering the code. It runs in one of **two modes**, auto-detected:

- **Brownfield** (the repo has source) → scan it once and persist the **current** architecture.
- **Greenfield** (empty / near-empty repo) → run a short, **level-adaptive foundation session**: pick the stack / structure / data approach / conventions *with* the user (defaults-heavy), fix them as the **foundation** + foundational ADRs, and emit a **scaffold `tasks.json`** that `implement` turns into a real skeleton. Greenfield detail → [`./references/foundation.md`](./references/foundation.md).

Repo-level utility (one map serves every feature). The scan is delegated to [`explorer`](../../agents/explorer.md); question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md); depth → [`../_shared/size-matrix.md`](../_shared/size-matrix.md).

## Owner

Architect / Tech Lead — they own the architecture (brownfield: confirm it reflects reality; greenfield: decide the foundation).

## Inputs

- (Optional) a path/scope hint (default: repo root).
- (Read, never overwrite) an authored architecture doc if present (`docs/architecture.md`, `ARCHITECTURE.md`, root `CLAUDE.md`, ADRs) — a strong input the map reconciles with, never clobbers.

## Protocol

1. **Detect mode + freshness.** If `docs/architecture-map.md` exists and is fresh (its `reflects_commit` ≈ current HEAD) → «map is fresh (reflects `<commit>`). Reuse or refresh?»; STOP on reuse. Else decide the mode: **brownfield** if the repo has source (modules/packages beyond config), else **greenfield** (empty or only scaffolding like a bare `go.mod` / `package.json`).

### Brownfield path (existing code)

2. **Read authored docs first.** Any hand-maintained architecture doc / root `CLAUDE.md` / ADRs → authoritative input; reconcile with it, never overwrite.
3. **Scan via explorer.** Dispatch the [`explorer`](../../agents/explorer.md) agent — `subagent_type: "sdd:explorer"` (`haiku`/`low`, clean-isolated per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)): «Report (a) language + frameworks + versions, (b) top-level module layout + per-module layers, (c) layering / wiring conventions, (d) datastores + access, (e) inter-module comms, (f) cross-cutting conventions (errors, IDs, tests, migrations) with one cited example each, (g) 2–3 representative features as precedents, (h) **if a frontend exists** — the component library / design system, design tokens (colors/spacing/typography), styling approach (Tailwind / CSS-modules / styled-components / …), shared UI primitives, and a representative screen/component as the UI precedent to reuse.» Large repo → fan out per subtree. (Fallback `subagent_type: "Explore"`.)
4. **Synthesize + stamp + validate + write.** Fill [`./templates/architecture-map.md`](./templates/architecture-map.md) (C4 of what exists, module inventory, cited conventions, datastores, **the Frontend / UI foundation if a frontend exists**, precedent guide, constraints) with real `file:line` anchors. Record `updated_at` + `reflects_commit: <short HEAD>`. **Validate the C4 Mermaid per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint; fix before committing). Write + commit `survey: architecture map (reflects <commit>)`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`docs/architecture-map.md`, + scaffold `tasks.json` on greenfield) + *Run next* (`/clear`, then `/sdd-specify <slug>`).

### Greenfield path (empty repo) → [`./references/foundation.md`](./references/foundation.md)

G2. **Calibrate to the person.** One opening `AskUserQuestion` to gauge how the user wants to engage — «pick good defaults, I'll confirm» / «walk me through each choice with explanations» / «let me choose each piece, keep it terse». This sets the dialogue's depth + phrasing (junior → defaults + glossed explanations per [`../_shared/ask-style.md`](../_shared/ask-style.md); senior → terser, more control). Not a product brief.
G3. **Intent (short).** 1–3 questions: what the project is + the kind of capabilities it'll have (e.g. «HTTP API» / «CLI» / «web app»). Enough to choose an architecture — deliberately NOT the feature briefing (that's `specify`, per feature).
G4. **Pick the foundation, defaults-heavy.** At the calibrated depth, choose: stack (language/framework/datastore), architectural style (e.g. hexagonal modules), folder/module structure, data/persistence approach (migration tool, ID strategy), core conventions (errors, tests, CI). Recommend a coherent default set; the user confirms or adjusts. Choice menus + defaults → [`./references/foundation.md`](./references/foundation.md).
G5. **Fix the foundation.** Write `docs/architecture-map.md` as the **established foundation** (mark `mode: greenfield-bootstrap`; the C4 is the *target* baseline) + spawn **foundational ADRs** in `docs/adr/` for the irreversible picks (stack, module style, persistence). Record `reflects_commit`. **Validate the C4 Mermaid per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** before committing.
G6. **Emit the scaffold + hand off.** Write a scaffold `tasks.json` (the skeleton: folder/module structure, a baseline module, the test harness, migration tooling, CI, a `CLAUDE.md`/rules doc) per the contract in [`./references/foundation.md`](./references/foundation.md). Each task's DoD anchors on the **skeleton smoke test** — «the project builds + boots + the empty test suite runs + the migration tool runs». Propose: «foundation fixed — run `implement` to materialize the skeleton» (the wave-of-the-hand hand-off). Commit `survey: greenfield foundation + scaffold plan`.

## Definition of Done

- `docs/architecture-map.md` exists with `updated_at` + `reflects_commit`; an authored doc (if any) was reconciled, never overwritten.
- **Brownfield:** C4 of what exists + module inventory + cited conventions + precedent guide, real anchors (no placeholders).
- **Greenfield:** foundation fixed (stack/structure/data/conventions) at the user's calibrated level + foundational ADRs + a scaffold `tasks.json` whose tasks carry the skeleton smoke-test DoD, ready for `implement`.

## Anti-patterns

- **Re-scanning the repo in every downstream skill** — the point is to scan once; others read the map (drift detection is the only re-read, of real domain files).
- **Overwriting a hand-maintained `docs/architecture.md`** — survey writes its own map and reconciles.
- **A map with no `reflects_commit`** — it silently rots; nobody knows it's stale.
- **Greenfield: a full product brief.** The foundation session picks the *architecture*, not the features — the idea/briefing is `specify`'s job, per feature. Keep it to intent + foundation choices.
- **Greenfield: ignoring the person's level.** A junior gets defaults + plain-language explanations; a senior gets control + terseness. One calibration question sets this — don't fire a senior-level wall of choices at a first-timer.
- **Placeholders / guessed layout** — cited or `UNKNOWN`; a fictional map is worse than none.

## References & template

- [`./references/foundation.md`](./references/foundation.md) — greenfield: the calibration question, level-adaptive depth, the stack/structure/convention choice menus + defaults, foundational-ADR list, and the scaffold `tasks.json` contract.
- [`./templates/architecture-map.md`](./templates/architecture-map.md) — output scaffold (same file for current OR foundation; a `mode:` marker distinguishes).
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — the explorer contract.
