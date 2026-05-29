---
name: data-model
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to design the data model AND generate the actual forward + rollback migrations in one
  pass — shippable SQL, not a plan. Triggers on "data model for {slug}", "schema for {slug}",
  "generate migrations for {slug}", "DB design + migration", "/sdd-data-model {slug}",
  "модель даних для {slug}", "схема для {slug}", "згенеруй міграції". Reads spec.md §5 +
  sad.md §6.4 ER + the sequence diagrams, then writes docs/features/{slug}/data-model.md plus
  paired *.up.sql / *.down.sql migrations and an audit report. Greenfield-first; brownfield
  delta via --mode brownfield; drift-only via --drift-only. Hard-refuses if spec.md or sad.md
  is missing. Stack-agnostic: detects the repo's migration convention and domain layer.
---

# Skill: data-model

End-to-end runner for the persistence cut: data model + migrations + drift check in one pass. Greenfield-first by default; brownfield delta as `--mode brownfield`. Output is **shippable** — full `.up.sql` + `.down.sql` ready to run, not a plan.

The DB-as-dumb-storage defaults below are a **starting opinion, not law.** On first run they're written to `.claude/rules/migrations.md`; from then on the skill **follows whatever that file says** and detects/respects an existing one. A team that wants `updated_at`, soft-deletes, or `CHECK` constraints just edits the rules file — the skill adapts (the proving run did exactly this: it followed a repo that opts into `CHECK` + `updated_at`). The size matrix (→ [`../_shared/size-matrix.md`](../_shared/size-matrix.md)) governs how much you produce; the aggregate-roots dialogue uses [`../_shared/ask-style.md`](../_shared/ask-style.md).

## Owner

Backend Lead.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse if missing):** `docs/features/<slug>/spec.md` (entities live in §5 acceptance criteria) and `docs/features/<slug>/sad.md` (§6.4 ER stub). Missing → «run `specify` / `design` first».
- Optional: the sequence diagrams in `sad.md §6` — each `writes/reads <entity>` note is an index candidate (one index per query, justified).
- Optional: `docs/architecture-map.md` (from `survey`) — read it for the module layout + persistence conventions instead of re-scanning. For **drift detection** specifically, `explorer` still reads the **actual domain layer** (the map gives layout; drift needs the real struct/field source). Stack-agnostic — no hard-coded path or language.

## Defaults (the opinionated set — written to the baseline rules file)

| Topic | Default | Why |
|---|---|---|
| Migration filename | **detect the repo's existing convention and follow it**; greenfield default = `<YYYYMMDDhhmmss>_<verb>_<entity>` | Respect what's there (sequential repos stay sequential); timestamps avoid branch collisions on a fresh repo. |
| Idempotency | `CREATE TABLE/INDEX IF NOT EXISTS`, `ON CONFLICT DO NOTHING` for seeds | Re-running a partially-applied migration does not error. |
| Audit columns | `created_at` only (your DB's "timestamp with time zone", `NOT NULL DEFAULT now()`) — **no `updated_at`** | Immutable-leaning; change history goes through an audit table or event log. |
| Delete strategy | Hard delete + audit table if history is required | No `deleted_at`, no status-as-delete. |
| PK | UUID v7, generated app-side | Cursor pagination, no insert-sequence contention. |
| Naming | `plural snake_case` tables, `snake_case` columns | Common SQL convention. |
| Indexes | One per query (from sequences); on an existing table use the non-blocking concurrent form | Each index has a write cost. |
| Breaking change / new NOT NULL on existing table | Auto-decompose: expand → backfill → contract (3 migrations) | Zero-downtime by default. |
| String columns | bounded `VARCHAR(N)`; unbounded text only for URLs / long descriptions | Schema as documentation. |
| Opaque payload | the JSON column type **only** for semantically opaque data | Structured fields → first-class columns. |
| Off by default (opt in via the rules file) | `CHECK`, `TRIGGER`, business-literal `DEFAULT`, sequence-as-PK, multi-DB / partitioning / materialized views | Keeps the DB dumb + business logic in code by default — enable any of these in `.claude/rules/migrations.md` if your team prefers them. |

## Protocol

1. **Prereq check (hard).** Both `spec.md` and `sad.md` present, else refuse with a pointer to the missing one.
2. **Rules bootstrap + convention detect.** If `.claude/rules/migrations.md` is absent, copy [`./templates/migrations-baseline.md`](./templates/migrations-baseline.md) there and tell the user. **Inspect the existing `migrations/` folder** (Explore or `ls`): if files are sequential (`000022_*.sql`), continue sequential (next = `000023`); if timestamped, continue timestamps; if empty, use the timestamp default. Never silently switch a repo's convention — flag it in the report.
3. **Read prereqs in order:** spec §5 (entity candidates from AC) → sad §6.4 (ER stub) → `sad.md §6` sequences (each write/read note → an index candidate) → (optional) the Explore-discovered domain layer for a struct-vs-DDL map.
4. **Aggregate roots.** Ask (or infer from AC) which aggregate roots own what — without explicit aggregates the FK graph turns into a hairball. Phrase per [`../_shared/ask-style.md`](../_shared/ask-style.md).
5. **PK strategy.** UUID v7 app-side by default; confirm only if an AC demands a different PK (e.g. a lookup slug).
6. **Columns + constraints** per entity: bounded `VARCHAR(N)` from AC validation limits; unbounded text only for URLs/long text; the opaque-JSON type only for opaque payloads (one-line justification in the Notes column); `created_at` timestamp `NOT NULL DEFAULT now()`, **no `updated_at`**; `<!-- TBD -->` where honestly undecided.
7. **Indexes per query.** Each sequence note becomes one index candidate; discard candidates with no concrete query; print a "Query it serves" justification column.
8. **Write `docs/features/<slug>/data-model.md`** from [`./templates/data-model.md`](./templates/data-model.md): ER Mermaid (clean ordered block) + entity tables per aggregate + indexes table. **Validate the `erDiagram` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint — valid cardinality glyphs + `type name` attribute lines; fix before continuing).
9. **Generate migration files** in the repo's migrations folder, following the detected convention:
   - **Greenfield:** one create-`<entity>` `.up.sql` + `.down.sql` per entity (or per small aggregate). `IF NOT EXISTS` everywhere; `ON CONFLICT DO NOTHING` on seeds.
   - **Existing-table index:** use the concurrent, non-blocking form, and warn that the file must contain only that one statement **if your migration tool wraps each file in a transaction** (e.g. golang-migrate).
   - **New NOT NULL on existing table / rename / drop:** emit the 3-step expand→backfill→contract sequence (separate files); the user reviews the backfill SQL.
10. **Seeds (3 buckets).** Bootstrap (deterministic hardcoded UUID v7) → first migration; lookup data → separate migration with `ON CONFLICT DO NOTHING`; test fixtures → **NOT** in `migrations/` — generate them in the form the repo uses (factory functions / fixtures / builders), documented under "Test fixtures". **PII guard (hard):** no real-looking email/name/phone in any seed — use `admin@example.test`, `user-<uuid>@example.test`, `Test User`.
11. **Drift detection (always; `--drift-only` short-circuits here).** If the Explore subagent found a domain layer, map each field to a column and report `field-without-column` / `column-without-field` / `type-mismatch` / `nullability-mismatch`; auto-propose fix migrations under `_drift/` for the user to review.
12. **Self-check (4 mandatory).** Naming (`plural snake_case`); **down reversibility** (every CREATE has a DROP, every ADD COLUMN a DROP COLUMN, every CREATE INDEX a DROP INDEX); **FK indexes** (every `REFERENCES other(id)` has an index on the FK column); **forbidden features** (grep for `CHECK (`, `CREATE TRIGGER`, business-literal `DEFAULT '` — fail with line numbers). Any failure → fix or surface, never silent-commit.
13. **Audit report** `docs/features/<slug>/_audit/data-model-<date>.md`: generated files, default deviations (e.g. «repo is sequential, I continued sequential»), drift findings, breaking-change decompositions, every `<!-- TBD -->`, next stage `api <slug>`.
14. **Propose commit.** `data-model: <slug> (data-model.md + migrations)`. Next: Backend Lead → `api <slug>`.

## Definition of Done

- `data-model.md` exists with ER + every entity + every index carrying a query justification.
- For every entity/change, a matched `.up.sql` + `.down.sql` pair exists, following the repo's migration convention.
- All 4 self-checks pass.
- Audit report written; drift report (with `_drift/*.sql`) if drift was detected.

## Anti-patterns

- **Business defaults in the DB** (`DEFAULT 'pending'`). Only `DEFAULT now()` for timestamps; the rest in app code.
- **CHECK constraints / triggers / stored procedures** for business invariants. DB stays dumb.
- **Index "just in case"** with no concrete query. Each index costs writes.
- **Unbounded text for everything** — bounded strings get `VARCHAR(N)`.
- **PK from a DB sequence** — default UUID v7 app-side.
- **One mega-migration with 5 ALTERs** — rollback becomes all-or-nothing. Split.
- **DROP COLUMN before deploying new code** — breaks running pods between phases. Always 3-step.
- **Real-looking PII in seeds.** Use `example.test`.
- **Silently switching the repo's migration naming convention.** Detect, follow, and flag in the report.
- **Live DB introspection with no offline fallback** — CI has no DB credentials; parse the SQL files.

## References & template

- [`./templates/data-model.md`](./templates/data-model.md) — output structure for the design doc.
- [`./templates/migrations-baseline.md`](./templates/migrations-baseline.md) — baseline `.claude/rules/migrations.md` copied at step 2 when missing.
