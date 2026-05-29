# Socratic loop — canonical batch validation + 4-state machine + edits-log

> **Reference-only.** This file is not a skill — it has no `SKILL.md` and never triggers.
> Skills that run a Socratic validation pass (`specify`, `design`) read this file for the
> canonical machine and keep only a short **delta** of their own decision-types and section list.

## TL;DR (короткий вступ українською)

«Сократичний цикл» — діалог із користувачем по кожній **секції/групі** артефакту. Логіка:

1. Skill **малює всю секцію відразу** + нумерує рішення всередині (велика картина перед деталями).
2. Питає **по одному рішенню** через `AskUserQuestion` (формулювання → [ask-style.md](./ask-style.md)).
3. Користувач обирає одну з **4 дій**: **Прийняти** / **Виправити** / **Винести у відкрите питання** / **Викинути**.
4. Skill **застосовує перехід** у пам'яті, веде **edits-log**, і лише наприкінці секції пише на диск + комітить.
5. Внутрішні протиріччя між секціями ловить окремий clean-context критик ([critic.md](./critic.md)).

---

## Contract — batch-per-section, not per-decision-across-sections

For each section/group in order, the skill:

1. **Render the full proposed section** in one message — body text + a numbered list of the decisions it contains. The user sees the whole shape before any per-decision commitment (they catch duplicates / gaps / drop-the-whole-section problems early).
2. **Walk per-decision resolutions** — one `AskUserQuestion` per decision, using the 4-state machine below.
3. **Apply transitions** to the in-memory section as each resolution arrives.
4. **Run any per-skill gate** on Approved decisions (e.g. `design`'s blast-radius gate → ADR). Edit/Drop/Save-as-OQ do not trigger gates.
5. **Write the resolved section to disk** + any files the gate spawned + commit one bundled commit per section.
6. **Move to the next section.** The skill **never returns** to a written section — cross-section drift is the critic's job, not a re-walk.

On-disk artifacts are **not touched** until step 5. Everything before that is in-memory.

## The 4-state machine (uniform across every decision-type)

> **UA-перифраза.** 4 дії з кожним рішенням: **Прийняти** (Approve) / **Виправити** (Edit) /
> **Винести у відкрите питання** (Save as OQ) / **Викинути** (Drop). `Cancel` і `Reject` — синоніми Drop.

- **`Approve`** → keep the decision verbatim. No edits-log entry (Approved is the baseline). Run the per-skill gate if any. Move on.
- **`Edit`** → user supplies new wording / option / value in one go; skill regenerates the decision under the new constraint and asks **once more** (single-iteration cap — the second answer is final). Log entry `action: "edit"`.
- **`Save as Open Question`** → decision leaves its native section and a row is appended to the artifact's Open-Questions / Risks table:

  ```
  | Open decision: <headline> | Open question | Resolve before <stage trigger or YYYY-MM-DD>; <inline rationale> | <owner> |
  ```

  Owner + due (a date OR a stage trigger like «before `sdd:tasks`») are **mandatory** — issue a follow-up `AskUserQuestion` to capture both. If either is left blank, **downgrade to `Drop`** with an explicit warning. Log entry `action: "save_as_oq"`. **No gate** — a defer is not an accepted decision.
- **`Drop`** → decision is removed. Two sub-paths:
  - **Mandatory decision** (e.g. a module boundary that every feature must have) → re-ask **once** with a reframed option set. Second drop → escalate to `Save as Open Question` with a skill-suggested owner + due and a warning.
  - **Optional decision** → leave it out, no replacement.
  - Log entry `action: "drop"` (`after: null`).

Each option `label` is the **next mechanical step**; each `description` explains what the skill will do — see [ask-style.md](./ask-style.md).

## Edits-log (mandatory)

After each `Edit` / `Drop` / `Save as Open Question` (NOT `Approve`), append one entry:

```
{decision_id: "DEC-<section>-<short-id>",
 action:      "edit" | "drop" | "save_as_oq",
 before:      "<verbatim wording/option/value before the action>",
 after:       "<verbatim wording after — for save_as_oq this is the OQ-row text incl. owner+due; for drop, null>",
 user_reason: "<the rationale the user gave, verbatim>"}
```

`Approve` decisions stay out of the log — they are the baseline. The log is the **sole** signal the clean-context critic uses to detect upstream-coherence drift caused by user edits. Without it the critic has no input for its F-classes. If the user gives no reason on `Drop` / `Save as OQ`, re-prompt once — verbatim wording matters to the critic.

## Cadence

- A 1-line mini-recap of decisions so far every ~5 questions, so the user sees the dependency chain without scrolling.
- Keep a soft question budget per section sized to the feature class (see [size-matrix.md](./size-matrix.md)): XS/S lean on `<!-- N/A -->`, M+ walk every decision.
- **Question volume also scales with the interview-depth dial** ([interview-depth.md](./interview-depth.md)): `easy` decides the reversible calls itself and walks only the irreversible/high-stakes ones (stating its assumptions in a ledger), `medium` walks every real decision, `hard` walks every decision and foregrounds each trade-off. Depth and size compound — an XS feature at `easy` asks the least; an L feature at `hard` asks the most. Volume only: the disk-write discipline, the edits-log, and any coverage floor are unaffected by depth.

## Exit condition

A section is done when every decision in it has exactly one resolution applied, the resolved content + any gate-spawned files are on disk, and the edits-log has no pending entries. The whole pass is done when all sections are written and (for skills that run one) the critic phase has been dispatched — see [critic.md](./critic.md).

## Per-skill delta (what each consuming skill defines locally)

A consuming skill's `references/socratic.md` (or an inline ≤5-line block in `SKILL.md`) supplies only:

- **Section/group list** walked in order (e.g. `specify`: the 5 AC coverage types; `design`: Arc42 §1–§12).
- **Decision-types catalog** for this artifact (e.g. `design`: Strategic / Building-block / Crosscutting / Quality-scenario / Risk).
- **Per-skill gate** run on Approved decisions, if any (e.g. `design`: blast-radius → ADR).
- **Open-Questions table location** (which section absorbs `save_as_oq` rows).

Everything else — the 4-state machine, the edits-log schema, the cadence, the disk-write discipline — comes from this file.
