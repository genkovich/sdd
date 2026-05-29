---
status: living
updated_at: "<YYYY-MM-DD>"
---

# Roadmap — <repo>

> **Direction, not a promise.** Near-term work is firm; the further out an item is, the more
> directional and likely-to-change it is. This is **not** a release plan and carries **no dates** —
> it's the set of outcomes we're pursuing, at decreasing certainty over time. The *solution* for any
> item lives in its `docs/features/<slug>/` spec, not here.

## Now — committed · spec'd · in progress

<!-- instruction: features whose docs/features/<slug>/ spec exists and is being built. One ROW each:
the OUTCOME (the why), a link to the feature folder, and a status (designing / implementing / review).
No spec detail — link, don't duplicate. specify promotes an item here; ship moves it to Shipped. -->

| Outcome (the why) | Feature | Status |
|---|---|---|
| <outcome — the problem this solves> | [<slug>](./features/<slug>/) | implementing |

## Next — problems / opportunities (deliberately not yet spec'd)

<!-- instruction: the prioritized candidate pool. Each row is an OUTCOME/PROBLEM, not a solution, and
has NO feature folder yet (it gets one when pulled into Now via specify). Ordered by RICE desc.
RICE = (Reach × Impact × Confidence) ÷ Effort — Impact 3/2/1/0.5/0.25, Confidence 100/80/50%, Effort person-weeks. -->

| Outcome / problem | RICE | R · I · C · E |
|---|---|---|
| <problem statement> | <score> | <reach> · <impact> · <conf%> · <effort wk> |

## Later — outcomes / themes (directional)

<!-- instruction: coarse, directional one-liners only — one ROW each. No features, no scores, no dates. -->

| Outcome / theme (directional) |
|---|
| <outcome or theme we expect to pursue, eventually> |

## Shipped

<!-- instruction: ship moves delivered items here — one ROW each: date + outcome + link to the feature
+ the PR/changelog. Keeps Now honest and records what landed. -->

| Date | Outcome | Feature | PR |
|---|---|---|---|
| <YYYY-MM-DD> | <outcome> | [<slug>](./features/<slug>/) | [PR](<url>) |
