<!-- Template for `plan-tests`. -->
<!-- M+: write to docs/features/<slug>/test-plan.md (this whole file). -->
<!-- XS/S: paste only the "## AC coverage" + "## Edge cases / error paths" blocks inline into -->
<!--       spec.md under a `## Test plan` heading — no frontmatter, no separate file. -->
<!-- The plan is written BEFORE tests exist; `implement` reads the AC→test map and writes the -->
<!-- red tests against it. Stay STACK-AGNOSTIC: name test LEVELS, never a runner / broker / -->
<!-- load tool. The real commands are detected by `implement` against the repo, not fixed here. -->

---
status: Draft
owner: "<QA owner>"
reviewers: ["<implementing engineer>", "<Tech Lead>"]
updated_at: "<YYYY-MM-DD>"
feature_size: "<XS|S|M|L|XL>"
---

# Test plan — <feature>

<!-- One-line restatement of what this feature must do, so the coverage below has a frame. -->

## Levels

<!-- The only allowed levels — generic, no tool names. Drop a row that doesn't apply to this -->
<!-- feature; mark it <!-- N/A: reason -->  rather than padding it. `implement` picks the actual -->
<!-- runner/tool for each level from what the repo already uses. -->
<!-- The Component / Visual-regression / E2E-through-UI rows apply ONLY when sad.md frontmatter -->
<!-- target_surfaces declares a UI surface (web-frontend / mobile-app / desktop-app) — the -->
<!-- "testing trophy" vocabulary (_shared/surfaces.md). Drop them for a backend-only feature. -->

| Level | Scope | Strategy (generic — no tool names) |
|---|---|---|
| Unit | Pure logic: a rule, a calculation, a validator — no I/O. | In-memory, no external dependency. |
| Integration | The module against a real dependency it owns (store / cache / queue). | An ephemeral real dependency, e.g. a throwaway DB container spun up per suite. |
| Contract | A boundary between two participants — an API shape or event schema both sides agree on. | Validate the real shape against the agreed contract; no hand-rolled stubs. |
| E2E | One full flow end to end (one per critical user story). | The flow exercised through its real entry point against ephemeral dependencies. |
| Load | NFR validation — only when an NFR carries a number. | The load tool already in your repo, or e.g. k6 or Locust. |
| Component *(UI surface only)* | A UI component exercised in isolation — props/state → rendered output + interactions. | Render in a component harness; assert output + behaviour, no full app boot. |
| Visual-regression *(web UI only)* | The rendered UI diffed against an approved baseline image. | Snapshot the render; fail on an unintended visual diff; update the baseline deliberately. |
| E2E-through-UI *(UI surface only)* | A user-story flow driven through the real UI, not just the API. | The flow exercised through the rendered UI against ephemeral dependencies. |

## AC coverage

<!-- THE CORE OF THIS PLAN: every acceptance criterion in spec.md §5 → at least one test row. -->
<!-- One AC may fan out to several rows (a unit test for the rule + an e2e test for the flow). -->
<!-- Zero uncovered ACs allowed. Name the test from the AC's intent, not a framework convention. -->
<!-- Expected outcome in plain words — NO status numbers, NO error-code strings, NO SQL. -->

| AC (spec.md §5) | Test name (intent-based) | Level | Expected outcome |
|---|---|---|---|
| AC-01 <happy path> | <e.g. request within limit is served> | unit + e2e | <served normally> |
| AC-02 <error path> | <e.g. request over limit is rejected> | unit + e2e | <rejected, caller told the limit was hit> |
| AC-03 <authorization> | <e.g. caller without rights is refused> | integration | <refused, action not performed> |
| AC-04 <domain invariant> | <e.g. invariant holds after the operation> | integration | <invariant still true> |

## Edge cases / error paths

<!-- Each error / authorization AC gets its OWN dedicated row — never folded into a happy path. -->
<!-- Add the boundary & failure cases the spec implies. Outcome named in plain words. -->

- <missing required identifier> → expected: <named outcome>
- <malformed input> → expected: <named outcome>
- <dependency unavailable> → expected: <the spec's fallback behaviour, e.g. fail-open / fail-closed>

## Test data

<!-- How test data is built and torn down. Seed = factories/fixtures for the entity shape -->
<!-- (read data-model.md if present). Cleanup boundary matters: no cleanup → flaky suite → CI block. -->

- Seed strategy: <factories / fixtures matching data-model.md entities>.
- Integration dependency: an ephemeral real dependency (throwaway container), NOT a mocked store.
- Cleanup boundary: <per-test | per-suite> — reset state so runs are independent.

## NFR validation (load)

<!-- One scenario per NUMERIC NFR from spec.md §6. If no NFR carries a number → N/A, do NOT invent one. -->
<!-- Tool stays generic: the load tool already in your repo, or e.g. k6 / Locust. -->

- <NFR: p95 latency ≤ N ms> → scenario: <target rate> for <duration>, assert <metric> ≤ <threshold>.
- <NFR: throughput ≥ N req/s> → scenario: sustain <rate> for <duration>, assert no error-rate regression.

<!-- If spec.md §6 has no numeric NFR: -->
<!-- N/A: no numeric NFR to load-test. -->

## CI placement

<!-- Advice, not pipeline config — `implement` and the repo's CI own the real wiring. -->

- On every PR: <unit, contract — the fast suites>.
- On schedule / pre-release: <e2e, load — the heavier suites>.
