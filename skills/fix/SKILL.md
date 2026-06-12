---
name: fix
model: opus
effort: high
agents: [explorer]
description: >
  Use to fix a reported bug spec-first: reproduce it, trace the symptom to the owning feature's
  acceptance criteria, pin it with a failing (RED) test, apply the minimal GREEN fix through the
  same per-task gate implement uses, then patch the spec so the bug class can't silently return.
  Triggers on "fix {bug}", "fix the bug in {slug}", "bug in {feature}", "/sdd:fix {slug}",
  "regression in {slug}", "полагодь баг", "виправ багу", "регресія в {slug}", "чому зламалось".
  Triage is three-way: AC exists and is violated (regression) / AC is ambiguous (spec-bug —
  patch the wording) / no AC covers it (gap — add one, marked added-by-fix). Works on a repo
  with no specs at all (soft mode — code-first, recommends survey after). Writes a fix record
  under docs/features/{slug}/_fixes/ and commits with an SDD-Fix trailer.
---

# Skill: fix

The **bugfix entry point** — the backbone in miniature, sized for «it's broken», not «build a feature». A bug is treated as **evidence about the spec**, not only about the code: either an acceptance criterion is violated (the code regressed), the AC was ambiguous enough to permit the behaviour (the spec is the root cause), or nothing covers it (a gap). So the fix always lands in two places — the **code** (RED → GREEN through the same gate `implement` runs) and the **spec** (a surgical AC patch) — tied together by a small fix record.

This skill keeps only its own machinery. Question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md); RED-classification semantics → [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) (reused, never duplicated); dispatch policy → [`../_shared/agent-roster.md`](../_shared/agent-roster.md).

## Owner

The engineer on the bug (drives). PM / Tech Lead is consulted only when triage lands on «spec-bug» or «gap» — changing an AC is a product decision, not a code one.

## Inputs

- `<slug>` — optional; pass it when you know which feature owns the bug, otherwise step 2 finds it from the symptom.
- The bug report, in any form — a sentence, a stack trace, a failing request, a screenshot description.
- **Soft gate (never hard-refuse):** `docs/features/` with ≥1 `spec.md`. Absent (a brownfield repo that never ran the backbone) → still run, in **no-spec mode**: steps 1 → 3 → 4 → record, skip the spec patch, and recommend `/sdd:survey` in the handoff.
- (Optional) `.claude/sdd.local.md` — gate command overrides; otherwise the commands are detected per `implement`'s cascade.

No depth dial and no `.size` here — a fix is one size, and the interview is the bug report itself.

## Protocol

1. **Intake — reproduce before touching anything.** At most 1–2 `AskUserQuestion` (phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md)), only for what the report doesn't already say: expected vs actual, the steps, the scope (one user? all? since when?). Outcome: a one-line reproduction statement — «doing X, expected Y, got Z». A bug you can't state this way isn't ready to fix.
2. **Trace to spec (triage).** Grep `docs/features/*/spec.md` (+ the candidate slug's `_fixes/` for a recurrence) for the reproduction's domain terms; locate the owning slug and the closest §5 AC. In parallel, dispatch [`explorer`](../../agents/explorer.md) — `subagent_type: "sdd:explorer"` (fallback `Explore` / inline per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — to localize the code path. Three outcomes (decision table → [`./references/triage.md`](./references/triage.md)):
   - **(a) Regression** — an AC describes the expected behaviour and the code violates it. The spec is right; only the code changes.
   - **(b) Spec-bug** — the AC exists but a reasonable implementer could read it and produce the observed behaviour. The wording is the root cause — the AC gets patched (with the user, step 5).
   - **(c) Gap** — no AC covers the behaviour. A new AC is added to §5, marked `<!-- added-by-fix: <date> -->`.
   - **No-spec mode** — no `docs/features/` (or no spec plausibly owns the symptom): skip the spec patch, say so in the record, recommend `survey`.
3. **RED — pin the bug with a failing test.** Write the **minimal** test that reproduces the bug at the level the behaviour implies (unit for a rule, integration for a dependency behaviour, e2e for a flow). Run it and classify the first run per [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) — it must be a **GOOD red** (fails on the assertion that encodes the *expected* behaviour); quote the failing line. A bug that can't be pinned by a test → STOP and say so — an unverifiable fix is a guess.
4. **GREEN + GATE — minimal fix.** Make the RED test pass with the smallest change; **no drive-by refactors** (anything the fix exposes goes to the record's follow-ups). Then the same per-task gate `implement` runs: unit + lint + vet (+ integration when available), via the detected commands (detection cascade → [`../implement/references/command-detection.md`](../implement/references/command-detection.md)). Red gate → fix it, never commit around it.
5. **Spec patch + fix record.** Apply the step-2 branch — (a) nothing to patch, re-verify the AC; (b) patch the AC wording; (c) add the new AC with the marker. **Any spec change is confirmed with the user** in one `AskUserQuestion` (before/after wording shown). Then write `docs/features/<slug>/_fixes/<date>-<short-slug>.md` from [`./templates/fix-record.md`](./templates/fix-record.md): symptom → root cause → the pinning test → the spec patch (or why there is none).
6. **Commit + handoff.** Propose commit `fix: <slug> <short summary>` with trailers `SDD-Fix: <date>-<short-slug>` and `SDD-AC: <id>` (when an AC was traced). Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant — `/clear` optional): *What I did* + *Review* (the diff, `_fixes/<date>-<short-slug>.md`, the spec patch if any) + *Run next*: resume what you were doing; **when the fix touched >5 files or crossed a module boundary, recommend `/sdd:review <slug>`** — a recommendation, not a gate.

## Definition of Done

- The bug is reproduced by a test that **failed before the fix and passes after** — GOOD red proven, failing line quoted.
- The gate is clean: unit + lint + vet (+ integration where available).
- The triage outcome is explicit — regression / spec-bug / gap / no-spec — and the matching spec patch is applied (or its absence explained in the record).
- `docs/features/<slug>/_fixes/<date>-<short-slug>.md` exists: symptom, root cause, the test, the spec patch, follow-ups.
- The commit carries the `SDD-Fix:` trailer (+ `SDD-AC:` when traced); any spec change was user-confirmed.

## Anti-patterns

- **Fixing without a pinning test.** «It works now» with no RED proof is a guess that re-breaks silently — the exact failure mode this skill exists to stop.
- **Patching code when the spec was the bug.** If the AC permitted the behaviour, the wording is the root cause; leave it unpatched and the next implementation reintroduces the bug legally.
- **Silent spec edits.** Every AC patch/addition is confirmed with the user — the spec is a contract, not a scratchpad.
- **Drive-by refactoring.** The fix commit is minimal; refactors the fix exposed go to the record's follow-ups, not into the same diff.
- **Skipping the gate because the change is «one line».** One-line fixes break suites just fine.
- **Hard-refusing on a repo without specs.** A brownfield bug is this skill's front door — degrade to no-spec mode and recommend `survey`, never block.
- **Writing a parallel test when `_fixes/` shows the same symptom was fixed before.** That's a recurrence — read the old record and **strengthen its test** instead.

## References & template

- [`./references/triage.md`](./references/triage.md) — the symptom→spec trace: grep strategy, the regression / spec-bug / gap decision table, the `added-by-fix` marker, no-spec mode, the recurrence check.
- [`./templates/fix-record.md`](./templates/fix-record.md) — the fix-record scaffold (symptom → root cause → pinning test → spec patch → follow-ups).
- [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) — RED classification (GOOD red / BAD red / false-pass) — the semantics step 3 reuses.
- [`../implement/references/command-detection.md`](../implement/references/command-detection.md) — how the step-4 gate commands are resolved (settings override → Makefile → package scripts → language manifests).
- [`../_shared/ask-style.md`](../_shared/ask-style.md) · [`../_shared/agent-roster.md`](../_shared/agent-roster.md) · [`../_shared/handoff.md`](../_shared/handoff.md).

## Example invocation

> **User:** «/sdd:fix — discounts are applied twice when the user clicks pay twice fast»
> **Skill:** intake confirms: expected one discount per order, got two on a double-click (all users, since the checkout-discounts release). Trace: `docs/features/checkout-discounts/spec.md` AC-04 says «a discount is applied to an order at most once» → the code violates it → **regression**. `explorer` localizes the apply-discount handler (no idempotency check). RED: an integration test posting the same apply twice asserts one discount row — fails with `got 2, want 1` (GOOD red). GREEN: guard on the existing uniqueness key; gate clean. Spec: nothing to patch (AC-04 was right). Record `_fixes/2026-06-12-double-discount.md`; commit `fix: checkout-discounts double-applied discount` + `SDD-Fix:` / `SDD-AC: AC-04` trailers. Handoff: 2 files touched → no review push; resume.
