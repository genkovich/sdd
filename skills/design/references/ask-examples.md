# design-specific `AskUserQuestion` shapes

The canonical question/option contract — junior-friendly, label = next mechanical step, description = 3–5 sentences with the four mandatory elements — lives in [`../../_shared/ask-style.md`](../../_shared/ask-style.md). Read that first (it also defines the `conversation_language` switch — the examples below are written in the default `en`). This file keeps only the **design-specific shapes** that aren't in the shared file: the strategic-decision-with-ADR-spawn, the blast-radius gate, and the Save-as-OQ follow-up. Examples are stack-agnostic — substitute your repo's real names.

## Strategic decision (§4) — option labels name the ADR spawn

```
Question:
  §4 Solution Strategy — how do the two modules talk to each other?
  CONTEXT: module A writes a record, module B must react to it (e.g. send a notification).
  We're deciding whether B is called inline or reacts to an event later.
  WHY IT MATTERS: this is irreversible (changing it after data accumulates is a multi-week
  migration) and multi-module (it changes the contract both A and B see) — blast-radius ≈ 3/3,
  so this will spawn an ADR. The trade-off is coupling vs added moving parts.
  Read the option descriptions before choosing.

Options:
  - label: "Async events (Recommended) (→ spawn ADR-0001)"
    description: "A writes its record and emits an event; B consumes it in the background. PROS: B can be down without blocking A's writes — supports the availability quality goal; the modules deploy independently. CONS: needs an event-delivery mechanism (a table A writes events into within the same transaction, plus a worker that reads and dispatches them — ~150 LOC) and eventual-consistency handling. RESULT: I spawn ADR-0001 in decision-form, add a §9 row, and the integration shape is locked for the `data-model` stage. HIDDEN: only worth it if you actually need the decoupling — for a single in-process call it's over-engineering."
  - label: "Synchronous call (→ spawn ADR-0001)"
    description: "A calls B directly and waits for the result. PROS: simplest to reason about, no extra infrastructure, strong read-after-write. CONS: A's write fails whenever B is down — couples their availability; couples their deploy lifecycles. RESULT: I spawn ADR-0001 with this as the chosen option and the alternatives recorded, add a §9 row. HIDDEN: fine until B becomes slow or flaky, then A inherits B's incidents."
  - label: "Save as Open Question"
    description: "I remove this decision from §4 and add a §11 Risks row «Open architectural decision: module integration — Open question — Resolve before `data-model` — owner: <you>». I ask you for owner + due next. Without both it becomes Drop. No ADR — a defer is not an accepted decision."
  - label: "Drop and reframe"
    description: "I discard this option set and ask again with a reframed set (e.g. only the synchronous variants if you ruled out async). Use this when the set is missing a dimension you care about. This decision is mandatory, so a second drop escalates to Save-as-OQ with a suggested owner."
```

## Blast-radius gate (after an Approve, on a 1-of-3 borderline)

When the gate scores **2+**, spawn the ADR without asking. Only on a **1-of-3 borderline** do you ask:

```
Question:
  Blast-radius check after you approved «<chosen option>».
  CONTEXT: this scored 1 of 3 — it has legitimate alternatives but is reversible and stays
  inside one module. We're deciding whether it still deserves its own ADR file.
  WHY IT MATTERS: ADRs are for decisions worth re-reading in six months; over-ADR-ing dilutes
  the genre, under-ADR-ing loses the «why». Read the options.

Options:
  - label: "Lock as ADR"
    description: "I create adr/NNNN-<decision-in-kebab>.md from the options you saw (including the rejected ones) + your rationale, Status Accepted, and add a §9 row. The file ships in this section's commit (or its batch on quick+easy). Pick this if the choice felt genuinely contestable."
  - label: "Keep inline"
    description: "I write the decision into the section body with a one-line rationale, no ADR file. Pick this when the choice is small-blast-radius despite having alternatives — typical for §8 crosscutting or a §5 internal-layout call."
```

## Save-as-OQ follow-up (capture owner + due)

Fired immediately after any section resolves to Save-as-OQ:

```
Question:
  The decision is migrating to §11 Open Decisions. Provide an owner and a due — a date
  (YYYY-MM-DD) or a stage trigger like «before `tasks`». Both are mandatory; without both
  this becomes a Drop and leaves nothing in §11.

Options:
  - label: "Provide owner + due"
    description: "You type «owner: <name/role>, due: <date or stage>» in one line; I write it into the §11 row (severity = Open question) so the deferred decision stays recoverable until that trigger."
  - label: "Cancel — Drop instead"
    description: "I abandon the OQ migration and apply Drop — the decision is removed from its section and no §11 row is created. The edits-log records it as a drop."
```
