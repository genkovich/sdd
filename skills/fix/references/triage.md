# Fix triage — tracing a symptom to the spec

> Step-2 detail for [`../SKILL.md`](../SKILL.md). The spine states the three outcomes; this file
> holds the mechanics: how to find the owning feature, the decision table, the `added-by-fix`
> marker, no-spec mode, and the recurrence check.

## Finding the owning feature

1. Extract the **domain nouns** from the reproduction statement («doing X, expected Y, got Z») —
   the entities and actions, not the technical symptoms (`discount`, `apply`, `order`; not
   `duplicate row`, `500`).
2. Grep `docs/features/*/spec.md` for those terms; rank candidate slugs by hit count, §4/§5 hits
   weighing more than §1 prose.
3. One clear winner → proceed. Several plausible owners (or zero hits but `docs/features/` is
   non-empty) → confirm with **one** `AskUserQuestion` listing the candidates (phrasing per
   [`../../_shared/ask-style.md`](../../_shared/ask-style.md)) — never guess a slug silently.
4. **Recurrence check (before triage):** grep the candidate slug's `_fixes/*.md` for the same
   symptom terms. A match means this bug (or its sibling) was fixed before — read that record
   first. The new record links the old one, and the right move is usually to **strengthen the
   old pinning test** (it let the regression through), not to write a parallel one.

## The decision table (ask in order)

| # | Question | Yes → | No → |
|---|---|---|---|
| 1 | Does a §5 AC describe the expected behaviour the reproduction names? | → 2 | **(c) Gap** |
| 2 | Does the observed behaviour violate that AC **as written**? | → 3 | re-check the slug/AC — the bug may belong elsewhere, or it's not a bug |
| 3 | Could a reasonable implementer read the AC and still produce the observed behaviour (ambiguous wording, undefined edge, missing bound)? | **(b) Spec-bug** | **(a) Regression** |

Question 3 is the load-bearing one: it separates «the code drifted from a clear contract»
(regression — fix code only) from «the contract permitted the bug» (spec-bug — fix the wording
too, or the next implementation reintroduces the bug legally).

## What each branch changes

| Branch | Code | Spec | Record's «Spec patch» section |
|---|---|---|---|
| (a) Regression | RED → GREEN fix | nothing — AC re-verified | «none — spec was right; AC-NN re-verified» |
| (b) Spec-bug | RED → GREEN fix (against the **corrected** reading) | AC wording patched, before → after shown to the user | the before/after wording |
| (c) Gap | RED → GREEN fix | new AC appended to §5 with the marker | the new AC text |
| No-spec | RED → GREEN fix | none exists to patch | «no spec to patch — brownfield; survey recommended» |

## The `added-by-fix` marker

A gap-branch AC is appended to spec §5 as a normal AC plus an adjacent comment:

```md
- AC-09: a discount is applied to an order at most once, regardless of repeated
  apply requests. <!-- added-by-fix: 2026-06-12 -->
```

The marker is **archaeology, not a status** — `clarify`, `sequences`, `plan-tests` and `review`
treat the AC exactly like any other (it must be covered by flows and tests on the next pass).
It only records that the AC entered the spec through a bug, not through `specify` — useful when
auditing why the original spec missed it.

One nuance: «like any other» is a floor, not a discount. An added-by-fix AC is **higher-risk by
construction** — it's evidence the spec already missed this case once — so the next `review` /
`implement` pass verifies it at least as strictly as the rest, with the pinning test that caught
the bug as the minimum baseline, never the whole proof.

## No-spec mode (brownfield soft gate)

Two ways in: `docs/features/` doesn't exist at all, or it exists but no spec plausibly owns the
symptom (the bug lives in pre-SDD code). Either way:

- run intake → RED → GREEN → gate → record as usual;
- the record's triage field is `no-spec`, and its «Spec patch» section states why;
- the handoff recommends `/sdd:survey` (map the codebase so future fixes have something to trace
  to) — a recommendation, never a blocker.

Hard-refusing here would lock out exactly the user this skill serves first: someone with a bug
in a repo that never ran the backbone.
