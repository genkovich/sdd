---
name: sequences
model: inherit
effort: medium
agents: []
description: >
  Use to add Mermaid sequenceDiagram blocks to the SAD's runtime view (sad.md §6) — one per
  critical flow, showing how a request moves between participants with happy + error paths.
  Triggers on "sequences for {slug}", "sequence diagram for {slug}", "draw the runtime flow",
  "add a sequence to the SAD", "/sdd-sequences {slug}", "діаграми послідовності {slug}",
  "sequence для {slug}", "намалюй потік {slug}". Reads sad.md §5 for participants, drafts each
  flow from templates/sequence.md with generic participants, walks them Socratically one flow at
  a time, and writes confirmed blocks into sad.md §6 — they inform data-model indexes downstream.
  Hard-refuse if sad.md is missing → run `design {slug}` first.
---

# Skill: sequences

Draws the **runtime view** of an already-designed feature: for each critical flow it produces a Mermaid `sequenceDiagram` block — generic participants, happy path plus the error branches the spec demands — and writes them into `docs/features/<slug>/sad.md §6`. One flow at a time, user confirms each. The diagrams are the bridge between the static design (§5 building blocks) and the data layer: every persist/read step you draw becomes a hint for the indexes `data-model` will need.

This skill keeps only its own machinery. Question phrasing is **shared** → [`../_shared/ask-style.md`](../_shared/ask-style.md). Depth (one flow vs all critical flows) follows the **size matrix** → [`../_shared/size-matrix.md`](../_shared/size-matrix.md).

## Owner

Tech Lead (drives the runtime decomposition). The PM confirms that each drawn flow matches a real user story; a backend engineer flags persist steps that imply a new index.

## Inputs

- `<slug>` — same feature slug used by every earlier stage.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/sad.md`. The §5 building-block view names the participants; §6 is where flows are written. If `sad.md` is absent → STOP and point: «run `design <slug>` first — sequences are written into its §6».
- (Optional) `docs/features/<slug>/spec.md` — §4 user stories tell you *which* flows are critical; §5 acceptance criteria tell you *which error branches* each flow must show.
- (Optional) `docs/features/<slug>/.size` — depth hint. Absent → default to M (draw all critical flows).

## Protocol

1. **Gate.** `test -f docs/features/<slug>/sad.md` → fail = refuse with the pointer above. Then read §5 (participants) and §6 (any flows already drawn — this skill is additive, never rewrite an existing block).
2. **Pick the flows.** From `spec.md` §4 (or, absent it, from §6 itself), list the critical flows. Per the size matrix: **XS/S → 1 flow** (the single happy path that defines the feature); **M+ → all critical flows (3–5)**. Confirm the list with one `AskUserQuestion` before drawing anything — phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md).
3. **Map participants — generic only.** For each flow, draw participants from a fixed generic vocabulary: `<client>`, `<service>`, `<data-store>`, `<external-system>`, `<message-bus>`. Do **not** invent concrete service or technology names — those are `design`/`data-model` decisions, not runtime-view ones. If a flow needs a participant §5 never declared, note it («flow needs `<message-bus>`, not in §5 — flag for design») and still draw it.
4. **Sync vs async.** If the spec describes a webhook, scheduled job, queued/event-driven step, or any third-party callback → async: add an idempotency-key check as the handler's first step, a retry note (`Note over <service>,<external-system>: retry N times with backoff`), and a dead-letter branch in an `alt` after N failures. Otherwise → sync (request → response).
5. **Draft each flow** from [`./templates/sequence.md`](./templates/sequence.md): a precondition note, the happy-path messages, an `alt`/`else` for the error branches the spec's acceptance criteria require, and a postcondition note. Mark every write as a generic persist note — `Note over <service>,<data-store>: persists <entity>` — so `data-model` sees what to index. Keep messages verb-first and free of HTTP verbs / status numbers / SQL.
6. **Socratic walk, one flow at a time.** Show a rendered block, then ask the user to confirm it with the 4-state actions from [`../_shared/ask-style.md`](../_shared/ask-style.md) (Accept / Fix / Save-as-OQ / Drop). On Fix, take the user's note and regenerate that one flow (one round, second answer is final). Maintain a short edits-log. Never touch a flow already present in §6.
7. **Write into §6, validate, propose commit.** Insert each confirmed block under a `### <flow name>` heading, ordered to match §4. **Validate every `sequenceDiagram` block per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint — balanced `alt`/`else`/`end`, declared participants; fix any that don't parse before committing). Append any flagged items (new participants, decisions worth an ADR) as a short note at the end of §6 — flag only, never auto-write an ADR. Propose commit `sequences: <slug> runtime flows`. Next: `data-model <slug>` (uses the persist notes to choose indexes).

## Definition of Done

- `sad.md §6` holds a Mermaid `sequenceDiagram` for every critical flow at the chosen depth (1 for XS/S, all 3–5 for M+).
- Every block uses **only** generic participants (`<client>` / `<service>` / `<data-store>` / `<external-system>` / `<message-bus>`) — no concrete technology or service names.
- Each flow shows the error branches its spec acceptance criteria require, not happy-path only; every mutating step carries a generic persist note for `data-model`.
- Every async flow has an idempotency-key step, a retry note, and a dead-letter branch.
- Pre-existing §6 blocks are untouched; new participants / ADR-worthy decisions are flagged, not silently added.

## Anti-patterns

- **Concrete participants.** `Postgres`, `content-api`, a specific broker — the legacy trap. Participants stay generic; naming the tech is the job of `design`/`data-model`.
- **Happy path only** when the spec lists explicit error acceptance criteria. Each flow gets happy + the demanded error branches.
- **One mega-diagram** for the whole feature. Split per flow; a cross-cutting flow gets its own `### Cross-cutting: <name>` heading.
- **Auto-writing ADRs.** This skill only flags decisions (idempotency strategy, retry shape, sync-vs-async); ADRs come from `decide-adr` or a human.
- **Rewriting an existing §6 block.** Additive only — editing a drawn flow is a deliberate manual diff.
- **Inventing a participant §5 never declared without flagging it.** §5 is the source of truth; the flag lets `design` reconcile it.

## References & template

- [`../_shared/ask-style.md`](../_shared/ask-style.md) — canonical question/option phrasing for steps 2 and 6.
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — MVP (1 flow) vs Full (all critical) depth.
- [`./templates/sequence.md`](./templates/sequence.md) — generic-participant `sequenceDiagram` scaffold (sync + async), embedded inline in sad.md §6.
