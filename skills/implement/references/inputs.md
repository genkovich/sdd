# Inputs + preconditions (step 1)

## Hard gate

`docs/features/<slug>/tasks.json` must exist and parse as JSON. Missing or malformed → refuse: «run `tasks <slug>` first (it emits tasks.json)». Do not try to reconstruct tasks from the markdown — `tasks.json` is the contract.

## Validate the contract

The loaded `tasks.json` must satisfy the shape from the `tasks` skill:

- top-level `{ slug, tasks: [...] }`.
- each task: `id` (unique), `title`, `layer`, `deps` (array of existing ids), `acs` (array), `dod` (string), `files_hint` (array).
- `deps` forms a DAG (no cycles) — verified in step 4. A cycle is a hard error: report the cycle and stop (it is a `tasks` bug, not an `implement` one).

## Scaffold task sets (from `survey` greenfield) → run `scaffold`, not `implement`

A `tasks.json` with `slug: "_scaffold"` and `layer: scaffold` tasks is the scaffold plan from
`survey`'s greenfield foundation — it is **not** an `implement` input. Redirect: «this is the
scaffold set — run `/sdd:scaffold` (the materialization protocol + the skeleton smoke-test anchor
are canonical there); `implement` is the feature engine.» After the skeleton is green, the normal
per-feature flow (`specify → … → implement`) builds into it with real feature TDD.

## Context the agents read directly

The engine does **not** paste these into prompts — each agent (or the sequential runner) reads them itself, so there's no paraphrase drift:

- `docs/features/<slug>/spec.md` — §5 acceptance criteria (the source of truth for what each test asserts).
- `docs/features/<slug>/test-plan.md` — the AC→test map, if `plan-tests` ran. **For XS/S the plan is usually inline instead** — a `## Test plan` section in `spec.md` (per the size matrix); check both locations and read whichever exists.
- `docs/features/<slug>/data-model.md` + the **staged** migration files under `docs/features/<slug>/migrations/` — the schema the code targets (a `layer: migration` task promotes them into the live `migrations/` tree; see «Staged migrations → promote» below).
- `docs/features/<slug>/contracts/openapi.yaml` — the API contract handlers must match.
- `docs/features/<slug>/sad.md` + Accepted `adr/` — the architecture and the locked decisions.
- `docs/architecture-map.md` (from `survey`, if present) — the existing system's conventions the new code must match (module wiring, error handling, IDs, tests, migrations; **for a `ui` surface, §Frontend / UI foundation — the design system / components / tokens / styling to reuse**) + the closest precedent to copy (including the **closest UI precedent** for a new screen). Saves the agents re-discovering the patterns.
- `docs/design-system.md` + `docs/features/<slug>/ux-flows.md` + `docs/features/<slug>/screens.md` (when they exist) — the **`ui`-task reading list**: the design canon (tool, posture, tokens, component inventory), the user flows, and the per-state screen manifest the task builds to (see «`ui`-layer tasks» below).

## Staged migrations → promote before running

`data-model` stages each migration as `docs/features/<slug>/migrations/<NN>_<verb>_<entity>.up.sql` + `.down.sql` (feature-local ordinal) — **not** in the live `migrations/` tree, so a design-stage schema can't be applied to a real DB before the feature is built. The `layer: migration` task(s) own **promotion**:

1. **Promote in ordinal order.** For each staged `<NN>_*` pair (ascending), copy it into the repo's live `migrations/` directory under the repo's detected convention — sequential → the **next free number** (`000023_*`); timestamped → a fresh timestamp — preserving the intra-feature order. The number is assigned **now, at promote-time**, so two features building around the same time never collide. The SQL body is copied **verbatim** — never rewritten during promotion. After promotion the live file is canonical; the staged copy is the frozen design record (git keeps it; don't hand-edit it).
2. **Then apply + verify.** Run the migration with the repo's tool against the (ephemeral, testcontainers) DB; the task's DoD «migration applies and reverts cleanly» is checked on the promoted file. The feature's integration tests run against the promoted schema.
3. **Commit** the promoted live file(s) with the migration task (the staged pair under `docs/features/<slug>/migrations/` was already committed by `data-model`).

A `layer: migration` task with **no** staged file under the feature's `migrations/` is a `tasks`/`data-model` mismatch — surface it, do not invent SQL.

## `ui`-layer tasks

A `layer: ui` task (present only when `sad.md` frontmatter `target_surfaces` declares a UI surface — `web-frontend` / `mobile-app` / `desktop-app`) runs through the **same TDD cycle** as any other task; it just follows the **repo's frontend test convention** — component / e2e-through-UI runners detected from `package.json` scripts (Playwright / Storybook / a visual-diff tool / etc.) — **not** a backend assumption. No engine change: command-detection already picks up frontend scripts in its cascade.

**Reuse the UI foundation (don't reinvent).** A `ui` task **composes the existing design system** from `architecture-map.md` §Frontend and the `docs/design-system.md` inventory — reuse the existing components / shared primitives, pull design tokens (colors / spacing / typography) from the repo's token source, and build in the repo's **one** styling approach. When `docs/features/<slug>/screens.md` exists, **build the screen to the states it declares** (default / loading / empty / error / … — the manifest is the contract) and **reuse the components the manifest names**; a **NEW** component only when no existing primitive fits — built in the repo's styling approach and **registered back into the `docs/design-system.md` §Component inventory** (flip its «Registered» row). Libraries: always the repo's existing ones — a **new dependency only as a last resort, confirmed with the user**, never silently added. Find the **closest existing screen/component** (the §Frontend UI precedent) and extend/compose it. This is the frontend echo of "match the repo + copy the closest precedent" → [`../../_shared/surfaces.md`](../../_shared/surfaces.md).

## Repo state

- Note the current branch. If `branch_strategy: feature` and the repo is on its default branch, create/switch to a feature branch before any commit (see [`settings.md`](./settings.md)).
- Do not touch unrelated dirty changes — work only the files each task's `files_hint` names.
