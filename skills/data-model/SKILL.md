---
name: data-model
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to design the data model AND generate the actual forward + rollback migrations in one
  pass — shippable SQL, not a plan. Triggers on "data model for {slug}", "schema for {slug}",
  "generate migrations for {slug}", "DB design + migration", "/sdd:data-model {slug}".
  Reads spec.md §5 +
  sad.md §5 building blocks + the §6 sequence diagrams, then writes docs/features/{slug}/data-model.md plus
  paired *.up.sql / *.down.sql migrations STAGED under docs/features/{slug}/migrations/ (NOT the
  live migrations/ tree — implement promotes them when the feature is actually built) and an audit
  report. Greenfield-first; brownfield delta via --mode brownfield; drift-only via --drift-only.
  Hard-refuses if spec.md or sad.md is missing. Stack-agnostic: detects and FOLLOWS the repo's DB +
  migration conventions and domain layer — it imposes no DB philosophy and writes no rules file.
---

# Skill: data-model

End-to-end runner for the persistence cut: data model + migrations + drift check in one pass. Greenfield-first by default; brownfield delta as `--mode brownfield`. Output is **shippable** — full `.up.sql` + `.down.sql`, not a plan — but **staged under `docs/features/<slug>/migrations/`, never written into the live `migrations/` tree.** `implement` **promotes** the staged pair into `migrations/` (with the real sequence number / timestamp) only when the feature is actually being built. This is deliberate: `data-model` is a design stage four steps before `implement`, so a stray `migrate up` (a teammate's loop, CI, a deploy) must not be able to apply a half-designed schema to a real database. (Same staging discipline the drift fixes already use under `_drift/`.)

**Stack-agnostic by design — it imposes no DB philosophy and writes no rules file.** `data-model` **derives the DB + migration conventions from the architecture** — `architecture-map.md` (the migration tool/naming `survey` recorded) + the `sad.md` persistence decisions (§4 strategy / §5 building blocks / §8 crosscutting) + the Accepted ADRs — and **follows** them; the live `migrations/` + schema **corroborate** and fill anything the architecture left implicit. On a greenfield repo with no architecture signal, it **confirms each schema choice with the user** (Socratic) instead of defaulting to a house style. What it applies regardless of stack is migration **safety** (staging, reversibility, FK indexes, zero-downtime decomposition, no-PII) — never a stance on `updated_at` vs not, hard vs soft delete, UUID vs sequence, or whether `CHECK` constraints are allowed. The size matrix (→ [`../_shared/size-matrix.md`](../_shared/size-matrix.md)) governs how much you produce; the aggregate-roots dialogue uses [`../_shared/ask-style.md`](../_shared/ask-style.md).

`data-model.md` prose follows `artifact_language` — SQL, table/column identifiers, headings and frontmatter stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Backend Lead — **or Mobile Lead** when the run's surface is a `mobile-app` with on-device local persistence (the local-persistence branch, step 2a).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse if missing):** `docs/features/<slug>/spec.md` (entities live in §5 acceptance criteria) and `docs/features/<slug>/sad.md` (entity candidates: §5 building blocks — the persistence containers — + the §6 persist notes). Missing → «run `specify` / `design` first».
- Optional: the sequence diagrams in `sad.md §6` — each `writes/reads <entity>` note is an index candidate (one index per query, justified).
- (Expected) `sad.md` frontmatter `target_surfaces` — context for which containers persist what. **Absent or empty → warn** and **fall back to `default_surfaces` from `.claude/sdd.local.md`** (default `[backend-service]` if unset) — «surfaces undeclared — re-run `design`, or proceeding as `<default_surfaces>`» (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)). A project that set `default_surfaces: [mobile-app]` therefore falls back to a mobile/UI-only surface, **not** to `backend-service` — so it won't silently generate server SQL for a phone's local store.
- **Convention source:** `docs/architecture-map.md` §Migrations (from `survey`) + the `sad.md` persistence decisions (§4/§5/§8) + Accepted ADRs — the migration tool/naming + the DB approach are **derived from here**, not invented (the map also gives module layout, saving a re-scan). For **drift detection** specifically, `explorer` still reads the **actual domain layer** (the map gives layout; drift needs the real struct/field source). Stack-agnostic — no hard-coded path or language.

## Conventions — detect and follow (stack-agnostic)

`data-model` imposes **no** DB philosophy. For each topic below it **follows the architecture's decision** — `architecture-map.md` §Migrations + the `sad.md` persistence decisions + Accepted ADRs — corroborated by the repo's existing migrations/schema; on a greenfield repo with no signal it **confirms the choice with the user**. It never legislates a house style.

| Topic | How `data-model` decides |
|---|---|
| Naming (tables / columns) | Follow the repo's convention (detected from existing migrations + schema); greenfield → confirm. |
| PK strategy | Follow the repo (UUID / bigint-identity / sequence / composite — whatever it uses); greenfield → confirm. |
| Audit columns (`created_at` / `updated_at` / …) | Match the repo's pattern; greenfield → confirm. No stance imposed either way. |
| Delete strategy (hard / soft / status) | Match the repo; greenfield → confirm. |
| Constraints (`CHECK` / `TRIGGER` / DB `DEFAULT`) | Use them **iff the repo does**; never add or forbid them by fiat. |
| String / JSON types | Match the repo's norms (`VARCHAR(N)` / `TEXT` / JSON); greenfield → confirm. |

What it **does apply regardless of stack** — migration **safety**, not DB philosophy:

| Mechanic | Why (stack-agnostic) |
|---|---|
| **Staged** as `docs/features/<slug>/migrations/<NN>_<verb>_<entity>.up.sql` + `.down.sql` (NN = feature-local ordinal), promoted by `implement` (real number/timestamp assigned at promote-time) | Keeps the live tree free of half-designed schema; late numbering avoids early-grab collisions. |
| Idempotent DDL where the tool supports it (`IF NOT EXISTS`, `ON CONFLICT DO NOTHING` on seeds) | Re-running a partially-applied migration does not error. |
| A `.down` for every `.up` (full reversibility) | Rollback is always possible. |
| An index on every FK + one index per real query (from the sequences) | Universal performance hygiene — no "just in case" indexes. |
| Breaking change on an existing table → expand → backfill → contract | Zero-downtime, any DB. |
| No real-looking PII in seeds (`example.test`) | Safety. |

## Protocol

1. **Prereq check (hard).** Both `spec.md` and `sad.md` present, else refuse with a pointer to the missing one.
1a. **Persistence-kind branch (surface-gated).** Read the run's surface (from `sad.md` `target_surfaces`, or the `default_surfaces` fallback — see Inputs). If the surface is a **UI surface with no `backend-service`** (e.g. `[mobile-app]`) and the feature's persistence is **on-device local storage** (Core Data / SwiftData / Room / SQLite / Realm — or a plain key-value / file store), **do not follow the server-SQL path below.** Instead take the **local-persistence branch (step 2a)**. A feature that *does* declare a `backend-service` (even alongside `mobile-app`) keeps the normal server path for the backend's store. When unsure whether persistence is local vs server, ask (one question per [`../_shared/ask-style.md`](../_shared/ask-style.md)).
2. **Derive conventions from the architecture (read-only — never write a rules file).** Read **`architecture-map.md` §Migrations** (the tool/naming `survey` recorded) + the **`sad.md` persistence decisions** (§4 strategy / §5 building blocks / §8 crosscutting) + the **Accepted ADRs** **first** — they choose the migration tool/naming + the DB approach (PK / audit / delete / constraints). **Corroborate** with the live `migrations/` folder + schema (Explore or `ls`) for anything the architecture left implicit — e.g. statement-per-file rules (golang-migrate's transaction-per-file), the next sequence value. Record the migration naming as a **promote-time hint** in the audit report (e.g. «sequential, next ≈ `000023` — `implement` assigns the real number at promotion, since another feature may promote first»). On a **greenfield** repo with no architecture signal, the schema choices are confirmed with the user (steps 4–6), not defaulted to a house style. **Do not pick a final number, do not write into the live `migrations/`, and do not impose a convention the architecture/repo doesn't use** — staging happens in step 9, promotion in `implement`; flag any divergence (architecture vs repo) in the report.
2a. **Local-persistence branch (mobile on-device) — taken only when step 1a routed here.** Server-SQL mechanics (staged `*.up.sql`/`*.down.sql`, reversible migrations, FK-index-per-query, expand→backfill→contract, `migrate up`) **do not apply** — a phone's local store versions forward, and users don't downgrade an installed app's schema, so `.down.sql` reversibility is meaningless. Produce **one of two outcomes**, and skip steps 3–13's SQL generation:
   - **(default) Self-skip → a design note, no schema artifact.** When persistence is a simple key-value / file store, or the real design concern is offline-first / sync / conflict-resolution rather than a schema, `data-model` **self-skips**: write a short note (route it to an ADR if it crosses the blast-radius gate, else a `sad.md §8` crosscutting note) recording *what* is stored locally + *how* (the store kind) + the sync/conflict strategy — and generate **zero** migration files. This is a valid outcome, not a failure (the same shape as the "no schema change" fast-lane skip).
   - **On-device schema section.** When the feature genuinely owns a structured local store (Core Data / SwiftData / Room / SQLite / Realm) with entities worth documenting, write an **on-device schema section** in `data-model.md`: entities + fields + relationships, the **schema version**, and the **migration strategy** (lightweight vs heavyweight / forward-only) — **not** reversible SQL pairs. Follow the repo's detected local-store conventions (Core Data model versioning, Room `@Database(version=)` + `Migration`, etc.); confirm with the user on greenfield.
   Either way: keep the stack-agnostic **safety** discipline that still applies (schema **versioning**, no real-looking PII in any seed/fixture); drop everything that assumes a server SQL migration. State the branch + outcome in the audit report (step 13) and the DoD (SQL-pair clauses are N/A here). Then **skip to step 14** (commit + handoff).
3. **Read prereqs in order:** spec §5 (entity candidates from AC) → sad §5 building blocks (the persistence containers — which container owns which data) → `sad.md §6` sequences (each `writes/reads <entity>` note → an entity + index candidate) → (optional) the Explore-discovered domain layer for a struct-vs-DDL map.
4. **Aggregate roots.** Ask (or infer from AC) which aggregate roots own what — without explicit aggregates the FK graph turns into a hairball. Phrase per [`../_shared/ask-style.md`](../_shared/ask-style.md).
5. **PK strategy.** Follow the repo's detected PK convention; on greenfield (or if an AC demands a specific PK like a lookup slug), confirm with the user — UUID, bigint-identity, sequence, composite, whatever fits. No default imposed.
6. **Columns + constraints** per entity, **matching the repo's conventions**: string/JSON types per the repo's norms (`VARCHAR(N)` sized from AC validation limits / `TEXT` / JSON, as the repo does); audit columns (`created_at` / `updated_at` / none) per the repo's pattern; `CHECK` / DB `DEFAULT` / triggers **iff the repo uses them**; `<!-- TBD -->` where honestly undecided. On greenfield, confirm these with the user.
7. **Indexes per query.** Each sequence note becomes one index candidate; discard candidates with no concrete query; print a "Query it serves" justification column.
8. **Write `docs/features/<slug>/data-model.md`** from [`./templates/data-model.md`](./templates/data-model.md): ER Mermaid (clean ordered block) + entity tables per aggregate + indexes table. **Validate the `erDiagram` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint — valid cardinality glyphs + `type name` attribute lines; fix before continuing).
9. **Generate migration files — STAGED in the feature folder, not the live tree.** A run that finds **no schema change** legitimately produces a minimal `data-model.md` (documenting the existing entities the feature touches) with **zero** staged migrations — that is a valid outcome, not a failure; note that `api` would also have accepted the fast-lane skip (→ [size-matrix fast lane](../_shared/size-matrix.md)). Write the pairs into **`docs/features/<slug>/migrations/`** with a **feature-local ordinal** name (`01_create_<entity>.up.sql` + `.down.sql`, `02_…`) that preserves intra-feature order. The SQL is full and shippable; only the location + the final number differ from a live migration. **Never write into the repo's live `migrations/` here** — `implement` promotes these (assigning the real sequence number / timestamp per the convention detected in step 2, in ordinal order) when it runs the `layer: migration` task. The SQL content rules are unchanged:
   - **Greenfield:** one create-`<entity>` `.up.sql` + `.down.sql` per entity (or per small aggregate). `IF NOT EXISTS` everywhere; `ON CONFLICT DO NOTHING` on seeds.
   - **Existing-table index:** use the concurrent, non-blocking form, and warn that the file must contain only that one statement **if your migration tool wraps each file in a transaction** (e.g. golang-migrate).
   - **New NOT NULL on existing table / rename / drop:** emit the 3-step expand→backfill→contract sequence (separate ordinal files); the user reviews the backfill SQL.
10. **Seeds (3 buckets).** Bootstrap (deterministic hardcoded UUID v7) → first migration; lookup data → separate migration with `ON CONFLICT DO NOTHING`; test fixtures → **NOT** in `migrations/` — generate them in the form the repo uses (factory functions / fixtures / builders), documented under "Test fixtures". **PII guard (hard):** no real-looking email/name/phone in any seed — use `admin@example.test`, `user-<uuid>@example.test`, `Test User`.
11. **Drift detection (always; `--drift-only` short-circuits here).** If the Explore subagent found a domain layer, map each field to a column and report `field-without-column` / `column-without-field` / `type-mismatch` / `nullability-mismatch`; auto-propose fix migrations under `_drift/` for the user to review.
12. **Self-check (4 mandatory, stack-agnostic).** Naming matches the **repo's** convention; **down reversibility** (every CREATE has a DROP, every ADD COLUMN a DROP COLUMN, every CREATE INDEX a DROP INDEX); **FK indexes** (every `REFERENCES other(id)` has an index on the FK column); **convention adherence** (the schema follows the repo's detected conventions — flag any deliberate divergence in the report, never silently impose a house style). Any failure → fix or surface, never silent-commit.
13. **Audit report** `docs/features/<slug>/_audit/data-model-<date>.md`: the **staged** migration files (their `docs/features/<slug>/migrations/<NN>_*` paths), the **promote-time convention hint** (e.g. «repo is sequential, next ≈ `000024` — `implement` assigns the real number at promotion»), convention deviations, drift findings, breaking-change decompositions, every `<!-- TBD -->`. State plainly: «migrations are staged — not yet in the live `migrations/` tree; `implement` promotes them». Next stage `api <slug>`.
14. **Propose commit + handoff.** `data-model: <slug> (data-model.md + staged migrations)`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`data-model.md`, staged `migrations/`) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)): forward `/sdd:api <slug>`; `api`'s N/A condition = **no contract change** (no new/changed endpoint, event, or public signature), skip target `/sdd:tasks <slug>` (on `quick` — auto-skip with the reason + inverted `↳ or`; on `standard` — offer the `↳ or`; on `full` — no skip line).

## Definition of Done

> **Local-persistence branch (step 2a) — the SQL clauses below are N/A.** DoD instead: either a
> self-skip note (ADR or `sad.md §8`) recording what's stored locally + the sync/conflict strategy and
> **zero** migration files, **or** an on-device schema section (entities + schema-version + migration
> strategy) — the branch + outcome stated in the audit report. The versioning + no-PII safety checks
> still apply; reversibility / FK-index / staged-SQL checks do not.

- `data-model.md` exists with ER + every entity + every index carrying a query justification.
- For every entity/change, a matched `.up.sql` + `.down.sql` pair exists **under `docs/features/<slug>/migrations/`** (staged, feature-local ordinal names) — **nothing was written into the live `migrations/` tree** (that's `implement`'s promotion step). The SQL still follows the repo's detected convention.
- All 4 self-checks pass.
- Audit report written (with the staged paths + the promote-time number hint); drift report (with `_drift/*.sql`) if drift was detected.
- The step-12 4-mandatory check + step-11 drift detection are this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **Imposing a DB philosophy the repo (or the user) didn't ask for** — forcing UUID v7 / hard-delete / no-`updated_at` / no-`CHECK` on a repo that does otherwise, or writing a `.claude/rules/migrations.md` to legislate one. `data-model` **detects and follows** the repo's conventions; if a repo uses `CHECK` constraints or `updated_at`, match it.
- **Index "just in case"** with no concrete query. Each index costs writes.
- **One mega-migration with 5 ALTERs** — rollback becomes all-or-nothing. Split.
- **DROP COLUMN before deploying new code** — breaks running pods between phases. Always 3-step.
- **Real-looking PII in seeds.** Use `example.test`.
- **Writing the migration into the live `migrations/` tree at design time.** That drops a half-designed, runnable schema where a stray `migrate up` (CI, a teammate's loop, a deploy) can apply it before the feature is built or reviewed — and grabs a sequence number early, colliding with other in-flight features. Stage under `docs/features/<slug>/migrations/`; `implement` promotes it (with the real number) when the code that needs it is actually being written.
- **Silently switching the repo's migration naming convention.** Detect, follow, and flag in the report.
- **Live DB introspection with no offline fallback** — CI has no DB credentials; parse the SQL files.

## References & template

- [`./templates/data-model.md`](./templates/data-model.md) — output structure for the design doc.
