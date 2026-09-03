# Rubric — roadmap-same-zone-wave

Discount codes and gift cards are two increments that land on the same price computation
(`internal/checkout/pricing.go`) — the brief says so in §6 and the architecture map confirms the
module. The dependency graph alone permits them to run at the same time; the codebase does not.
This scenario catches the roadmap that puts both in one wave because nothing checked the zone.

PASS requires ALL of:

1. `docs/roadmap.md` exists with a `## Execution path` table whose rows name a **zone per step**.
2. The discount-code step and the gift-card step are **not in the same wave** — either because an
   edge orders them, or because the wave layout separates them on the zone. Both landing in one
   wave is an automatic FAIL, whatever the reasoning text says.
3. Every zone named in the execution-path table resolves to a path that exists in the fixture
   (`internal/checkout/`, `internal/notify/`) or is explicitly marked `(new)`.
4. The confirmation-email step, which touches `internal/notify/` only, IS allowed to share a wave
   with a checkout step — a roadmap that serialises everything to be safe has lost the point of
   the waves and fails this item.
5. Dependencies live **only** in the `## Dependency graph` mermaid block — the steps table has no
   `Depends on` column — and every edge names two step ids that exist in that table.
6. The `## Steps` table has a `Size` column with values from {XS, S, M, L, XL, fog} and **no
   `Clarity` column**.
7. `## Destination` exists and holds one sentence.
8. `## Open decisions` exists; the stacking question from §8 is present with a type and an owner,
   and the email-template question is typed `research` with owner `agent`.
9. The final message contains a stage-handoff block and reports the self-check as N/6.

FAIL on two same-zone steps in one wave, a zone naming a path that does not exist and is not
marked `(new)`, a steps table that still carries `Depends on` or `Clarity`, a graph edge naming a
step id that is not in the table, or any date outside `## Shipped`.
