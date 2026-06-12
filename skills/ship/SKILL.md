---
name: ship
model: inherit
effort: medium
agents: []
description: >
  Use to close the loop after review — verify the feature actually works, write the changelog /
  knowledge-base note, and open the pull request. Triggers on "ship {slug}", "open a PR for {slug}",
  "changelog for {slug}", "prepare {slug} for merge", "/sdd:ship {slug}", "відправ фічу {slug}",
  "створи PR для {slug}", "changelog для {slug}". Re-runs the gate, runs the app/feature to confirm
  the spec's outcomes for real (not just green tests), drafts a changelog + PR body that link spec/
  AC/ADRs, and proposes the PR command for whatever forge the repo uses. Never auto-merges to main.
---

# Skill: ship

The closing step. `review` confirmed the change is correct on paper; `ship` confirms it **works in reality** and packages it for merge. The loop ends here: a reviewed, verified change with a changelog and an open PR — not a merge to main (that stays a human decision).

Forge-agnostic and stack-agnostic: the verification commands are detected the way `implement` detects them; the PR step targets whatever forge the remote points at (GitHub via `gh`, GitLab via `glab`, or copy-paste).

## Owner

The implementer (drives) + the reviewer who signed off in `review`.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** a `PASS` review record (`docs/features/<slug>/_review/`) or, at minimum, an implemented + gate-green change. No review yet → «run `review <slug>` first».
- Read: `spec.md` (what to claim in the changelog), Accepted `adr/` (decisions worth recording), the feature's commits (the `SDD-Task` history).

## Protocol

1. **Final verification — does it actually work.** Re-run the detected gate (unit + integration where available + lint + vet). Then **run the feature for real** against its acceptance criteria — not just "tests pass": start the app / hit the endpoint / exercise the flow and observe the spec's outcomes (e.g. the default-on read returns defaults; an invalid value is rejected). Concretely: **spot-check at least 3 of the most critical §5 AC outcomes** (fewer only if the spec has fewer; scale the count with the feature's breadth), and for each name the AC id + the behaviour actually observed — «AC-03: posted the same apply twice → one discount row» — so the verification is checkable, not a vibe. If the app can't be run here (no runtime, no Docker), say so explicitly and record what was verified vs deferred — never claim verified-working when only tests compiled.
2. **Write the changelog / KB note.** From [`./templates/changelog.md`](./templates/changelog.md): what changed, why (link spec + the key ADRs), any migration/operational note (e.g. "adds migration 000023 — run it on deploy"), and how to use it. Partner-facing if the change is partner-facing.
3. **Prepare the PR.** Ensure the work is on a feature branch (not the default branch). Draft the PR body from [`./templates/pr-body.md`](./templates/pr-body.md): summary, the AC it satisfies, links to spec/sad/ADRs, the `SDD-Task` commit list, the test + verification evidence, and any migration/rollback note.
4. **Detect the forge + propose the PR command.** Inspect the remote: `github.com` → `gh pr create`; `gitlab.com`/self-hosted GitLab → `glab mr create`; otherwise print the branch + body for manual creation. **Propose** the command — do not run a push/PR to a shared remote without the user's go-ahead, and never merge to main.
5. **Update the roadmap.** Move this feature's item to **Shipped** in `docs/roadmap.md` (via `roadmap`) — date + outcome + link to the feature folder + the PR/changelog — and remove it from **Now**. This is the anti-drift hook: delivery itself keeps the roadmap current. (No roadmap yet → skip; it's optional.)
6. **Summary (terminal handoff).** **Emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (terminal variant) — *What I did* (verification result: verified-working / what was deferred and why; the roadmap update) + *Review* (the changelog path + the PR) + *Run next* = **Done**: the PR command (or URL if the user ran it) — merging to main is your call; there is no `/sdd` successor.

## Definition of Done

- The gate was re-run and the feature was exercised against its AC (or the deferral was stated explicitly with the reason).
- A changelog / KB note exists, linking spec + ADRs.
- A PR body is prepared and the forge-appropriate PR command proposed (work on a feature branch; main untouched).

## Anti-patterns

- **"Tests pass" ≠ "it works".** Run the actual feature against the spec's outcomes; green unit tests don't prove the wired system behaves.
- **Claiming verified when you only compiled.** If the runtime/Docker wasn't available, say what was deferred — don't overstate.
- **Auto-merging to main / pushing to a shared remote unasked.** Propose the PR; the merge is the team's call.
- **A changelog that restates the diff.** Say what changed and why (link the spec + ADR), plus the operational note (migrations, flags) — not a file list.
- **Forgetting the migration/rollback note** when the change includes one — the deployer needs it.

## References & template

- [`./templates/changelog.md`](./templates/changelog.md) — changelog / KB-note scaffold.
- [`./templates/pr-body.md`](./templates/pr-body.md) — PR description scaffold.
