# Migration rules — baseline

<!-- Bootstrapped by the sdd `data-model` skill. Edit freely — these are an opinionated default. -->

## Filenames & staging

- **Design-stage migrations are STAGED, not live.** `data-model` writes the pair under `docs/features/<slug>/migrations/` with a feature-local ordinal (`01_<verb>_<entity>.up.sql` + `.down.sql`, `02_…` preserving order) — **never** into the live `migrations/` tree. `implement` **promotes** them into `migrations/` when it builds the feature, assigning the real name. Rationale: a design-stage schema in the live tree can be applied by a stray `migrate up` before the feature exists.
- **Follow the repo's existing convention at promote-time.** If `migrations/` uses sequential numbers (`000022_*.sql`), the promoted file is the next free number (`000023_*`). If it uses timestamps, use a timestamp. The number is assigned **at promotion, not at design**, so two features in flight don't grab the same number.
- Greenfield default (empty `migrations/`): timestamp `<YYYYMMDDhhmmss>_<verb>_<entity>` assigned at promote-time.

## Hard rules (DB as dumb storage)

- No `CHECK` constraints on business invariants.
- No triggers, no stored procedures.
- No business-literal `DEFAULT` (only `DEFAULT now()` for timestamps).
- Business logic lives in app code.

## Required constraints

- Every `REFERENCES other_table(id)` is followed by an index on the FK column (same or next migration).
- Every `.up.sql` has a matching `.down.sql` that fully reverses it.
- `CREATE TABLE` / `CREATE INDEX` use `IF NOT EXISTS`.
- Seed `INSERT` uses `ON CONFLICT DO NOTHING`.

## Defaults

- **PK:** UUID v7, generated app-side. Column type `UUID`.
- **Timestamps:** your DB's timestamp-with-time-zone type, `NOT NULL DEFAULT now()`.
- **Strings:** bounded `VARCHAR(N)`; unbounded text only for URLs / long descriptions.
- **Soft delete:** not used. Hard delete + an audit table if history is required.
- **Audit columns:** `created_at` only. `updated_at` is opt-in per entity and must be justified (usually it means an audit-log or event-sourcing alternative was rejected).
- **Naming:** `plural snake_case` tables, `snake_case` columns.
- **Opaque-JSON column type:** only for semantically opaque payloads. Structured fields → first-class columns.

## Zero-downtime patterns (mandatory for existing tables)

- New NOT NULL column → 3-step (add nullable → backfill → set NOT NULL).
- New index on an existing table → the concurrent, non-blocking form. **If your migration tool wraps each file in a transaction (e.g. golang-migrate), the concurrent index must be the only statement in the file.**
- Rename / drop column → 3-step (add new + dual-write in app code → backfill → drop old). Each phase = separate PR + deploy.

## Seeds

- **Bootstrap** (admin user, default org): hardcoded deterministic UUID v7 in a migration.
- **Lookup** (statuses, currencies): separate migration, `INSERT ... ON CONFLICT DO NOTHING`.
- **Test fixtures:** NOT in `migrations/`. Generate them in the form your repo uses (factory functions / fixtures / builders).
- **PII guard:** no real-looking emails / names. Use `admin@example.test`, `user-<uuid>@example.test`, `Test User`.

## Out of scope

Multi-DB (read replicas, sharding), partitioning, materialized views — performance/scale topics owned by SRE/DBA, decided per-project with a separate ADR.
