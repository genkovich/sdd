---
name: roadmap
model: inherit
effort: medium
agents: []
description: >
  Use to break a product idea into incremental steps and keep that decomposition living — one
  docs/roadmap.md with a destination sentence, the steps table (source-anchored, sized XS–XL or
  marked fog), the fog vocabulary (what's in scope but not yet formulated, what never graduates,
  which decisions are still open and who owns them), the dependency graph that owns every edge,
  and the execution path: dependency-respecting waves that show what can run in parallel (e.g. in
  worktrees) and what must wait. Triggers on "roadmap", "break this down", "decompose the idea",
  "what depends on what", "execution plan", "/sdd:roadmap", "роадмап", "розбий ідею на кроки",
  "що від чого залежить", "що можна паралельно". Takes any scope — a whole product, an epic, or a
  single feature. Reads docs/idea-brief.md or a PRD (+ design canon and architecture map when they
  exist; neither is required). It decomposes and orders — it is NOT a prioritization scorecard and
  NOT a dated Gantt; specify/ship keep step statuses in sync as features move.
---

# Skill: roadmap

The **decomposition layer** between the idea and the per-feature pipeline. SDD builds one feature
at a time under `docs/features/<slug>/`; `roadmap` answers the question that comes *before* any
feature: **where are we going, how does the idea break into steps, what depends on what, and in
which order — and in what parallel lanes — do we walk them.** One living `docs/roadmap.md`,
repo-level utility (like `survey`).

**Scope is whatever you bring.** A whole product, one epic, or a single feature — the unit of the
input does not change the unit of the output. A one-feature request gets decomposed the same way;
there are simply fewer steps, and «fewer» is a legitimate answer. The skill never refuses a request
for being too small, and never inflates one to look like a product plan.

Five load-bearing properties, in priority order:

1. **A destination** — one sentence for what is true once the last step ships. Without it the
   steps are a list of work with nothing to be a decomposition *of*.
2. **Steps** — the idea decomposed into incremental, source-anchored slices (each row cites the
   brief/PRD section it comes from; size XS–XL per [`../_shared/size-matrix.md`](../_shared/size-matrix.md)).
3. **A word for what you don't know yet.** `Size` is `XS…XL` **or** `fog`, in the same cell,
   because they answer the same question and only one of them can be true: sizing something nobody
   has formulated yet is how an estimate becomes a lie. Fog lives in `## Not yet specified` until a
   recon pass sharpens it, and then the row trades `fog` for a real size.
4. **Dependencies** — an explicit graph, and the graph is where edges live. Every edge has a
   one-line reason (data model, UI zone, auth precondition). No edge without a real blocker, and no
   second copy of the edges in a column that could disagree with it.
5. **Execution path** — waves that respect the graph: wave N only contains steps whose deps are
   in earlier waves, and steps inside one wave are **conflict-safe in the codebase** (different
   modules / UI zones — so they can run as parallel worktree lanes). Each wave row names the zone.

**Not here:** RICE or any scoring (order IS the prioritization), dates (a decomposition, not a
promise), solution detail (lives in the feature's spec). Question phrasing →
[`../_shared/ask-style.md`](../_shared/ask-style.md); prose follows `artifact_language`, table
structure and the `Status` / `Size` values stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Whoever owns product direction (PM / lead / the solo maintainer).

## Inputs

- **Required** — the idea source: `docs/idea-brief.md` (written by [`interview`](../interview/SKILL.md)) /
  a PRD / a vision note (ask which, if several). This is the only hard input.
- **Optional** — `docs/architecture-map.md` (written by [`survey`](../survey/SKILL.md)): zones for
  conflict-safety. Its absence costs precision in one column, not the roadmap.
- **Optional** — `docs/design-system.md`.
- **Optional** — existing `docs/features/*/` + existing `docs/roadmap.md` — current statuses.

## Protocol

1. **Locate sources.** Find the idea source (`docs/idea-brief.md` first, then PRD candidates).
   None found → say so and STOP: a roadmap without a source is fiction, and the fix is one
   command — `/sdd:interview` writes that brief. **That is the only hard stop.**

   `docs/architecture-map.md` is **optional and never a gate**. Present → its module inventory
   supplies the zones in `## Execution path`. Absent → the roadmap is written anyway, every zone
   that is not an existing path is marked `(new)`, and the handoff says plainly that the waves are
   a first cut worth re-cutting after `/sdd:survey` fills the map. A missing map degrades one
   column; it does not block the decomposition.

   **Greenfield (empty repo, no `docs/features/*` at all): the first step is `scaffold`.** Every
   other step assumes a skeleton to build into — a repo with no module layout, no test harness and
   no migration tooling cannot receive step 1 as written. Its source anchor is the foundation
   section of `docs/architecture-map.md` when the map exists, otherwise the brief itself (the
   project has to exist before anything in the brief can be built).

   If `docs/roadmap.md` exists, this run **updates** it (statuses, new steps, re-waving) — never
   silently rebuilds. A file written before 2.2 carries a `Depends on` column the template no
   longer has; this run folds it away — the edges it held move into the dependency graph, which
   is now the one place edges live. Say so in the handoff, so the dropped column reads as a
   migration rather than lost data.

2. **Decompose — yourself, with the owner.** Cutting an idea into steps is a live exchange with
   the person who holds the intent; it is not delegable, and a subagent standing in for the
   owner's half of it produces a plausible decomposition of a misunderstood idea. Read the sources
   and draft the steps under these rules:

   1. **Every step traces to a source.** Each row cites the section that justifies it
      (`idea-brief.md §2 Problem`, `prd.md §5`). No anchor → the step does not exist. Never invent
      scope the sources don't support.
   2. **Steps are increments, not layers.** A step is a walkable slice that leaves the product
      demonstrably better (UI + API + data as needed) — never «backend», «frontend», «tests».
   3. **Dependencies are edges, not vibes.** An edge names two step ids and has a reason you could
      defend in one line. Edges live in `## Dependency graph` and nowhere else — a step with no
      real blocker has no edge, and inflated dependencies serialize work that could run in parallel.
   4. **Fog is a size value, not a second column.** Ask the Pocock test of each step: *can you
      state the question precisely right now?* — not «can you answer it». No → the step's `Size`
      cell reads `fog`, and the substance goes to `## Not yet specified` as **one area**. Because
      fog and XS–XL share one cell, «the unformulated thing got sized anyway» stops being possible
      to write down. Do NOT pre-chop fog into ticket-sized pieces; that's inventing structure for
      something you haven't looked at yet.
   5. **Size, don't score.** Size every non-fog step XS–XL per
      [`../_shared/size-matrix.md`](../_shared/size-matrix.md). No RICE, no priority numbers, no
      dates — order IS the prioritization.
   6. **Existing state is respected.** A step whose `docs/features/<slug>/` already exists keeps
      its real status (spec'd / building / shipped); never re-plan shipped work.
   7. **Name the destination.** One sentence in `## Destination` for what is true about the product
      once the last step ships. Write it before the steps and check it after: a step that moves
      nothing toward that sentence is scope that snuck in.

3. **Close the AFK questions in parallel.** Decomposition throws off two kinds of question. The
   ones that need the owner's judgment («is this in scope», «which of these matters more») you ask
   in step 4 — nobody can answer them for them. The ones that are just **lookup** («where does X
   live», «what format does the exporter emit», «is there already a library for this», «do steps 3
   and 5 actually touch the same file») are AFK work, and today nobody does them: they get guessed
   at, and the guess becomes a dependency edge.
   For each such question, spawn one subagent — `subagent_type: "general-purpose"` (or the host's
   equivalent per [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md)), tools **Read,
   Grep, Glob, Bash, WebSearch, WebFetch** — **all in one message so they run concurrently**, one
   agent per question. Wrap each with the worker preamble from
   [`../_shared/agent-roster.md`](../_shared/agent-roster.md) and demand a fixed shape back:
   **one line of answer + one citation** (`file:line` or a URL). Uncited → dropped, and the
   question moves to `## Open decisions` with type `research`. Zero AFK questions → skip this step
   and say so; do not manufacture questions to have something to fan out.

4. **Review with the owner.** Present the draft **in prose** (destination + steps + fog + waves;
   the mermaid goes to the file, never dumped raw to the terminal — same rule as `design`), calling
   each step by its name rather than its id. Then **one `AskUserQuestion` call**: (a) steps to
   merge/split/drop (multiSelect over flagged candidates + the questions step 3 could not close),
   (b) confirm the wave layout or name what must move. Apply.

5. **Ask whether the file is worth keeping.** If the pass surfaced **no fog** — every step is
   sized, `## Not yet specified` is empty, `## Open decisions` is empty — then say so and put the
   choice to the owner: a three-row file restating an already-clear plan is one more thing to keep
   current, and the alternative is to build straight from `/sdd:specify <slug>`. **It is their
   call, not a stop.** They want the file as a shared reference — write it. Say the tradeoff once,
   plainly, and take the answer; never refuse to write a roadmap because the request was small or
   clear.

6. **Write.** Fill [`./templates/roadmap.md`](./templates/roadmap.md) → `docs/roadmap.md`;
   set `updated_at`.

7. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md), re-read
   from disk, verify **6 items**:
   1. Every step row carries a source anchor, **and the anchor resolves**: the named document
      exists and the cited section is greppable in it (`grep -F "<section>" <doc>`). Text in the
      column is not evidence — a source anchor nobody checked is how invented scope gets in.
   2. **Every graph edge names two existing step ids**, and no step sits in a wave ≤ any of its
      dependencies' waves. (There is no `Depends on` column to reconcile against: the graph is the
      only place edges live, so an edge is wrong only by naming an id that isn't there or by
      contradicting the waves.)
   3. **`## Destination` is present and is one sentence** — not a bulleted list, not a paragraph of
      goals. One sentence, or the section has failed at the only job it has.
   4. Every zone named in the execution-path table exists as a real path (`test -e`) or is
      explicitly marked `(new)`.
   5. **Every closed enum holds.** `Size ∈ {XS, S, M, L, XL, fog}` — and every `fog` row points
      into `## Not yet specified` and carries no XS–XL anywhere. `Status ∈ {idea, spec'd, building,
      shipped}`, and every spec'd+ step links an existing `docs/features/<slug>/` (`test -d`). In
      `## Open decisions`, `Type ∈ {research, prototype, grilling, task}` and `Owner ∈ {agent,
      human}` — a role, never a person's name. The frontmatter carries exactly the template's keys,
      none invented.
   6. Zero dates outside `## Shipped` (`\b20\d\d-` scan) and `updated_at` = today.

   Fix + re-check ≤2 cycles; surface the rest.

8. **Commit + handoff.** Propose commit `roadmap: <what changed>`.
   Then emit the **stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   (utility variant) — *What I did*
   (incl. «self-check: 6/6 pass» and the fog count) + *Review* (`docs/roadmap.md`) + *Run next*:
   **name the first unblocked step the way the file names it, then give the command on its own
   line, ready to run** — `/sdd:specify <slug>` for that step, `/sdd:scaffold` when the first step
   is the greenfield skeleton, or a recon pass on the top `## Not yet specified` area when the
   first thing in the way is fog rather than work. When the run had no architecture map, add one
   line: the zones are unverified, `/sdd:survey` then a re-run re-cuts the waves.

## Sync hooks (delivery keeps it current — anti-drift)

- **`specify`** sets the step's `Status` to **spec'd** (and → **building** as implement starts)
  and links `docs/features/<slug>/`. A spec'd feature with no step row gets one appended (source
  anchor = its spec). A step cannot go `spec'd` while its `Size` reads `fog` — specifying it *is*
  what clears the fog, so the hook replaces `fog` with a real size in the same edit.
- **`ship`** sets `Status: shipped` and adds the date + PR link to **Shipped**.
- Neither hook re-waves the graph — structure changes only happen here, with the owner.

## Definition of Done

- `docs/roadmap.md` exists: a one-sentence `Destination`, the steps table (every row
  source-anchored + sized XS–XL or `fog` + status), the fog vocabulary (`Not yet specified` ·
  `Out of scope` · `Open decisions`), `Decisions so far` as gists-with-links, the dependency graph
  that owns every edge, and execution waves that respect the graph with a named zone per parallel
  step.
- No scores, no dates outside Shipped; no XS–XL on a `fog` row; `updated_at` current.

## Anti-patterns

- **A prioritization scorecard.** No RICE/effort-value math here — decomposition and order are
  the deliverable. If the owner wants scoring, that's a separate conversation, not this file.
- **A dated Gantt / roadmap-as-promise.** Zero dates outside Shipped; the disclaimer stays.
- **Horizontal steps** («backend», «the UI», «testing») — steps are vertical increments.
- **A roadmap with no destination.** Twelve rows and no sentence saying what they add up to. The
  steps then can't be wrong, because there's nothing for them to be wrong about.
- **Phantom dependencies.** An edge you can't justify in one line serializes parallelizable work.
- **Same-wave conflicts.** Two steps touching one code zone in one wave = a guaranteed merge
  conflict between lanes; the zone column exists to catch exactly this.
- **Sizing the fog.** A one-line step marked `L`, `spec'd`, one edge — and underneath it nine
  undecided things. The size was invented, the status was wrong, and the roadmap's unit was too
  coarse to say so. `Size: fog` is the honest cell.
- **Refusing the small request.** «This is one feature, you don't need a roadmap» is not an
  answer — it is a two-step roadmap. Say the tradeoff, then do what the owner asks.
- **Stopping on a missing architecture map.** The map sharpens the zones; the decomposition does
  not depend on it. Mark the zones `(new)` and say so in the handoff.
- **Restating a decision instead of linking it.** `## Decisions so far` is a gist plus a link to
  where the decision actually lives (the ADR, the spec, the thread). A paragraph of solution
  detail copied in here is a second source of truth that will drift.
- **Delegating the decomposition.** A subagent has the same files and less context than you, and
  it cannot have the exchange with the owner that the cut depends on. Fan out the lookups
  (step 3), keep the judgment.
- **Re-planning shipped work / duplicating specs.** Shipped rows are history; solution detail
  lives in `docs/features/<slug>/`.

## References & template

- [`./templates/roadmap.md`](./templates/roadmap.md) — the decomposition scaffold.
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — XS–XL sizing heuristics.
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — the shared contract every fanned-out
  question-closer follows.
