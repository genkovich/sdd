---
name: classify-size
model: haiku
effort: low
agents: []
description: >
  Use to classify a feature into XS/S/M/L/XL and write docs/features/{slug}/.size so
  later skills know how much of each artifact to produce. Triggers on "classify size",
  "feature size", "is this XS or M for {slug}", "size {slug}", "/sdd-classify-size {slug}",
  "класифікуй розмір {slug}", "який розмір фічі", "XS чи M". Asks four AskUserQuestion
  (PR count / time / new module-API-migration / breaking changes), maps to a size class via
  the shared size matrix, confirms with the user, and writes the one-line .size file. Syncs
  with spec.md frontmatter feature_size: if present (warns on conflict).
---

# Skill: classify-size

Atomic skill — classifies a feature into XS/S/M/L/XL and fixes the result in
`docs/features/<slug>/.size`. This is the single source of size-aware behaviour for the rest
of the pipeline: later skills read `.size` to decide MVP vs Full output depth.

This skill is the **canonical owner of the size matrix** → [`../_shared/size-matrix.md`](../_shared/size-matrix.md). The classification rules, the MVP-vs-Full table, and the one-sentence rule all live there; this skill only runs the dialogue and writes the file.

## Owner

PM or Tech Lead (driver of the intake phase). An architect may escalate S → M on spotting a new subsystem.

## Inputs

- `<slug>` — feature slug.
- (Optional) the idea / intake note — for a rough starting hint. The skill works without it.

## Protocol

1. **Check existing.** `test -f docs/features/<slug>/.size`. If it exists, read the value and ask «`.size` is currently `<X>`. Reclassify?». On «no» — STOP (suggest editing, don't overwrite silently).
2. **Ask the four signals** — one `AskUserQuestion` each, phrased per [`../_shared/ask-style.md`](../_shared/ask-style.md):
   - **PR count** — `1` / `2–5` / `5–15` / `15+`.
   - **Time to merge the main part** — `≤1 day` / `~1 week` / `1–2 sprints` / `>1 month`.
   - **New module / new API / DB migration** — `none` / `one of three` / `two of three` / `all three`.
   - **Breaking changes for consumers** — `no` / `internal only` / `public clients`.
3. **Map to a class** using the table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md). On an edge case, name the dominant signal aloud («M because it adds a new API + 1–2 sprints, even though PR count is on the S/M border»). For an all-maximums answer, ask explicitly «needs a separate roadmap?» → yes = XL.
4. **Confirm with the user.** `AskUserQuestion`: «Classifying as `<size>` (<one-line rationale>). Lock it in?» — `Yes` / `No, I want <X>` / `Reclassify`.
5. **Write `.size`.** One line, plain text, only `XS`/`S`/`M`/`L`/`XL` — no comments, no frontmatter. `docs/features/<slug>/.size`.
6. **Sync with spec frontmatter (if present).** If `docs/features/<slug>/spec.md` exists, check its `feature_size:` field. Same value → OK. Conflict → WARN and resolve with the user (update one side). Missing → suggest adding `feature_size: <size>`.
7. **Propose commit + handoff.** `size: <slug> classified as <size>` (or fold into the intake commit if a wrapper called this). Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) — *What I did* + *Review* (`.size`) + *Run next*: resume your backbone stage (e.g. `/sdd-specify <slug>`); `/clear` optional.

## Definition of Done

- `docs/features/<slug>/.size` holds exactly one of XS/S/M/L/XL.
- The user confirmed the classification (never silent).
- If `spec.md` exists, its `feature_size:` is in sync (no drift).

## Anti-patterns

- **Self-classify without confirmation.** The skill proposes; the user locks it.
- **Optimistic «it's probably S».** Run the four questions — a week later the skipped design hurts.
- **Skipping the module/API/migration and breaking-change questions.** They are what separates S from M.
- **Overwriting an existing `.size` without asking.**
- **A multi-line `.size` with comments.** Wrappers grep it cheaply — keep it one bare word.

## Example invocation

> **User:** «classify size rate-limiting-per-user»
> **Skill:** `.size` absent → asks the four questions (`2–5 PR`, `~1 week`, `one of three — new API`, `internal only`) → maps to **S** (rationale: one API endpoint + ~1 week + internal breaking) → confirms → writes `docs/features/rate-limiting-per-user/.size` = `S` → `spec.md` not yet written, skip sync → commit `size: rate-limiting-per-user classified as S`.
