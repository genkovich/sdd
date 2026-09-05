---
name: tasks
model: inherit
effort: medium
agents: []
description: >
  Use to break a designed feature into atomic, ≤1-day tasks with a dependency graph, a
  per-task Definition of Done, and a machine-readable tasks.json that the implement engine
  consumes. Triggers on "task breakdown for {slug}", "break down tasks for {slug}",
  "tasks for {slug}", "plan the work for {slug}", "/sdd:tasks {slug}", "розбий на задачі {slug}",
  "декомпозиція {slug}", "список задач". Reads spec.md + sad.md + Accepted ADRs (+ data-model +
  openapi if present), writes docs/features/{slug}/tasks/{_epic,tracker,<task>}.md AND
  docs/features/{slug}/tasks.json. Tracker export to any issue tracker is optional and
  tool-neutral. Hard-refuses if spec.md or sad.md or an Accepted ADR is missing.
---

# Skill: tasks

Task-breakdown generator: atomic tasks ≤1 day, each a separately reviewable change (≤~500 LOC preferred), with a visible dependency graph and a Definition of Done per task. One task = one focused session = one PR. "Build the feature" is not a task — break it down.

A task file is **self-contained**. The rule that governs every task body: **inline the slice the task actually needs, name where it came from, and keep the link as the fallback for when the slice turns out not to be enough.** A task that only points at `spec.md §AC-N` makes the executing agent go and rebuild the context this breakdown already had — it burns its budget on rediscovery and still misses. Alongside the human-facing markdown, this skill emits **`tasks.json`**, the contract the `implement` engine reads to build its dependency DAG.

Every inlined chunk carries a one-line **provenance signature** — `<file> §<section>, <identifier>, verbatim|abridged`, e.g. «`spec.md` §5, AC-02, verbatim» — never «see the spec». The signature is what makes an inline re-checkable: an inline is a snapshot taken at breakdown time, upstream can move after it, and the source always wins.

Task prose (`title` / `dod`, the markdown bodies) follows `artifact_language` — the `tasks.json` machine fields (`id`, `layer`, `deps`, `acs`, `files_hint`, `slug`) and tracker states stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md). An inlined chunk is quoted **verbatim in the language its source artifact is written in**; the signature is not translated.

## Owner

Tech Lead.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** `docs/features/<slug>/spec.md` + `docs/features/<slug>/sad.md` + ≥1 Accepted ADR in `adr/`. Missing → STOP and point at the producing skill (`specify` / `design` / `decide-adr`).
- Read directly (not via an index): spec §5 AC + §6 NFR, sad §5 module boundaries + §6 runtime + §9 ADR index, each Accepted ADR, and — if present — `data-model.md`, `contracts/openapi.yaml` and `screens.md` (the screen manifest `ui` tasks cite).
- (Expected) `sad.md` frontmatter `target_surfaces` — gates which layers appear (step 4). **Absent or empty → warn** («surfaces undeclared — re-run `design`, or proceeding as `backend-service`») **and treat as `[backend-service]`** (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)); never silently emit `ui` tasks for an undeclared surface.

## Protocol

1. **Prereq check (hard).** spec.md + sad.md + ≥1 Accepted ADR, else refuse with the missing one named.
2. **Read upstream directly.** Each task will carry the slices it needs, quoted from the source — so read the source text itself, never a paraphrase of it: the quote goes into the file.
3. **Read the templates from disk, then scaffold output.** **Read [`./templates/task.md`](./templates/task.md) before writing a single task file** — its frontmatter keys and its `## ` section list are the contract, and its `<!-- instruction … -->` comments are the per-section brief. Same for [`./templates/_epic.md`](./templates/_epic.md) and [`./templates/tracker.md`](./templates/tracker.md). **Never write a task from memory of what a task file looks like:** the self-contained format (the `blocks` / `context_budget` keys, the nine sections, the provenance signatures) is younger than most recollections of it, and a remembered shape silently reverts this skill to the link-only tasks it exists to replace. Output: `docs/features/<slug>/tasks/` with `_epic.md` (summary + links + the DAG `flowchart`), `tracker.md` (status table), one `<task-slug>.md` per task. **Validate the `_epic.md` `flowchart` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint; fix before committing).
4. **Identify work-items by layer.** Generic, stack-agnostic layers: `migration` (DB) · `domain` (entities/invariants) · `infra` (repo/persistence) · `app` (service/use-case) · `ports` (handler/API) · `ui` (UI components / screens / view-state — only when a UI surface is declared) · `tests` · `wiring` (composition/DI) · `docs`. **`sad.md` frontmatter `target_surfaces` gates which layers appear** (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)): a `web-frontend` / `mobile-app` / `desktop-app` surface adds `ui` tasks; a backend-only feature emits domain/infra/app/ports (no `ui`); a `cli` feature app/ports; a `worker` domain/infra. Each `ui` task **names the existing components / tokens / styling it reuses** (from `architecture-map.md` §Frontend and the `docs/design-system.md` inventory) — a *new* component is listed only when no existing primitive fits — and, **when `docs/features/<slug>/screens.md` exists, cites the `SCR-NN` id(s) + the states it builds** (the manifest is the task's screen contract; `implement` builds to those states). List 8–20 items by size (see [`../_shared/size-matrix.md`](../_shared/size-matrix.md)).
5. **Atomic check — work size and context size.** Each task ≤1 working day. More → split. **And atomic in context:** count the inlined lines the finished body will carry (the non-empty lines from `## Why (user story)` through `## Acceptance criteria`) against the `context_budget` bands — `S` ≤40 · `M` ≤120 · `L` beyond. An `L` is a split signal: either split the task, or keep it and write the reason on the frontmatter line itself (`context_budget: "L"   # justified: <one line>`). An unjustified `L` fails the step-13 self-check. A change >~500 LOC is a smell that the task is too wide. **Contract-task rule:** a task whose content is changing a shared interface/type that existing implementations must satisfy in a statically-checked language (Go, TS, Java, …) is **not emitted standalone** — it cannot be committed green on its own (the compile-time check breaks every implementer). **Fold it into the first implementing task.** If a split is still warranted (several implementers), mark the pair a **compile-coupled lane**: both tasks list the contract file in `files_hint` (reusing the existing overlap-lane mechanics — no `tasks.json` schema change), so `implement` serializes them and may close them with one shared gate + commit.
6. **Dependency graph.** For each task, `deps: [...]` — and its exact inverse `blocks: [...]`, the ids waiting on this one, so a task shows what it holds up without the reader reconstructing the graph. Identify parallel branches (e.g. the migration and a pure-domain task can start together). This graph IS the DAG `implement` will topologically sort into phases.
7. **Per-task DoD.** Each task is testable: «unit tests for the new validation pass», «migration applies and reverts cleanly», «handler returns the spec'd outcome for AC-03». No subjective «done when I say so».
8. **AC refs + files hint.** Each task lists the `acs` it satisfies (spec §5 IDs) and a `files_hint` — the directories/files it will touch. `files_hint` lets `implement` serialize tasks whose file sets overlap, and `layer: migration` is always serialized (ordered migration sequence); a **compile-coupled pair** (step 5) shares the contract file across both `files_hint`s for the same reason; `layer: ui` is **not** auto-serialized — UI tasks parallelize unless their `files_hint` overlaps. A migration task's `files_hint` is the **staged** pair `docs/features/<slug>/migrations/<NN>_*` (which `implement` promotes into the live `migrations/` when it runs the task) — not a live `migrations/` path.
9. **Fill the task body — self-contained, not a link list.** Every section of [`./templates/task.md`](./templates/task.md) is sourced from a named artifact:
    - *Place in the sequence* ← the DAG (step 6): `deps` and `blocks` by id + title, the wave, and the lane it shares (overlapping `files_hint` / compile-coupled pair).
    - *Why (user story)* ← `spec.md` §4 — the `US-NN` block **verbatim**, then one sentence on what this task contributes to it.
    - *Inlined context* ← `spec.md` §1 committed approach · `spec.md` §6 NFR + `sad.md` §11 for the Hard Rules this task must not violate · `sad.md` §5 for the building block it lives in (boundary + collaborators) · `sad.md` §6 for the runtime steps it implements, error branches included · the decision line of each Accepted ADR that constrains it · `screens.md` `SCR-NN` + the states, for `ui` tasks.
    - *Data delta* ← `data-model.md` — only the entity/columns/constraints/indexes this task touches, plus the **staged** migration pair for `layer: migration`. No schema change → the literal «No DB changes.», never an empty section.
    - *API contract* ← `contracts/openapi.yaml` — only the operations this task implements or calls, with the request/response fields and error codes it owns. No surface → «Internal — no API surface.»
    - *Acceptance criteria* ← `spec.md` §5 — the Given-When-Then of **every** id in `acs`, verbatim. The tests assert these; a paraphrase here becomes a wrong test downstream.
    - *Edge cases* ← the negative branches of those §5 ACs + the `sad.md` §6 error paths, as a case/behaviour table.

    Record the file you just wrote as the task's `file` (repo-relative `docs/features/<slug>/tasks/<task-slug>.md`) — step 11 emits it into `tasks.json`, and that pointer is the only way `implement` reaches this body.

    **Signature.** Each chunk ends with `<file> §<section>, <identifier>, verbatim|abridged` and the link to the full text. **Cutting a long chunk:** keep the sentences that change what gets built (the constraint, the number, the branch, the error code), drop narrative and anything belonging to another task, mark the result `abridged`, keep the link. **Budget:** only this task's ACs, only the fields and endpoints it touches — a task carrying another task's context is as broken as one carrying none. The template also addresses the executing agent directly: an insufficient or code-contradicting slice means go read the named file, never invent the missing part.
10. **Estimate + owner + context budget.** `estimate` S/M/L or hours (how long the work takes); a named owner (or `<TBD lead>`); `context_budget` S/M/L — the honest cost of holding this task, measured (not guessed) as the step-5 count: `S` ≤40 inlined lines and ≤1 extra file to open · `M` ≤120 lines, 2–4 files · `L` beyond, carrying its `# justified:` reason. Adapt `estimate` to the team's sizing if any; the budget bands are fixed.
11. **Emit `tasks.json`** (step contract below) — the same model the markdown reflects, in machine form, at `docs/features/<slug>/tasks.json`. Every entry carries `file`, the repo-relative path of the markdown written in step 9; that pointer is what lets `implement` hand the agent the inlined context instead of sending it back upstream.
12. **Optional tracker export.** If an issue-tracker MCP is connected (Jira / Linear / GitHub Issues / Redmine — whichever the repo uses), offer to create tickets from `_epic.md` + the task files. Otherwise provide copy-paste-ready bodies. Never hard-bind to one tracker.
13. **Self-check.** Every task ≤1 day; DAG acyclic with ≥1 parallel branch where the work allows; `blocks` is the exact inverse of `deps`; DoD per task; every task's *Inlined context* and *Acceptance criteria* are non-empty; no upstream reference without a provenance signature; every task's inlined-line count sits inside its `context_budget` band, and every `L` carries its `# justified:` reason; every `file` points at a markdown that exists on disk; `acs` cover every spec §5 AC; `tasks.json` validates against the contract.
14. **Propose commit + handoff.** `tasks: <slug> (breakdown + tasks.json)`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`tasks/`, `tasks.json`) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)): forward `/sdd:plan-tests <slug>` (on `quick` it always collapses to the inline `## Test plan` in `spec.md`), then `/sdd:implement <slug>`; `plan-tests`' N/A condition = **every task's DoD already names its test** — only then skip target `/sdd:implement <slug>` directly (auto-skip on `quick`, offered `↳ or` on `standard`, never on `full`).

## `tasks.json` contract (read by `implement`)

```json
{
  "slug": "<slug>",
  "tasks": [
    {
      "id": "T1",
      "title": "imperative, specific",
      "layer": "migration|domain|infra|app|ports|ui|tests|wiring|docs",
      "deps": ["T0"],
      "acs": ["AC-01", "AC-02"],
      "dod": "one testable sentence",
      "files_hint": ["path/or/dir/the/task/touches"],
      "file": "docs/features/<slug>/tasks/<task-slug>.md"
    }
  ]
}
```

- **`file` is what makes the inlined context reachable.** It is a **repo-relative** path (same convention as `files_hint` in the same object — not feature-folder-relative), and it is the pointer `implement` follows to hand the executing agent its task file. Without it the engine physically cannot find the markdown, and everything inlined per step 9 is read by humans only. Emit it for **every** task; a task whose `file` does not exist on disk is a hard error, not a warning.
- The markdown task files and `tasks.json` use the **same field names** (`deps`, `acs`, `files_hint`, …) — this skill emits both from one model, so there's no translation layer to drift. Downstream parses the **JSON**: `implement` builds its DAG from `tasks.json` and reads the markdown body through `file`; the frontmatter keys are the human-readable mirror of the same model. **Never rename or drop one on either side** — the mirror is what keeps them auditable against each other.
- `blocks` and `context_budget` stay **markdown-frontmatter only** and are deliberately absent from the JSON: `blocks` is derivable from `deps` (it is its inverse) and `context_budget` is a breakdown-time budget check (step 5 / step 13), not an input to the DAG. **Do not «fix» that by adding them to `tasks.json`.** `file` is the opposite case and no exception to this rule: it adds no content, it is a **pointer** to content the engine otherwise cannot reach.
- `deps` must form a **DAG** (no cycles) and reference only ids present in the file.
- `layer: migration` tasks are serialized by `implement` (ordered migration sequence); `layer: ui` is **not** auto-serialized (UI tasks parallelize); tasks with overlapping `files_hint` are serialized into the same lane regardless of layer — a **compile-coupled pair** (step 5) rides this same mechanism via the shared contract file, and `implement` may commit the pair together (one gate, both `SDD-Task` trailers).
- Which layers are present is gated by `sad.md` frontmatter `target_surfaces` (a UI surface adds `ui`; a backend-only feature has none) → [`../_shared/surfaces.md`](../_shared/surfaces.md).

## Definition of Done

- `tasks/_epic.md` + `tasks/tracker.md` + one `tasks/<task>.md` per task exist.
- Every task file is **self-contained**: a non-empty *Inlined context* and *Acceptance criteria*, a *Data delta* and an *API contract* section that either carry a slice or state the explicit «none», and a provenance signature on every quoted chunk — no bare «see the spec».
- `tasks.json` exists and validates: acyclic `deps`, every `acs` entry is a real spec §5 AC, every task has a `dod`, a `files_hint` and a `file` that resolves to an existing markdown.
- Every task's inlined-line count matches its `context_budget` band; an `L` carries its `# justified:` reason on the frontmatter line.
- Every task ≤1 day with an owner; the DAG shows ≥1 parallel branch where the work allows.
- Every spec §5 AC is covered by ≥1 task's `acs`.
- The step-13 check (atomicity, acyclic DAG, `deps`/`blocks` inverse, per-task DoD, self-containment, signature coverage, context budget, `file` resolves, AC coverage, `tasks.json` contract) is this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **«Build the feature»** as one task. Break into ≥8 atomic ones.
- **5-day monster tasks** → unreviewable. Split.
- **No dependencies** → parallel starts that block each other the next day.
- **No per-task DoD** → «done when I decide».
- **No owner** → nobody starts, or everyone assumes the other will.
- **Hard-binding to one tracker** (Jira-only language). Export is optional and tool-neutral.
- **A task that is only links** («derives from spec §5, see sad §6») — the executing agent goes off to rebuild the context this breakdown already had, burns its budget, and still misses. Inline the slice.
- **An inline with no provenance signature** — an unattributable quote can't be re-checked when upstream moves, so nobody trusts it or updates it.
- **A task file with no `file` pointer in `tasks.json`** — the body is then unreachable by `implement`, every inlined slice is decoration, and the agent goes back to re-reading spec/sad. This is the failure mode the inlining exists to kill.
- **A wholesale paste of a whole upstream document** — the opposite failure, and just as expensive. Inline the slice THIS task needs, cut long chunks and mark them `abridged`, link the rest.
- **A task written from memory instead of from [`./templates/task.md`](./templates/task.md)** — the giveaway is a task with `## Why` / `## What` / `## Notes` instead of the nine sections, or a frontmatter missing `blocks` / `context_budget`. Re-read the template and rewrite.
- **`tasks.json` entries without `file`** — the engine then cannot reach the body, every inlined slice becomes decoration, and the executing agent goes back to re-reading `spec.md`. That is the exact failure this format exists to remove.
- **`tasks.json` out of sync with the markdown** — they must reflect the same model.
- **A task that violates a Hard Rule** from spec §6 / sad §11 (e.g. «edit another module» when the architecture forbids it).

## References & template

- [`./templates/_epic.md`](./templates/_epic.md) · [`./templates/tracker.md`](./templates/tracker.md) · [`./templates/task.md`](./templates/task.md)
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — how many tasks for the feature size.
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — `target_surfaces` (read from `sad.md`) gates which layers appear; a UI surface adds the `ui` layer (not auto-serialized).
