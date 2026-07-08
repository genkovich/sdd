---
name: tasks
model: inherit
effort: medium
agents: []
description: >
  Use to break a designed feature into atomic, ≤1-day tasks with a dependency graph, a
  per-task Definition of Done, and a machine-readable tasks.json that the implement engine
  consumes. Triggers on "task breakdown for {slug}", "break down tasks for {slug}",
  "tasks for {slug}", "plan the work for {slug}", "/sdd:tasks {slug}". Reads spec.md + sad.md + Accepted ADRs (+ data-model +
  openapi if present), writes docs/features/{slug}/tasks/{_epic,tracker,<task>}.md AND
  docs/features/{slug}/tasks.json. Tracker export to any issue tracker is optional and
  tool-neutral. Hard-refuses if spec.md or sad.md or an Accepted ADR is missing.
---

# Skill: tasks

Task-breakdown generator: atomic tasks ≤1 day, each a separately reviewable change (≤~500 LOC preferred), with a visible dependency graph and a Definition of Done per task. One task = one focused session = one PR. "Build the feature" is not a task — break it down.

Task files **link** to upstream artifacts (`spec.md §AC-N`, `sad.md §6`, `data-model.md`, `contracts/openapi.yaml`, `adr/NNNN-*.md`) — they do not duplicate them. Alongside the human-facing markdown, this skill emits **`tasks.json`**, the contract the `implement` engine reads to build its dependency DAG.

Task prose (`title` / `dod`, the markdown bodies) follows `artifact_language` — the `tasks.json` machine fields (`id`, `layer`, `deps`, `acs`, `files_hint`, `slug`) and tracker states stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Tech Lead.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** `docs/features/<slug>/spec.md` + `docs/features/<slug>/sad.md` + ≥1 Accepted ADR in `adr/`. Missing → STOP and point at the producing skill (`specify` / `design` / `decide-adr`).
- Read directly (not via an index): spec §5 AC + §6 NFR, sad §5 module boundaries + §6 runtime + §9 ADR index, each Accepted ADR, and — if present — `data-model.md` and `contracts/openapi.yaml`.
- (Expected) `sad.md` frontmatter `target_surfaces` — gates which layers appear (step 4). **Absent or empty → warn** («surfaces undeclared — re-run `design`, or proceeding as `backend-service`») **and treat as `[backend-service]`** (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)); never silently emit `ui` tasks for an undeclared surface.

## Protocol

1. **Prereq check (hard).** spec.md + sad.md + ≥1 Accepted ADR, else refuse with the missing one named.
2. **Read upstream directly.** Each task will link back to the section it derives from — no paraphrase layer.
3. **Scaffold output.** `docs/features/<slug>/tasks/`: `_epic.md` (summary + links + the DAG `flowchart`), `tracker.md` (status table), one `<task-slug>.md` per task. Templates → [`./templates/_epic.md`](./templates/_epic.md), [`./templates/tracker.md`](./templates/tracker.md), [`./templates/task.md`](./templates/task.md). **Validate the `_epic.md` `flowchart` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint; fix before committing).
4. **Identify work-items by layer.** Generic, stack-agnostic layers: `migration` (DB) · `domain` (entities/invariants) · `infra` (repo/persistence) · `app` (service/use-case) · `ports` (handler/API) · `ui` (UI components / screens / view-state — only when a UI surface is declared) · `tests` · `wiring` (composition/DI) · `docs`. **`sad.md` frontmatter `target_surfaces` gates which layers appear** (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)): a `web-frontend` / `mobile-app` / `desktop-app` surface adds `ui` tasks; a backend-only feature emits domain/infra/app/ports (no `ui`); a `cli` feature app/ports; a `worker` domain/infra. Each `ui` task **names the existing components / tokens / styling it reuses** (from `architecture-map.md` §Frontend) — a *new* component is listed only when no existing primitive fits. List 8–20 items by size (see [`../_shared/size-matrix.md`](../_shared/size-matrix.md)).
5. **Atomic check.** Each task ≤1 working day. More → split. A change >~500 LOC is a smell that the task is too wide. **Contract-task rule:** a task whose content is changing a shared interface/type that existing implementations must satisfy in a statically-checked language (Go, TS, Java, …) is **not emitted standalone** — it cannot be committed green on its own (the compile-time check breaks every implementer). **Fold it into the first implementing task.** If a split is still warranted (several implementers), mark the pair a **compile-coupled lane**: both tasks list the contract file in `files_hint` (reusing the existing overlap-lane mechanics — no `tasks.json` schema change), so `implement` serializes them and may close them with one shared gate + commit.
6. **Dependency graph.** For each task, `deps: [...]`. Identify parallel branches (e.g. the migration and a pure-domain task can start together). This graph IS the DAG `implement` will topologically sort into phases.
7. **Per-task DoD.** Each task is testable: «unit tests for the new validation pass», «migration applies and reverts cleanly», «handler returns the spec'd outcome for AC-03». No subjective «done when I say so».
8. **AC refs + files hint.** Each task lists the `acs` it satisfies (spec §5 IDs) and a `files_hint` — the directories/files it will touch. `files_hint` lets `implement` serialize tasks whose file sets overlap, and `layer: migration` is always serialized (ordered migration sequence); a **compile-coupled pair** (step 5) shares the contract file across both `files_hint`s for the same reason; `layer: ui` is **not** auto-serialized — UI tasks parallelize unless their `files_hint` overlaps. A migration task's `files_hint` is the **staged** pair `docs/features/<slug>/migrations/<NN>_*` (which `implement` promotes into the live `migrations/` when it runs the task) — not a live `migrations/` path.
9. **Estimate + owner.** S/M/L or hours; a named owner (or `<TBD lead>`). Adapt to the team's sizing if any.
10. **Emit `tasks.json`** (step contract below) — the same model the markdown reflects, in machine form, at `docs/features/<slug>/tasks.json`.
11. **Optional tracker export.** If an issue-tracker MCP is connected (Jira / Linear / GitHub Issues / Redmine — whichever the repo uses), offer to create tickets from `_epic.md` + the task files. Otherwise provide copy-paste-ready bodies. Never hard-bind to one tracker.
12. **Self-check.** Every task ≤1 day; DAG acyclic with ≥1 parallel branch where the work allows; DoD per task; `acs` cover every spec §5 AC; `tasks.json` validates against the contract.
13. **Propose commit + handoff.** `tasks: <slug> (breakdown + tasks.json)`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`tasks/`, `tasks.json`) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)): forward `/sdd:plan-tests <slug>` (on `quick` it always collapses to the inline `## Test plan` in `spec.md`), then `/sdd:implement <slug>`; `plan-tests`' N/A condition = **every task's DoD already names its test** — only then skip target `/sdd:implement <slug>` directly (auto-skip on `quick`, offered `↳ or` on `standard`, never on `full`).

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
      "files_hint": ["path/or/dir/the/task/touches"]
    }
  ]
}
```

- The markdown task files and `tasks.json` use the **same field names** (`deps`, `acs`) — this skill emits both from one model, so there's no translation layer to drift.
- `deps` must form a **DAG** (no cycles) and reference only ids present in the file.
- `layer: migration` tasks are serialized by `implement` (ordered migration sequence); `layer: ui` is **not** auto-serialized (UI tasks parallelize); tasks with overlapping `files_hint` are serialized into the same lane regardless of layer — a **compile-coupled pair** (step 5) rides this same mechanism via the shared contract file, and `implement` may commit the pair together (one gate, both `SDD-Task` trailers).
- Which layers are present is gated by `sad.md` frontmatter `target_surfaces` (a UI surface adds `ui`; a backend-only feature has none) → [`../_shared/surfaces.md`](../_shared/surfaces.md).

## Definition of Done

- `tasks/_epic.md` + `tasks/tracker.md` + one `tasks/<task>.md` per task exist, linking (not duplicating) upstream.
- `tasks.json` exists and validates: acyclic `deps`, every `acs` entry is a real spec §5 AC, every task has a `dod` and a `files_hint`.
- Every task ≤1 day with an owner; the DAG shows ≥1 parallel branch where the work allows.
- Every spec §5 AC is covered by ≥1 task's `acs`.
- The step-12 check (atomicity, acyclic DAG, per-task DoD, AC coverage, `tasks.json` contract) is this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **«Build the feature»** as one task. Break into ≥8 atomic ones.
- **5-day monster tasks** → unreviewable. Split.
- **No dependencies** → parallel starts that block each other the next day.
- **No per-task DoD** → «done when I decide».
- **No owner** → nobody starts, or everyone assumes the other will.
- **Hard-binding to one tracker** (Jira-only language). Export is optional and tool-neutral.
- **Task body duplicates spec AC / sad §6 / data-model verbatim** — link, don't paste.
- **`tasks.json` out of sync with the markdown** — they must reflect the same model.
- **A task that violates a Hard Rule** from spec §6 / sad §11 (e.g. «edit another module» when the architecture forbids it).

## References & template

- [`./templates/_epic.md`](./templates/_epic.md) · [`./templates/tracker.md`](./templates/tracker.md) · [`./templates/task.md`](./templates/task.md)
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — how many tasks for the feature size.
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — `target_surfaces` (read from `sad.md`) gates which layers appear; a UI surface adds the `ui` layer (not auto-serialized).
