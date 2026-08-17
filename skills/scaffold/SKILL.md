---
name: scaffold
model: inherit
effort: medium
agents: []
description: >
  Use to materialize the greenfield skeleton that survey's foundation session planned. Reads
  docs/architecture-map.md (mode: greenfield-bootstrap) plus docs/features/_scaffold/tasks.json
  and builds the real project structure: folders + entry point, test harness + smoke test,
  migration tooling, CI, the conventions doc. Triggers on "scaffold the skeleton", "materialize
  the skeleton", "bootstrap the project skeleton", "/sdd:scaffold", "матеріалізуй скелет",
  "розгорни скелет проєкту", "збудуй каркас". Runs the S-tasks sequentially inline (no
  team/workflow orchestration), anchored on the skeleton smoke test — builds + boots + empty
  test suite runs + migration tool runs — commits, and hands off to /sdd:specify. Hard-refuses
  without the greenfield foundation: run survey first.
---

# Skill: scaffold

The **materialization step between `survey`'s greenfield foundation and the first feature.** `survey`
fixes the foundation (stack / structure / conventions in `docs/architecture-map.md`, marked
`mode: greenfield-bootstrap`) and emits the scaffold plan (`docs/features/_scaffold/tasks.json`,
tasks S1–S5 per [`../survey/references/foundation.md`](../survey/references/foundation.md));
`scaffold` turns that plan into a repo that **builds, boots, tests and migrates** — then the normal
per-feature flow (`specify → … → implement`) builds into it. This skill exists so the greenfield
handoff is a real gate, not a wave of the hand: `_scaffold` is **not a feature** (no `.size`, no
`.route`, no ACs), so it never enters `implement`'s engine or its team/workflow decision tree.

**The skeleton smoke test is the TDD anchor** (canonical here). Scaffold tasks have no feature ACs,
so red→green anchors on the structural smoke test: **RED** = the project does not build / boot / the
tooling doesn't run; **GREEN** = build + boot + the empty test suite + the migration tool all
succeed. That keeps the discipline meaningful for structural work — no per-folder TDD theatre.

## Owner

Architect / Tech Lead — the same person who fixed the foundation in `survey`.

## Inputs

- `docs/architecture-map.md` with `mode: greenfield-bootstrap` — the decided stack, module
  structure, conventions, and the machine keys (`build_cmd`, `test_cmd`, `lint_cmd`,
  `migration_tool`, `frontend`).
- `docs/features/_scaffold/tasks.json` — the S1–S5 scaffold plan (`layer: scaffold`, `slug: "_scaffold"`).

## Protocol

1. **Hard gate.** Both inputs must exist: `docs/architecture-map.md` whose frontmatter says
   `mode: greenfield-bootstrap`, AND `docs/features/_scaffold/tasks.json` parsing as the scaffold
   contract (`slug: "_scaffold"`, `layer: scaffold` tasks with `id`/`title`/`deps`/`dod`/`files_hint`).
   Either missing → **refuse**: «run `survey` first — its greenfield session fixes the foundation and
   emits the scaffold plan». A map without the greenfield marker means the repo is already real —
   refuse too and point at `/sdd:specify <slug>`. If the skeleton already exists (every S-task's
   output present and the smoke test green), say so and STOP — nothing to materialize.
2. **Read the foundation.** From the map: stack, folder/module structure, conventions catalog, the
   machine keys. From `tasks.json`: the S-tasks in dependency order. The map is the **only** source
   of decisions — scaffold never re-litigates stack/style choices (that was `survey`'s session).
3. **Materialize sequentially inline.** Execute the S-tasks one by one in dependency order, in this
   session — deliberately **no** agent team, no Workflow, no `implement` decision tree: `_scaffold`
   has no `.size`/`.route`, and five structural tasks need no orchestration. Per task: create the
   files its `files_hint` names, to the map's conventions; verify its `dod`; record it done. A task
   that genuinely doesn't apply (e.g. no datastore → the migration task) is **explicitly dropped
   with a stated reason** — never silently skipped.
4. **Drive the smoke test green.** Write the smoke test as part of the harness task, then run the
   full anchor with the map's machine-key commands: build + boot + the empty test suite + the
   migration tool (apply + revert). Iterate until GREEN — a red skeleton is not done.
5. **Reconcile the map's machine keys.** If the commands that actually worked differ from the map's
   frontmatter (`build_cmd` / `test_cmd` / `lint_cmd` / `migration_tool`), **update the map** —
   `implement`'s command-detection cascade reads these keys; stale keys poison every later feature.
6. **Commit** — `scaffold: materialize skeleton`.
7. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): verify
   **4 items**: (1) the smoke test was actually executed and is green (build + boot + empty suite +
   migration tool — command output in hand, not assumed); (2) every S-task is done or explicitly
   dropped with a reason; (3) the map's machine keys match the commands that just ran (updated if
   they diverged); (4) the commit contains the skeleton files. Fix + re-check ≤2 cycles; surface
   anything unresolved.
8. **Handoff.** Emit the **stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) —
   *What I did* (tasks materialized, smoke-test result, «self-check: 4/4 pass») + *Review before
   continuing* (the committed skeleton diff + `docs/architecture-map.md`) + *Run next*: `/clear`,
   then `/sdd:specify <slug>` — the first real feature, with a real repo to build into.

## Definition of Done

- Every S-task from `docs/features/_scaffold/tasks.json` is materialized (or explicitly dropped
  with a reason), to the conventions the map fixes.
- The skeleton smoke test is **green**: the project builds, boots, the empty test suite runs, the
  migration tool applies + reverts.
- The map's machine keys reflect the commands that actually work; the skeleton is committed.

## Anti-patterns

- **Orchestrating five structural tasks.** No team mode, no Workflow, no DAG engine — `_scaffold`
  is repo-level bootstrap, not a feature; sequential inline is the design, not a fallback.
- **Per-folder TDD theatre.** The smoke test is the one anchor; writing a failing test per directory
  is ceremony without information.
- **Re-deciding the foundation.** Stack/structure/convention choices live in the map + its ADRs
  (`survey`'s session); scaffold materializes, it never re-litigates. A gap in the map goes back to
  `survey`, not into an improvised decision here.
- **Handing off red.** «Skeleton written but doesn't boot» is not done — GREEN is the exit condition.
- **Treating `_scaffold` as a feature.** No `.size`/`.route`, no spec, no ACs — it never enters the
  per-feature pipeline or its size/route machinery.
