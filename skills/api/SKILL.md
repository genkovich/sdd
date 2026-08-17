---
name: api
model: inherit
effort: medium
agents: []
description: >
  Use to derive the API contract for a feature — an OpenAPI 3.1 document at
  docs/features/{slug}/contracts/openapi.yaml plus a drift/sync report (and an events doc when
  the feature has async flows). Triggers on "api for {slug}", "openapi for {slug}",
  "API contract for {slug}", "lock the interface for {slug}", "events for {slug}",
  "/sdd:api {slug}", "контракт API для {slug}", "OpenAPI для {slug}", "опиши ендпоінти".
  The contract is never hand-written: it is a derived function of data-model.md (typed fields +
  constraints), the sad.md §6 sequence diagrams (error branches, async actors), and spec.md
  acceptance criteria. Runs an inline drift check (does the contract match the model and the
  sequences?) and a reconcile mode. Hard-refuse if data-model.md is missing AND the feature
  changes the schema → run `data-model {slug}` first; on a legal no-schema-change skip it
  derives from the existing schema instead.
---

# Skill: api

Projects the upstream artifacts into one **interface contract**. By default that's an HTTP/OpenAPI contract; this skill is **interface-kind aware** — and the kind comes from the surface(s) `design` declared in `sad.md` frontmatter `target_surfaces`, **read here, not re-derived** (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)). For a non-HTTP project it produces the matching contract form (or steps aside):

- **HTTP / REST** (default) → `contracts/openapi.yaml` (OpenAPI 3.1) + `api-sync-report.md`.
- **gRPC / RPC** → a `.proto` (or the repo's IDL) with the same derive-and-drift discipline.
- **CLI** → `contracts/cli.md` — the command/flag/exit-code surface derived from the AC.
- **Library / SDK** → `contracts/public-api.md` — the public signatures/types the feature exposes.
- **Event-only / worker** → just `contracts/events.md` (no request/response surface).
- **No external interface** (pure internal logic) → **skip** with a one-line note in the report; go straight to `tasks`.

Whatever the form, the contract is **derived from `data-model.md` — or, on a legal no-schema-change skip, the existing schema — plus the sad.md §6 sequences + the spec's AC, never typed by hand** — generation that diverges from the model or the sequences is the bug this skill exists to catch. The rest of this file details the HTTP path (the common case); the same derive → drift-check → reconcile loop applies to the other forms with the form-appropriate artifact.

This skill keeps only its own machinery. Question phrasing is **shared** → [`../_shared/ask-style.md`](../_shared/ask-style.md). Depth (events doc only when async; one resource vs full surface) follows the **size matrix** → [`../_shared/size-matrix.md`](../_shared/size-matrix.md). The drift-resolution dialog reuses the shared 4-state actions — keep it short, point the machinery to `_shared`.

Contract `summary`/`description` prose follows `artifact_language` — paths, `operationId`, status codes and schema names **never** translate → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Backend Lead (drives the interface). The PM confirms each endpoint maps to a real user story; a frontend / consumer engineer is the first reader — the contract is locked before they start integration.

## Inputs

- `<slug>` — same feature slug used by every earlier stage.
- **Gate (conditional — hard-refuse only when a schema change exists):** `docs/features/<slug>/data-model.md`. When present, it is the source of typed fields and constraints. When absent, evaluate `data-model`'s N/A condition (no schema change — [size-matrix fast lane](../_shared/size-matrix.md)) yourself: sad.md §5 declares no new building blocks/entities, no staged `docs/features/<slug>/migrations/`, and the spec introduces no new entity → **proceed**, deriving types/constraints from the **existing schema** (the live `migrations/` DDL + `architecture-map.md` §Migrations/§Conventions) and saying so loudly in the handoff. Absent **and** a schema change exists → STOP and point: «run `data-model <slug>` first — the contract is derived from its entities».
- (Expected) `sad.md` frontmatter `target_surfaces` — picks the contract form (step 1). **Absent or empty → warn** («surfaces undeclared — re-run `design`, or proceeding as `backend-service`») **and treat as `[backend-service]`**, falling back to the architecture-map derivation (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)).
- (Expected) `docs/features/<slug>/sad.md` §6 — the Mermaid `sequenceDiagram` blocks. Their `alt`/`else` branches become the error `responses`; an async participant (`<message-bus>` / `<external-system>`) on a mutating flow marks its endpoint `Idempotency-Key`-required and seeds `events.md`. Absent → note the gap (error branches derived from `spec.md` §5 only — likely misses authorization branches) and still generate.
- (Expected) `docs/features/<slug>/spec.md` — §4 user stories give the endpoint list; §5 acceptance criteria give the shape of each happy + error outcome. The spec deliberately holds **no** HTTP/status/error-code/SQL detail — that mapping is this skill's job.
- (Optional) `docs/features/<slug>/.size` — depth hint. Absent → default to M (full surface) **and say so loudly in the handoff** — «size M (default — no `.size`; run `/sdd:classify-size <slug>`)». `docs/features/<slug>/adr/*.md` — override defaults (versioning, error format, auth scheme) when an ADR mandates it; `CONTEXT.md` (read both repo-root and `docs/features/<slug>/` — per-feature wins → [`../glossary/SKILL.md`](../glossary/SKILL.md)) — glossary terms become schema names verbatim. Existing `contracts/openapi.yaml` → diff and update in place, never overwrite whole-cloth.

## Protocol

1. **Gate + interface kind + read.** `test -f docs/features/<slug>/data-model.md` — a three-way gate, not a binary one:
   - **present** → derive from it (the default path below, unchanged);
   - **absent + no schema change** (evaluate `data-model`'s N/A condition yourself: sad.md §5 names no new building blocks/entities, no staged `docs/features/<slug>/migrations/`, spec introduces no new entity) → **PROCEED** — this is the legal fast-lane skip: derive types/constraints from the **existing schema** (live `migrations/` DDL + `architecture-map.md` §Migrations/§Conventions), record each field-origin as `existing schema — <migration/DDL anchor>` with the same confidence scale, and state loudly in the handoff: «data-model.md absent — legal fast-lane skip (no schema change); fields derived from the existing schema»;
   - **absent + a schema change exists** → refuse with the pointer above.
   **Determine the interface kind — read `sad.md` frontmatter `target_surfaces` FIRST** (design already declared it; the surface picks the contract form per [`../_shared/surfaces.md`](../_shared/surfaces.md): `backend-service` → OpenAPI / gRPC / events per its sub-kind; `cli` → `contracts/cli.md`; `worker` → `contracts/events.md`; `library-sdk` → `contracts/public-api.md`; a UI surface — `web-frontend` / `mobile-app` / `desktop-app` — *consumes* the backend contract, it does not author one). **Fall back to deriving the kind** from `docs/architecture-map.md` + the spec's capabilities **only if the SAD or the field is absent** (a greenfield run where `design` was skipped). HTTP/REST → the OpenAPI path below (the default, detailed here); gRPC/CLI/library/event-only → produce the matching contract form (see the intro) with this same derive→drift→reconcile loop; **no external interface** (pure internal logic) → skip to `tasks` with a one-line note in the report — this self-skip is `api`'s N/A condition in the [size-matrix fast lane](../_shared/size-matrix.md). Then read `data-model.md` (entities, fields, types, constraints) — or, on a legal skip, the existing schema sources named above — plus `sad.md` §6 (flows + `alt`-branches + async actors), `spec.md` §4/§5. Surface a one-line "found / missing" note for sad.md and spec.md — never refuse on their absence, only narrow the derivation and record the gap.
2. **Copy the template.** [`./templates/openapi.yaml`](./templates/openapi.yaml) → `docs/features/<slug>/contracts/openapi.yaml`. If async flows exist, also [`./templates/events.md`](./templates/events.md) → `contracts/events.md`. Fill `info.description` from `spec.md` §1 (why this API exists).
3. **Derive endpoints + schemas.** One endpoint (or more) per §4 user story. Every request/response field traces to a `data-model.md` entity column — or, on a legal skip, to an existing-schema column (a live migration's DDL) — copy its constraints across (`maxLength`/`pattern`/`enum` from the model's bounded types). **Never invent a field with no origin in any input** — ask the user where it comes from. `$ref` every shared schema; no inline duplication. Lists paginate by cursor (`?after=&before=&limit=`), wrapped in `{items, has_next, has_prev, next_cursor}`.
4. **Derive error responses from the sequences.** Each endpoint covered by a §6 flow: turn every `alt … else … end` branch into a `responses` entry. The error body is the unified envelope **`{code, message, details?}`**; `code` follows the **neutral** convention `module.error_name` (snake_case, e.g. `lesson.not_owned`, `lesson.invalid_state`) — a naming rule, not a language artifact. Map status by class (4xx client / 5xx server). This closes the spec's usual blind spot — §5 lists the happy path + a couple of errors; the sequences enumerate the authorization and concurrent-state branches the spec omits.
5. **Async + idempotency.** A mutating endpoint whose §6 flow shows a retry note or an async actor is marked `Idempotency-Key`-required (state the TTL). For each async message, fill an `events.md` entry: event name `module.action.vN`, payload schema, producer, consumers, retry / dead-letter behaviour.
6. **Examples + placeholder data.** Every operation carries a request example + a success example + an error example, using placeholder values only (`<...>@example.test`, `+380 00 000 00 00`, `Test User`) — never real PII.
7. **Inline DRIFT CHECK (bidirectional) + write the report.** Compare the generated contract against the read artifacts and write `docs/features/<slug>/contracts/api-sync-report.md` — see [`./references/drift-check.md`](./references/drift-check.md). It has a field-origins table (one row per `operation.field`: `path | origin | confidence`) and a checklist. The check runs **both directions**:
   - **forward** (contract derived correctly): endpoint↔model, error-code↔repo, validation↔constraint, OpenAPI↔sequence.
   - **back-feed (coverage cross-check)**: every `spec.md` §5 AC maps to ≥1 operation/response; every operation maps to a §4 user story + ≥1 AC; every `sad.md` §6 `alt`-branch has a response, and any error/authorization response the contract needs but no §6 flow shows is a **sequence gap**. A gap here is not an api bug — it's a hole upstream: surface it and resolve it as **Save-as-OQ with the upstream stage as owner** — the OQ row names the producing stage as owner (`specify` for a missing AC, `sequences` for a missing branch) with due «before the contract is finalized», so the source gets fixed through the standard 4-state machine, not a fifth action.
   A **core** finding failing (or ≥3 flags total) pauses the run — resolve each via the shared 4-state actions ([`../_shared/ask-style.md`](../_shared/ask-style.md)): Accept / Fix (the contract) / Save-as-OQ / Drop. A fix that belongs upstream (the spec's AC, the sequence) is the **Save-as-OQ variant with the upstream stage as owner** (see step 7's back-feed) — never a fifth action. Never silently edit the sources — surface the mismatch and let the human pick the right artifact (the contract, the spec's AC, or the sequence).
8. **Lint + write + commit.** Suggest `spectral lint contracts/openapi.yaml` (add it to the project's check target if not yet wired). On a clean check, the files are written; propose commit `api: <slug> contract`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`contracts/openapi.yaml`, `api-sync-report.md`, + `events.md` if async) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)): forward `/sdd:screens <slug>`; `screens`' N/A condition = **no UI surface declared** (`sad.md` `target_surfaces` contains none of `web-frontend` / `mobile-app` / `desktop-app`), skip target `/sdd:tasks <slug>` (on `quick` — auto-skip with the reason + inverted `↳ or`; on `standard` — offer the `↳ or`; on `full` — no skip line).

### Reconcile mode

`/sdd:api <slug> --reconcile`. Re-derives after an upstream artifact changed (typically `data-model.md` arrived or was tightened after a thinner first pass). It re-reads inputs, tightens loose types where the model now has a constraint, refreshes the field-origins confidence column, and — the load-bearing part — surfaces any field that **had** an inferred origin but **now disagrees** with the model. That disagreement is real drift, not stale incompleteness. `info.version` is never bumped silently; the user does that with a CHANGELOG line.

## Definition of Done

- `docs/features/<slug>/contracts/openapi.yaml` written: OpenAPI 3.1, `BearerAuth` global with public endpoints declaring explicit `security: []`, every error response the `{code, message, details?}` envelope, every operation with examples, all shared types via `$ref`.
- `api-sync-report.md` written alongside: field-origins table + the 4-point drift checklist, every core finding ✓ or explicitly resolved with the user.
- Every endpoint maps to a §4 user story; every field traces to a `data-model.md` column (or, on a legal fast-lane skip, to an existing-schema column named in the field-origins table); every error `code` exists in the repo's error definitions (checked in the form the repo uses).
- `contracts/events.md` present iff the feature has async flows; each event has a payload schema, producer, consumers, retry / DLQ note.
- The step-7 bidirectional drift check + `api-sync-report.md` are this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **Contract written by hand**, then the model/sequences bent to fit it. The arrow is one-way: model (or the existing schema on a legal skip) + sequences + spec → contract.
- **Skipping the drift check** because "it was just generated, of course it matches". Generation can match the spec-as-read while diverging from the model or the sequences — different files, different authors. A clean 4/4 ✓ is cheap; a silent ✗ in prod is not.
- **Error responses from the spec only.** §5 lists happy + a couple of errors; the §6 sequences hold the authorization and concurrent-state branches. Skipping them leaves blind spots.
- **Inventing a field** with no origin in any input, or **silently dropping** one that left `data-model.md` (keep it with a `# stale` note and surface it — the human decides).
- **Tripping the hard refuse when the skip was legal** — bouncing a no-schema-change feature back to `data-model` just to produce an empty document. The gate is conditional (step 1): refuse only when a schema change actually exists; otherwise derive from the existing schema and say so.
- **Stack-specific schema or error names.** Schemas use the domain language from `data-model.md`; error codes are the neutral `module.error_name` convention — not a Go/TS/Python idiom and not tied to any driver's error type.
- **Free-text errors** (`{"error": "failed"}`), `?v=2` query versioning, `nullable: true` (3.0 style — use `type: [string, null]`), offset pagination, or real PII in examples.
- **Re-deriving the interface kind when `design` already declared it.** `target_surfaces` in `sad.md` is the primary signal — read it; the architecture-map derivation is the **fallback only** when the SAD/field is absent (greenfield). Silently re-inferring HTTP-vs-events on every run is the double-derivation this skill's surface-awareness removes.

## References & template

- [`../_shared/ask-style.md`](../_shared/ask-style.md) — canonical question/option phrasing for the drift-resolution dialog (step 7).
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — MVP (one resource, events only if async) vs Full surface depth.
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — the declared `target_surfaces` (read from `sad.md`) pick the contract form; this skill reads, never re-derives.
- [`./references/drift-check.md`](./references/drift-check.md) — the field-origins table + 4-point drift checklist, reconcile semantics, conflict table.
- [`./templates/openapi.yaml`](./templates/openapi.yaml) — OpenAPI 3.1 scaffold: `BearerAuth`, cursor page wrapper, `{code, message, details?}` Error schema.
- [`./templates/events.md`](./templates/events.md) — async event-contract scaffold (producer / consumers / payload / retry / DLQ).
