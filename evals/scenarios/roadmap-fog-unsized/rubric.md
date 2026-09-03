# Rubric — roadmap-fog-unsized

The fixture's brief says three times over that the legacy billing runner's deploy-log format has
never been read (§6 risk, §7 recommendation, §8 open question). That is fog: the question can be
stated precisely, but nobody has looked, so nothing about the work's shape is known. The failure
this scenario exists to catch is the roadmap sizing it anyway — a one-line row, `L`, one edge,
with nine undecided things underneath it.

The fixture also carries **no `docs/architecture-map.md`**. That is not a blocker: the map sharpens
the zone column and nothing else, so a run that stops for a missing map has failed a second way.

PASS requires ALL of:

1. `docs/roadmap.md` exists and its `## Steps` table carries a `Size` column whose every value is
   one of {XS, S, M, L, XL, fog}. There is **no `Clarity` column** — clarity and size share the one
   cell now, so a separate column is a stale-template failure.
2. The legacy-billing / second-data-source work has `fog` in its **`Size`** cell — and no
   XS/S/M/L/XL anywhere on that row.
3. A `## Not yet specified` section exists and names that area together with what would have to be
   learned to sharpen it. It is **one** area — not pre-chopped into several invented sub-steps.
4. The steps covering the four already-structured services each carry a size from {XS, S, M, L, XL}.
5. `## Out of scope` exists and carries at least the deploy-approval / rollback exclusion from §5.
6. `## Open decisions` exists and every row has a type from {research, prototype, grilling, task}
   AND an owner from {agent, human}.
7. Every step row carries a source anchor naming a section of `idea-brief.md`.
8. `## Destination` exists and holds **one sentence** — not a bulleted list, not a paragraph of
   goals.
9. The run produced the file despite the missing architecture map, and every zone in
   `## Execution path` that is not an existing path is marked `(new)`.
10. The final message contains a stage-handoff block and reports the self-check as N/6.

FAIL if the legacy-log work carries a size, if the steps table still has a `Clarity` column, if the
run stopped because `docs/architecture-map.md` was missing, if the legacy-log work was silently
dropped instead of parked in `Not yet specified`, if `Not yet specified` was pre-chopped into
ticket-sized rows, or if any date outside `## Shipped` appears in the file.
