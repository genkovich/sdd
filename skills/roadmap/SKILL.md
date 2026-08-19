---
name: roadmap
model: inherit
effort: medium
agents: [roadmapper]
description: >
  Use to break the overall product idea into incremental steps and keep that decomposition
  living — one docs/roadmap.md with the steps table (source-anchored, sized XS–XL), the
  dependency graph between steps, and the execution path: dependency-respecting waves that
  show what can run in parallel (e.g. in worktrees) and what must wait. Triggers on "roadmap",
  "break this down", "decompose the idea", "what depends on what", "execution plan",
  "/sdd:roadmap", "роадмап", "розбий ідею на кроки", "що від чого залежить", "що можна
  паралельно". Reads idea-brief/PRD (+ design canon and architecture map when present).
  It decomposes and orders — it is NOT a prioritization scorecard and NOT a dated Gantt;
  specify/ship keep step statuses in sync as features move.
---

# Skill: roadmap

The **decomposition layer** between the idea and the per-feature pipeline. SDD builds one feature
at a time under `docs/features/<slug>/`; `roadmap` answers the question that comes *before* any
feature: **how does the overall idea break into steps, what depends on what, and in which order —
and in what parallel lanes — do we walk them.** One living `docs/roadmap.md`, repo-level utility
(like `survey`).

Three load-bearing properties, in priority order:

1. **Steps** — the idea decomposed into incremental, source-anchored slices (each row cites the
   brief/PRD section it comes from; size XS–XL per [`../_shared/size-matrix.md`](../_shared/size-matrix.md)).
2. **Dependencies** — an explicit graph: every edge has a one-line reason (data model, UI zone,
   auth precondition). No edge without a real blocker.
3. **Execution path** — waves that respect the graph: wave N only contains steps whose deps are
   in earlier waves, and steps inside one wave are **conflict-safe in the codebase** (different
   modules / UI zones — so they can run as parallel worktree lanes). Each wave row names the zone.

**Not here:** RICE or any scoring (order IS the prioritization), dates (a decomposition, not a
promise), solution detail (lives in the feature's spec). Question phrasing →
[`../_shared/ask-style.md`](../_shared/ask-style.md); prose follows `artifact_language`, table
structure and the `Status` values stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Whoever owns product direction (PM / lead / the solo maintainer).

## Inputs

- The idea source: `docs/idea-brief.md` / a PRD / a vision note (ask which, if several).
- (Optional) `docs/design-system.md`, `docs/architecture-map.md` — zones for conflict-safety.
- (Optional) existing `docs/features/*/` + existing `docs/roadmap.md` — current statuses.

## Protocol

1. **Locate sources.** Find the idea source (`docs/idea-brief.md` first, then PRD candidates).
   None found → say so and STOP: a roadmap without a source is fiction. If `docs/roadmap.md`
   exists, this run **updates** it (statuses, new steps, re-waving) — never silently rebuilds.
2. **Dispatch the decomposer.** Spawn the [`roadmapper`](../../agents/roadmapper.md) agent —
   `subagent_type: "sdd:roadmapper"` (fallback `general-purpose`, same prompt, per
   [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — naming the source paths, the
   size heuristics pointer, and (updates) the current roadmap + feature statuses. It returns the
   full draft: steps table · mermaid graph · waves (+ ≤5 open decomposition questions).
3. **Review with the owner.** Present the draft **in prose** (steps + waves; the mermaid goes to
   the file, never dumped raw to the terminal — same rule as `design`). Then **one
   `AskUserQuestion` call**: (a) steps to merge/split/drop (multiSelect over flagged candidates
   + the agent's open questions), (b) confirm the wave layout or name what must move. Apply.
4. **Write.** Fill [`./templates/roadmap.md`](./templates/roadmap.md) → `docs/roadmap.md`;
   set `updated_at`.
5. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md), re-read
   from disk, verify **4 items**: (1) every step row carries a source anchor; (2) every
   `Depends on` id resolves to an existing step id, and no step sits in a wave ≤ any of its
   dependencies' waves; (3) statuses ∈ {idea, spec'd, building, shipped} and every spec'd+
   step links an existing `docs/features/<slug>/` (`test -d`); (4) zero dates outside Shipped
   (`\b20\d\d-` scan) and `updated_at` = today. Fix + re-check ≤2 cycles; surface the rest.
6. **Commit + handoff.** Propose commit `roadmap: <what changed>`. **Emit the stage-handoff
   block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) — *What I did*
   (incl. «self-check: 4/4 pass») + *Review* (`docs/roadmap.md`) + *Run next*: `/sdd:specify
   <first unblocked step>` (greenfield) or resume your backbone stage.

## Sync hooks (delivery keeps it current — anti-drift)

- **`specify`** sets the step's `Status` to **spec'd** (and → **building** as implement starts)
  and links `docs/features/<slug>/`. A spec'd feature with no step row gets one appended (source
  anchor = its spec).
- **`ship`** sets `Status: shipped` and adds the date + PR link to **Shipped**.
- Neither hook re-waves the graph — structure changes only happen here, with the owner.

## Definition of Done

- `docs/roadmap.md` exists: steps table (every row source-anchored + sized + status), the
  dependency graph, execution waves that respect the graph with a named zone per parallel step.
- No scores, no dates outside Shipped; `updated_at` current.

## Anti-patterns

- **A prioritization scorecard.** No RICE/effort-value math here — decomposition and order are
  the deliverable. If the owner wants scoring, that's a separate conversation, not this file.
- **A dated Gantt / roadmap-as-promise.** Zero dates outside Shipped; the disclaimer stays.
- **Horizontal steps** («backend», «the UI», «testing») — steps are vertical increments.
- **Phantom dependencies.** An edge you can't justify in one line serializes parallelizable work.
- **Same-wave conflicts.** Two steps touching one code zone in one wave = a guaranteed merge
  conflict between lanes; the zone column exists to catch exactly this.
- **Re-planning shipped work / duplicating specs.** Shipped rows are history; solution detail
  lives in `docs/features/<slug>/`.

## References & template

- [`./templates/roadmap.md`](./templates/roadmap.md) — the decomposition scaffold.
- [`../../agents/roadmapper.md`](../../agents/roadmapper.md) — the decomposer contract (step 2).
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — XS–XL sizing heuristics.
