# Inputs + preconditions (step 1)

## Hard gate

`docs/features/<slug>/tasks.json` must exist and parse as JSON. Missing or malformed → refuse: «run `tasks <slug>` first (it emits tasks.json)». Do not try to reconstruct tasks from the markdown — `tasks.json` is the contract.

## Validate the contract

The loaded `tasks.json` must satisfy the shape from the `tasks` skill:

- top-level `{ slug, tasks: [...] }`.
- each task: `id` (unique), `title`, `layer`, `deps` (array of existing ids), `acs` (array), `dod` (string), `files_hint` (array).
- `deps` forms a DAG (no cycles) — verified in step 4. A cycle is a hard error: report the cycle and stop (it is a `tasks` bug, not an `implement` one).

## Scaffold task sets (from `survey` greenfield)

A `tasks.json` with `slug: "_scaffold"` and `layer: scaffold` tasks comes from `survey`'s greenfield foundation (not from `tasks`). These tasks have **no feature `acs`** — they create the project skeleton (structure, baseline module, test harness, migration tooling, CI, conventions doc). Handle them specially:

- **The skeleton smoke test is the red→green anchor**, not a feature AC: RED = «the project does not build / boot / the tooling doesn't run»; GREEN = «build + boot + the empty test suite + the migration tool all succeed». Write that smoke test as part of the scaffold (task S2 in the foundation contract) and drive the skeleton to make it pass — no per-folder TDD theatre.
- Read `docs/architecture-map.md` (`mode: greenfield-bootstrap`) for the exact stack + conventions to scaffold to.
- After the scaffold is green the repo is real, and the normal per-feature flow (`specify → … → implement`) builds into it with real feature TDD.

## Context the agents read directly

The engine does **not** paste these into prompts — each agent (or the sequential runner) reads them itself, so there's no paraphrase drift:

- `docs/features/<slug>/spec.md` — §5 acceptance criteria (the source of truth for what each test asserts).
- `docs/features/<slug>/test-plan.md` — the AC→test map, if `plan-tests` ran.
- `docs/features/<slug>/data-model.md` + the migration files — schema the code targets.
- `docs/features/<slug>/contracts/openapi.yaml` — the API contract handlers must match.
- `docs/features/<slug>/sad.md` + Accepted `adr/` — the architecture and the locked decisions.
- `docs/architecture-map.md` (from `survey`, if present) — the existing system's conventions the new code must match (module wiring, error handling, IDs, tests, migrations) + the closest precedent to copy. Saves the agents re-discovering the patterns.

## Repo state

- Note the current branch. If `branch_strategy: feature` and the repo is on its default branch, create/switch to a feature branch before any commit (see [`settings.md`](./settings.md)).
- Do not touch unrelated dirty changes — work only the files each task's `files_hint` names.
