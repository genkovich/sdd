# Size matrix — XS/S/M/L/XL classification + MVP-vs-Full artifact set

> **Reference-only.** Not a skill. `classify-size` is the canonical owner of this matrix;
> every other skill reads it to decide how much of its artifact to produce (MVP vs Full)
> and how deep to run its Socratic pass.

## How to classify size

The four signals (`classify-size` asks one `AskUserQuestion` per signal):

| Signal | XS | S | M | L | XL |
|---|---|---|---|---|---|
| **PR count** | 1 | 2–5 | 5–15 | 15+ | many, staged |
| **Time to merge main part** | ≤1 day | ~1 week | 1–2 sprints | >1 month | own roadmap |
| **New module / new API / migration** | none | ≤1 of three | 1–2 of three | 2–3 of three | new subsystem |
| **Breaking changes for consumers** | no | internal only | internal or public | public | public + cross-team |

- **XS** — 1 PR, ≤1 day, no migration, no new API. (Typo, copy fix, config tweak.)
- **S** — 2–5 PRs, ~1 week, maybe a small migration.
- **M** — separate epic, 1–2 sprints, new module / API / migration.
- **L** — cross-module, several teams, breaking changes possible.
- **XL** — new subsystem, needs a separate roadmap.

On edge cases, name the dominant signal: «this is M because it adds a new API + 1–2 sprints, even though PR count is on the S/M border».

> **One-sentence rule.** If you hesitate between MVP and Full — start with MVP. Filling the empty sections of an artifact later is cheaper than discarding pre-built ones.

## MVP-vs-Full artifact set

Artifact depth ∝ feature size. XS/S → minimal set; M+ → full.

| Artifact (skill) | MVP (XS/S) | Full (M+) |
|---|---|---|
| spec — `specify` | yes | yes |
| clarify pass — `clarify` | light (always run; the skip is offered by `specify`'s handoff per the fast lane below) | yes |
| CONTEXT.md glossary — `glossary` | yes | yes |
| SAD (Arc42 12 §) + C4 L1/L2 — `design` | 12 sections walked, more `<!-- N/A -->` allowed | all 12 filled |
| ADRs (in `adr/`) — `design` / `decide-adr` | 2–4 typical | 5–12 typical |
| sequence diagrams — `sequences` | every AC covered, detail collapsed | as many flows as the user-stories/ACs need — never a cap; XS/S may collapse detail but still cover every AC |
| deployment view — `design` §7 | `<!-- N/A -->` if no infra change | yes |
| data-model + migrations — `data-model` | if DB touched | yes |
| API contract (OpenAPI) — `api` | yes | yes |
| events — `api` | if async | yes |
| task breakdown + tasks.json — `tasks` | yes | yes |
| test-plan — `plan-tests` | inline in spec | separate file |
| implementation — `implement` | yes | yes |

## Routes — quick / standard / full (the auto-router)

The **route** decides how the optional stages (`clarify`, `ux-flows`, `sequences`, `data-model`,
`api`, `screens`, `plan-tests`) are handled at each handoff. It lives in **`docs/features/<slug>/.route`** — one
line, plain text, exactly one of `quick` / `standard` / `full` (same discipline as `.size`: no
comments, no frontmatter — wrappers grep it cheaply). It is written by `classify-size` (the
canonical owner) and by `specify` step 1 when it classifies inline; the route **default derives
from the size** — **XS/S → `quick`, M → `standard`, L/XL → `full`** — and is confirmed together
with the size in the **same single `AskUserQuestion`** (the user may pick a different route than
the default; a `quick` L is legal, just loud).

| Route | Handoff behaviour at an optional stage |
|---|---|
| `quick` | the producing stage **evaluates the N/A condition itself** (table below): condition holds → **auto-skip** the stage, stating the reason in the handoff («auto-skipped `clarify`: zero §8 OQ»), and the `↳ or` alternative **inverts** — it now offers the *skipped* stage («run the full path»); condition does **not** hold → the stage is not skipped, normal forward handoff |
| `standard` | today's behaviour — the handoff names the next stage and **offers** the skip as the `↳ or` alternative when the N/A condition holds; the **user** picks |
| `full` | no skip alternatives — every optional stage runs; the handoff never prints an `↳ or` skip line |

**Quick-route softenings** (in addition to the auto-skip): `design` recommends `--depth=easy` in
the question that sets its depth dial; `plan-tests` always collapses to the inline `## Test plan`
in `spec.md`; `clarify` auto-skips when the spec has zero §8 open questions.

**Missing `.route`** → behave as `standard` (the pre-route default) and say so in the handoff —
«route standard (default — no `.route`; run `/sdd:classify-size <slug>`)» — fully back-compatible.

**Mid-flight override.** The route steers **handoffs only — it never makes a stage refuse**. To
change course: re-run `/sdd:classify-size <slug>` (rewrites `.route`), or simply invoke a skipped
stage directly — it runs normally regardless of the route.

### The N/A conditions (the fast-lane table)

Every condition is a **«skip when N/A»** condition, never «skip always»: an XS feature *with* a
schema change still runs `data-model` — on every route.

| Stage | Skip when (the N/A condition) | Who evaluates/offers it |
|---|---|---|
| `clarify` | the spec came out with **zero §8 open questions** and no AC was flagged ambiguous during specify | `specify`'s handoff |
| `ux-flows` | **no human-facing UI** — every spec §4 actor is a system/service (API-to-API, worker, scripted CLI), **or** the repo has no UI at all (`architecture-map.md` `frontend: ""` and no `docs/design-system.md`). `target_surfaces` doesn't exist yet at this point — the condition deliberately derives from the spec's actors + the repo signal; the **formal** surface declaration is made by `design`, which reads `ux-flows.md` as input | `clarify`'s handoff (`specify`'s when clarify was legally skipped) |
| `sequences` | **one actor and no multi-step runtime flow** — a single request/response or a pure rule change; nothing an `alt`-branch diagram would reveal | `design`'s handoff |
| `data-model` | **no schema change** — no new entity, column, index, or migration | `sequences`' handoff |
| `api` | **no contract change** — no new/changed endpoint, event, CLI command, or public signature (the skill also self-skips on «no external interface»). `api` **accepts a legally-skipped `data-model`** (no schema change) — it derives from the existing schema; its hard gate fires only when a schema change exists | `data-model`'s handoff |
| `screens` | **no UI surface declared** — `sad.md` frontmatter `target_surfaces` contains none of `web-frontend` / `mobile-app` / `desktop-app` | `api`'s handoff (carried forward when `api` is itself N/A) |
| `plan-tests` | never fully skipped — it **collapses to the inline `## Test plan`** in `spec.md` (cheap; always inline on `quick`); skip entirely only when every task's DoD already names its test | `tasks`' handoff |

**Never skippable — on any route:** `specify` (the spec is the trace anchor), `design` (declares
`target_surfaces` + the ADR gate), `tasks` (`implement` consumes `tasks.json`), `implement`,
`review`, `ship`. The shortest legal route is therefore
`specify → design → tasks → implement → review → ship` — a `quick` XS feature closes in one session.

When several consecutive stages are N/A, walk the conditions in order at each handoff and jump to
the first stage whose condition does **not** hold (skipping `sequences` moves its `data-model`
skip-question into `design`'s handoff, and so on) — on `quick` the stage walks them itself, on
`standard` it offers each hop as the `↳ or` alternative.

## Surface count is a second scaling axis

Size (XS–XL) is the *depth* dial; the number of **target surfaces** a feature declares (in `design`, written to `sad.md` frontmatter `target_surfaces` → [`./surfaces.md`](./surfaces.md)) is a second, *breadth* axis on the artifact set. Each surface adds its own work: a UI surface (`web-frontend` / `mobile-app` / `desktop-app`) adds the `ui` task layer, UI-driven §6 flows, and the component / visual-regression / e2e-through-UI test tiers; a `cli` / `worker` / `library-sdk` surface adds its own contract form + flows. So a multi-surface feature (`[backend-service, web-frontend]`) is genuinely **larger** than a single-surface one of the same XS/S/M class — no new column here, but expect more tasks, more flows, and more test rows per extra surface.

## SAD size behaviour

Even for XS/S, `design` walks all 12 Arc42 sections — consistency beats completeness theatre. Sections that genuinely don't apply get `<!-- N/A: <one-line reason> -->`. Common XS/S N/A patterns:

- §7 Deployment — `<!-- N/A: reuses existing deployment unit, no infra change -->`
- §6 Runtime — collapses to the **fewest flows that still cover every §5 AC** (often one flow with the error branches inline as `alt`, rather than separate failure-mode flows). Detail collapses; AC-coverage does not — `sequences` still maps every AC to a flow, a branch, or an explicit N/A even at XS/S.
- §11 Risks — one accepted-debt row, no medium/high risks.

Same skill, same template, smaller content footprint.

## Wrappers / gates

A skill that reads `.size` skips heavy sub-artifacts for XS/S (separate test-plan, deployment view, full ADR sweep). `specify` **establishes `.size` at the start of the backbone** (it classifies + writes it if absent), so later stages normally read a real size. A stage that *still* finds none (e.g. `design` run standalone, before `specify`) defaults to **M** (the safe over-production default) **and says so in its handoff** — never a silent assumption.
