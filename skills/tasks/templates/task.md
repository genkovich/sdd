---
id: T1
title: "<imperative, specific title>"
layer: "migration|domain|infra|app|ports|ui|tests|wiring|docs"
deps: []                # task ids that must finish first
blocks: []              # task ids waiting on this one — the inverse of `deps` (markdown only)
acs: ["AC-01"]          # spec §5 acceptance criteria this task satisfies
files_hint: ["path/or/dir/the/task/touches"]
owner: "<owner / TBD lead>"
estimate: "S"           # S/M/L or hours — how long the work takes
context_budget: "S"     # what the task costs the executing agent to hold (markdown only).
                        # Measured, not guessed: the non-empty lines from `## Why (user story)`
                        # through `## Acceptance criteria`.
                        # S = ≤40 inlined lines, ≤1 extra file to open
                        # M = ≤120 inlined lines, 2–4 files in play
                        # L = beyond that — split the task, or keep it and say why right here:
                        #     context_budget: "L"   # justified: <one line>
status: "todo"
---

<!-- The governing rule of this file: **inline the slice the task actually needs, name where it came
from, and keep the link as the fallback for when the slice turns out not to be enough.** A task is
self-contained: it carries its own context instead of sending the executing agent off to reconstruct it.

Every inlined chunk ends with a one-line **provenance signature**:
`<file> §<section>, <identifier>, verbatim|abridged` — e.g. `spec.md §5, AC-02, verbatim`,
`data-model.md §Entities, table order, abridged`. Never «see the spec».

**Inline budget.** Exactly what THIS task needs: only its own acceptance criteria, only the
data-model fields and endpoints it touches. Cut a long chunk to the essential, mark it `abridged`,
and link the full text. `context_budget` in the frontmatter carries the measured number, and an `L`
either gets split or gets its `# justified:` reason on that line — the `tasks` skill checks both.

**Divergence risk.** An inline is a snapshot taken at breakdown time; upstream can move after it.
The source always wins — which is exactly why every chunk carries a signature pointing at where the
truth lives.

**To the executing agent:** work from what is inlined here. If a slice is insufficient, ambiguous,
or contradicts the code in front of you, open the named file for the full text and follow that.
Do not invent the missing part. -->

# T1 — <title>

## Place in the sequence

<!-- instruction: 2–4 lines. What must finish first (`deps`, by id + title), what is waiting on this
one (`blocks`, by id + title), and why it sits in this wave. Name the lane it shares if any — an
overlapping `files_hint` with another task, or a compile-coupled pair — so the executing agent knows
it is serialized rather than parallel. -->

- **Blocked by:** <T0 — title> · **Blocks:** <T4 — title, T5 — title> · **Wave:** <n, and why>.
- **Lane:** <shares `path/x` with T3 — serialized>, or «own lane».

## Why (user story)

<!-- instruction: the user story from spec §4 **verbatim** in its As a / I want / So that form, then
one sentence on what THIS task contributes to it. Signature under the quote. -->

> **As a** <role>
> **I want** <action>
> **So that** <observable benefit>
>
> — `spec.md §4, US-01, verbatim` · full text: [spec.md](../spec.md)

<one sentence: the part of that story this task delivers>

## Inlined context

<!-- instruction: the upstream slices the task actually needs, each as a quote + signature. Draw from:
spec §1 committed approach · spec §6 NFR and sad §11 Hard Rules the task must not violate ·
sad §5 the building block it lives in (its boundary + collaborators) · sad §6 the runtime steps it
implements · the decision line of any Accepted ADR that constrains it · `screens.md` SCR-NN + the
states, for `ui` tasks. Cut to the essential, mark `abridged`, keep the link. This section replaces
the old list of links — it is never empty. -->

> <the quoted slice, cut to what this task needs>
>
> — `sad.md §6, «<flow name>» steps 3–5, abridged` · full text: [sad.md](../sad.md)

> **Hard rule:** <the constraint, verbatim>
>
> — `sad.md §11, RISK-02, verbatim` · full text: [sad.md](../sad.md)

**Fallback:** insufficient or contradicted by the code → read the named file in full
([spec.md](../spec.md) · [sad.md](../sad.md) · [data-model.md](../data-model.md) ·
[openapi.yaml](../contracts/openapi.yaml) · [adr/](../adr/)) and follow it. Do not guess.

## Data delta

<!-- instruction: only the schema this task touches — the entity/columns/constraints/indexes, as a
slice of the data-model table, with the signature. A migration task also names its **staged** pair
`docs/features/<slug>/migrations/<NN>_*.up.sql` / `*.down.sql` (which `implement` promotes into the
live `migrations/`). A task that changes nothing in the DB writes the sentence explicitly — an empty
section is a defect, «No DB changes.» is an answer. -->

| Column | Type | Constraints | Change |
|---|---|---|---|
| `<col>` | `<type>` | `<NOT NULL / FK / UNIQUE>` | added / altered / read-only |

— `data-model.md §Entities, table <entity>, abridged` · full text: [data-model.md](../data-model.md)

<!-- or, when the task touches no schema, the whole section is this one line: -->
No DB changes.

## API contract

<!-- instruction: only the endpoints/schemas this task touches — method + path, the request and
response fields it reads or writes, the error codes it must return, sliced out of
`contracts/openapi.yaml` with the signature. A task with no external surface writes the sentence
explicitly. -->

- `POST /<path>` → `201` `<SchemaName>` · errors: `400 <code>`, `409 <code>`.
- Request fields this task handles: `<field>`, `<field>`.

— `contracts/openapi.yaml, operationId <op>, abridged` · full text: [openapi.yaml](../contracts/openapi.yaml)

<!-- or, when the task exposes nothing, the whole section is this one line: -->
Internal — no API surface.

## Acceptance criteria

<!-- instruction: one block per id in the `acs` frontmatter, Given-When-Then **verbatim** from
spec §5, each carrying its AC id and signature. These are what the test asserts — never paraphrase
them here. -->

### AC-01 — <coverage type>

> **Given** <preconditions>
> **When** <action>
> **Then** <observable outcome>
>
> — `spec.md §5, AC-01, verbatim` · full text: [spec.md](../spec.md)

## Checklist

<!-- instruction: atomic, ordered steps for the executing agent — the concrete change, scoped to
≤1 day / one reviewable PR. Each step names the file or dir it touches (consistent with
`files_hint`). Migration task: write the staged up + down pair. Ports task: handler + its dto +
errors. Keep it within one layer where possible. -->

- [ ] <step — `path/to/file`>
- [ ] <step — `path/to/file`>

## Edge cases

<!-- instruction: the cases the happy path does not cover, drawn from the §5 ACs and the sad §6
error branches. Behaviour is observable, not «handle gracefully». -->

| Case | Behaviour |
|---|---|
| <empty input> | <the specified outcome> |
| <concurrent write> | <the specified outcome> |

## Definition of Done

<!-- instruction: testable bullets, then the gate. e.g.: -->
- [ ] <unit/integration test for this task passes>
- [ ] <staged migration is promoted to live `migrations/`, then applies and reverts cleanly> (migration tasks)
- [ ] <handler returns the spec'd outcome for AC-01> (ports tasks)
- [ ] every Hard Rule inlined above still holds
- [ ] lint + vet clean
