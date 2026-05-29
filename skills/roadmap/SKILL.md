---
name: roadmap
model: inherit
effort: medium
agents: []
description: >
  Use to keep the portfolio layer above individual features — one living docs/roadmap.md of
  outcomes, structured Now / Next / Later, that links to per-feature specs without duplicating
  them. Triggers on "roadmap", "what's next", "prioritize the roadmap", "add to the roadmap",
  "show the roadmap", "/sdd-roadmap", "роадмеп", "що далі", "пріоритети", "додай у roadmap".
  Captures a candidate as an outcome/problem (lands in Next/Later, RICE-scored), promotes/demotes
  between horizons, and renders the board. It is outcome-altitude — NOT a feature list or a
  dated Gantt; the solution lives in the feature's spec, not here. specify promotes an item to
  Now; ship moves it to Shipped — so delivery keeps the roadmap in sync.
---

# Skill: roadmap

The **portfolio layer** above the per-feature pipeline. SDD builds one feature at a time under `docs/features/<slug>/`; `roadmap` is the single living view *across* features — what we're doing now, what's next, what's directional later — kept at **outcome altitude** (the "why"/problem), with each item linking to its feature folder rather than restating the spec.

A roadmap is **direction, not a promise**, and **not a release plan**: feature-and-date roadmaps are the biggest source of waste — they project false certainty, go stale fastest the further out they reach, and commit to solutions before discovery. So this roadmap encodes *decreasing certainty over time* and never carries dates. Repo-level utility (like `survey`) — one file serves the whole repo. Question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md).

## Owner

Whoever owns product direction (PM / lead / the solo maintainer). They decide what's Now/Next/Later; the pipeline keeps statuses in sync.

## Inputs

- (Optional) a candidate to capture (an outcome/problem in one line), or an action: prioritize / promote / demote / render.
- `docs/features/*/` — to link items to existing feature folders and read their status.

## Protocol

1. **Lazy-create.** If `docs/roadmap.md` is absent, copy [`./templates/roadmap.md`](./templates/roadmap.md) there (the non-commitment disclaimer + the Now / Next / Later / Shipped sections). One file, repo root `docs/`.
2. **The three horizons — content type changes per horizon** (this is the load-bearing rule, not feature-everywhere):
   - **Now** — committed work whose `docs/features/<slug>/` spec exists and is being built. Item = outcome one-liner + link to the feature folder + a status (designing / implementing / review). Promoted here only after `specify` (it's spec'd + committed).
   - **Next** — problems/opportunities deliberately **NOT yet spec'd** — an outcome/problem one-liner + a RICE score, no feature folder yet. This is the prioritized candidate pool.
   - **Later** — outcomes/themes, directional only. No features, no scores.
3. **Capture a candidate** → add to **Next** (or Later) as an outcome/problem, RICE-scored. **Never** write a solution/feature spec here — that's `specify`'s job when the item is pulled into Now.
4. **Prioritize (RICE).** For Next candidates, score `RICE = (Reach × Impact × Confidence) ÷ Effort` (Impact 3/2/1/0.5/0.25; Confidence 100/80/50%; Effort in person-weeks) → one sortable number; order Next by it descending. RICE is a guide, not a gate — the owner can override. → [`./templates/roadmap.md`](./templates/roadmap.md) shows the columns.
5. **Promote / demote.** Move items between horizons as certainty changes. Promote Next→Now only when the item is about to be `specify`'d (committed). Demote freely; far-out items stay coarse.
6. **Render / write + commit + handoff.** Update `docs/roadmap.md`, set `updated_at`, propose commit `roadmap: <what changed>`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) — *What I did* + *Review* (`docs/roadmap.md`) + *Run next*: resume your backbone stage; `/clear` optional.

## Sync hooks (delivery keeps it current — anti-drift)

- **`specify`** registers its feature on the roadmap and promotes the item to **Now** (outcome one-liner + link to the new `docs/features/<slug>/` + status). A brand-new feature with no prior candidate is added directly to Now.
- **`ship`** moves the item to **Shipped** (date + link to the PR/changelog) and removes it from Now.

Because the pipeline stages themselves update the roadmap, it stays current without separate upkeep — the same mechanism GitHub's public roadmap uses (ship → mark shipped → close).

## Definition of Done

- `docs/roadmap.md` exists with the disclaimer + Now / Next / Later (+ Shipped), items at **outcome altitude**, each Now/Shipped item **linking** to its `docs/features/<slug>/` (no spec duplication).
- Next is RICE-ordered; no dates anywhere; no feature-level detail in Later.
- `updated_at` reflects the change.

## Anti-patterns

- **A feature-and-date roadmap / a Gantt.** Items are outcomes/problems; dates are absent; the solution lives in the spec. This is the cardinal sin the research names as the biggest source of waste.
- **Duplicating the spec** on the roadmap. Link to `docs/features/<slug>/`; the roadmap holds the *why*, not the *how*.
- **Over-detailing Later.** Far-out items are directional one-liners — detailing them is fiction that goes stale.
- **Roadmap-as-promise.** Keep the disclaimer; near-term is firm, far-term will change.
- **Promoting to Now before `specify`.** Now = committed + spec'd; un-spec'd work stays in Next.
- **Letting it rot.** The `specify`/`ship` hooks keep it live — don't bypass them with a stale hand-maintained list.

## References & template

- [`./templates/roadmap.md`](./templates/roadmap.md) — the living-roadmap scaffold (disclaimer + Now/Next/Later/Shipped + RICE columns).
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — phrasing for capture/prioritize questions.
