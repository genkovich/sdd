---
name: classify-size
model: haiku
effort: low
agents: []
description: >
  Use to classify a feature into XS/S/M/L/XL and write docs/features/{slug}/.size plus the
  pipeline route docs/features/{slug}/.route (quick|standard|full) so later skills know how
  much of each artifact to produce and how handoffs resolve skips. Triggers on "classify size",
  "feature size", "is this XS or M for {slug}", "size {slug}", "change route", "/sdd:classify-size {slug}".
  Asks four AskUserQuestion
  (PR count / time / new module-API-migration / breaking changes), maps to a size class via
  the shared size matrix, derives the default route (XS/S→quick, M→standard, L/XL→full),
  confirms size + route in ONE question, and writes the one-line .size and .route files — the
  source of truth; the feature_size: frontmatter mirrors in spec.md and sad.md are re-synced
  to it on every (re)classification.
---

# Skill: classify-size

Atomic skill — classifies a feature into XS/S/M/L/XL and fixes the result in
`docs/features/<slug>/.size`, plus the pipeline **route** (`quick` / `standard` / `full`) in
`docs/features/<slug>/.route`. This is the single source of size- and route-aware behaviour for
the rest of the pipeline: later skills read `.size` to decide MVP vs Full output depth, and
their handoffs read `.route` to decide how optional-stage skips resolve (auto-skip / offered /
never — the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)).

This skill is the **canonical owner of the size matrix** → [`../_shared/size-matrix.md`](../_shared/size-matrix.md). The classification rules, the MVP-vs-Full table, and the one-sentence rule all live there; this skill only runs the dialogue and writes the file.

**Called inline by `specify`.** When `.size` is absent at the start of the backbone, `specify` step 1 runs this protocol inline (same signals, same file, folded into one bundled question) — this skill stays the standalone utility for classifying up front or **re-classifying when scope changes**; the protocol is never duplicated elsewhere.

## Owner

PM or Tech Lead (driver of the intake phase). An architect may escalate S → M on spotting a new subsystem.

## Inputs

- `<slug>` — feature slug.
- (Optional) the idea / intake note — for a rough starting hint. The skill works without it.

## Protocol

1. **Check existing.** `test -f docs/features/<slug>/.size` (and `.route`). If `.size` exists, read both values and ask «`.size` is currently `<X>` (route `<Y>`). Reclassify?». On «no» — STOP (suggest editing, don't overwrite silently). Re-running just to switch the route is a legal, common case — mid-flight override per the Routes table.
2. **Ask the four signals** — one `AskUserQuestion` each, phrased per [`../_shared/ask-style.md`](../_shared/ask-style.md):
   - **PR count** — `1` / `2–5` / `5–15` / `15+`.
   - **Time to merge the main part** — `≤1 day` / `~1 week` / `1–2 sprints` / `>1 month`.
   - **New module / new API / DB migration** — `none` / `one of three` / `two of three` / `all three`.
   - **Breaking changes for consumers** — `no` / `internal only` / `public clients`.
3. **Map to a class** using the table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md). On an edge case, name the dominant signal aloud («M because it adds a new API + 1–2 sprints, even though PR count is on the S/M border»). For an all-maximums answer, ask explicitly «needs a separate roadmap?» → yes = XL.
4. **Confirm size + route — ONE question.** Derive the default route from the size (**XS/S → `quick`, M → `standard`, L/XL → `full`** — the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)). Then one `AskUserQuestion`: «Classifying as `<size>` (<one-line rationale>) → route `<route>` (<one-line what the route does>). Lock both in?» — options: `Yes` / `Yes, but route <other>` / `No, I want size <X>` / `Reclassify`. Never a second question just for the route.
5. **Write `.size` + `.route`.** Each one line, plain text — `.size` only `XS`/`S`/`M`/`L`/`XL`; `.route` only `quick`/`standard`/`full` — no comments, no frontmatter. `docs/features/<slug>/.size`, `docs/features/<slug>/.route`.
6. **Re-sync the frontmatter mirrors (`.size` is the source of truth).** `feature_size:` lives in up to three places: the `.size` file (canonical) plus the `spec.md` and `sad.md` frontmatter (human-readable mirrors). For each of the two files that exists: same value → OK; different (a reclassification, or a hand-edited mirror) → **update the frontmatter to the new `.size` value** and say so — never leave a mirror stale; missing field → suggest adding `feature_size: <size>`. If the user insists a mirror is the right value, that's a reclassification — loop back to step 4 and re-confirm, then re-sync.
7. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read the written files from disk and verify **3 items**: (1) `.size` holds exactly one of {XS, S, M, L, XL} (one bare word, no trailing content); (2) `.route` holds exactly one of {quick, standard, full}; (3) both frontmatter mirrors (`feature_size:` in `spec.md` and `sad.md`, for whichever exists) match `.size`. Fix + re-check ≤2 cycles; surface anything unresolved.
8. **Propose commit + handoff.** `size: <slug> classified as <size> (route <route>)` (or fold into the intake commit if a wrapper called this). Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) — *What I did* (incl. «self-check: 3/3 pass») + *Review* (`.size`, `.route`) + *Run next*: resume your backbone stage (e.g. `/sdd:specify <slug>`); `/clear` optional.

## Definition of Done

- `docs/features/<slug>/.size` holds exactly one of XS/S/M/L/XL; `docs/features/<slug>/.route` holds exactly one of quick/standard/full.
- The user confirmed the classification — size AND route in one question (never silent, never two questions).
- If `spec.md` / `sad.md` exist, their `feature_size:` mirrors match `.size` (no drift; `.size` is the source of truth).

## Anti-patterns

- **Self-classify without confirmation.** The skill proposes; the user locks it.
- **Optimistic «it's probably S».** Run the four questions — a week later the skipped design hurts.
- **Skipping the module/API/migration and breaking-change questions.** They are what separates S from M.
- **Overwriting an existing `.size` / `.route` without asking.**
- **A multi-line `.size` / `.route` with comments.** Wrappers grep them cheaply — keep each one bare word.
- **A second question just for the route.** Size + route confirm together; the route option rides in the same `AskUserQuestion`.

## Example invocation

> **User:** «classify size rate-limiting-per-user»
> **Skill:** `.size` absent → asks the four questions (`2–5 PR`, `~1 week`, `one of three — new API`, `internal only`) → maps to **S** → default route **quick** → confirms both in one question (rationale: one API endpoint + ~1 week + internal breaking) → writes `docs/features/rate-limiting-per-user/.size` = `S` and `.route` = `quick` → `spec.md` not yet written, skip sync → commit `size: rate-limiting-per-user classified as S (route quick)`.
