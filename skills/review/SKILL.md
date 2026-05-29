---
name: review
model: opus
effort: high
agents: [reviewer]
description: >
  Use to run an independent, clean-context code review of an implemented feature against its
  spec and acceptance criteria before shipping. Triggers on "review {slug}", "code review the
  changes for {slug}", "review the diff for {slug}", "is {slug} ready to ship", "/sdd-review {slug}",
  "переглянь зміни {slug}", "код-рев'ю фічі {slug}", "рев'ю diff". Dispatches the reviewer
  subagent over the whole feature diff (stage 1 spec/AC compliance, stage 2 quality), collects
  cited findings, and resolves each with you. Hard-refuses if the feature isn't implemented yet.
---

# Skill: review

The independent review gate. After `implement` has written + tested + committed the code, `review` looks at the **whole change at once, with fresh eyes** — does it actually satisfy every acceptance criterion, and is it good code? This is distinct from the per-task gate inside `implement` (which proves each task green): `review` is the cross-cutting, clean-context pass a human reviewer would do on the PR.

It reuses the shared clean-context discipline ([`../_shared/critic.md`](../_shared/critic.md)) and the [`reviewer`](../../agents/reviewer.md) subagent (read-only). Question phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md).

## Owner

Tech Lead / a reviewer who did **not** write the code (independence is the point).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** an implemented change must exist (commits on the feature branch, or a non-empty working diff). Nothing to review → «run `implement <slug>` first».
- Read for the review baseline — the **whole AC chain**, so the trace can be checked end-to-end: `docs/features/<slug>/spec.md` §5 (the full AC set — the source of truth, not the diff's trailers), `sad.md` §6 (the sequence flows/branches each AC should appear in), `data-model.md` / `contracts/openapi.yaml` / Accepted `adr/` (the contracts the code must honour), `test-plan.md` (the AC→test map, if a separate file), and `tasks.json` (which AC each task claimed).

## Protocol

1. **Scope the diff.** Determine the change under review: `git diff <base>..HEAD` on the feature branch (base = the branch point), or the named changed files. Note the `SDD-AC` trailers — the ACs the implementation claims to satisfy.
2. **Dispatch the independent reviewer.** Run the [`reviewer`](../../agents/reviewer.md) agent — `subagent_type: "sdd:reviewer"` (read-only, **clean context** — it re-reads spec/contracts itself, no paraphrase) — over the diff along the dimensions in [`./references/review-dimensions.md`](./references/review-dimensions.md): **stage 1** — every claimed AC genuinely satisfied **and the whole §5 AC set traced end-to-end (spec → sequences §6 → data-model → api → tasks → implement), flagging any AC that dropped out anywhere in the chain — not only the ACs the diff claims via its `SDD-AC` trailers**; **stage 2** — conventions, error/edge handling, security, boundary violations, test adequacy. For a large diff, fan out one reviewer per dimension and merge.
3. **Collect cited findings.** Each finding cites `file:line` + the AC/contract it touches. Drop uncited findings (per the critic discipline). A clean review returns `REVIEW_CLEAN`.
4. **Resolve each finding with the user** via `AskUserQuestion`: **Fix now** (hand the actionable finding back to `implement`/the author as a follow-up task — re-enter the TDD loop for it) / **Defer** (record in spec §8 Open questions with owner + due) / **Not an issue** (the reviewer misread; record why). Never ship an unresolved stage-1 (AC) finding.
5. **Write the review record.** `docs/features/<slug>/_review/review-<date>.md`: scope (diff stat), findings with verdicts, and the gate result (`PASS` / `CHANGES REQUESTED`).
6. **Verdict + next.** `PASS` → next is `ship <slug>`. `CHANGES REQUESTED` → loop back to `implement` for the fixes, then re-review the changed surface.

## Definition of Done

- The independent reviewer ran over the whole feature diff (not just per-task).
- Every claimed AC was checked for genuine satisfaction; **the whole §5 AC set was traced end-to-end (spec → sequences → data-model → api → tasks → implement)** and any AC that dropped out anywhere in the chain was flagged — not just the ACs the diff claims. Every in-scope AC is covered or explicitly deferred with owner + due.
- Every finding is resolved (fixed / deferred / dismissed-with-reason); no open stage-1 finding remains.
- A review record exists with a `PASS` / `CHANGES REQUESTED` verdict.

## Anti-patterns

- **Reviewing your own code in the same context that wrote it.** The reviewer must be clean-context and, ideally, not the author — that's what catches the blind spots.
- **Uncited findings.** «This feels off» is not actionable — cite `file:line` + the AC/contract or drop it.
- **Shipping with an open AC finding.** A stage-1 gap means the feature doesn't do what the spec says — fix or explicitly de-scope (spec change), never wave through.
- **Trusting the diff's `SDD-AC` trailers as the complete AC set.** The trailers only list what the diff *claims*. Review traces the **whole** §5 set end-to-end — an AC that never reached the diff (no task wrote it, no test asserts it) is the most dangerous gap precisely because the trailers can't reveal it.
- **Re-litigating style the repo already settled.** Judge against the conventions + contracts, not personal taste.
- **Treating the per-task gate as the review.** Green tests prove each task; they don't prove the change coheres or that the AC are truly met end-to-end.

## References

- [`./references/review-dimensions.md`](./references/review-dimensions.md) — the review dimensions + the reviewer dispatch shape.
- [`../_shared/critic.md`](../_shared/critic.md) — the clean-context dispatch discipline this reuses.
