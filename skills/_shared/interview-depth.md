# Interview depth — easy / medium / hard (the depth dial)

> **Reference-only.** Not a skill. The Q&A skills (`specify`, `clarify`, `design`) read this for
> the canonical three levels and how each adapts. The dial tunes **how much the skill decides on
> its own vs. interrogates you** — question volume, autonomy, which analyses run, and whether each
> diagram is confirmed per-item or written-and-summarized. It does **not** tune *completeness*:
> every acceptance criterion is still covered at every level (see the coverage floor below).

## TL;DR (короткий вступ українською)

«Депт-діал» — один регулятор на запуск скіла: **easy / medium / hard**.

- **easy** — скіл сам ухвалює більшість рішень із розумними дефолтами, питає тільки незворотні / високоризикові, і **виписує припущення, які зробив**, щоб ти міг їх ветувати. Менше аналізу, діаграми пишуться + один підсумок (без поштучного питання).
- **medium** — поточний збалансований сократичний прохід (дефолт).
- **hard** — проходимо **кожне** рішення; кожне `AskUserQuestion` виводить trade-off на передній план; повний набір ідейних аналізів (research / approaches / perspectives / devil's-advocate); кожна діаграма підтверджується прозою; edge-cases копаємо глибше.

Повнота (покриття кожного AC) **не залежить** від рівня — easy теж покриває всі AC, просто менше питає *як саме*.

---

## How the level is chosen (every consuming skill, step 1)

A consuming skill resolves the level once, at the top of its run, in this precedence (highest wins):

1. **A `--depth=easy|medium|hard` argument** passed on the invocation, if present — silent, no question.
2. **The opening `AskUserQuestion`** — ONE depth-selection question, phrased per [`ask-style.md`](./ask-style.md) (explanatory + every term glossed). Its **default option** (the «(Recommended)» first option) is:
   - the `interview_depth` value from `.claude/sdd.local.md` if that file exists and sets it, else
   - **medium**.
   The user can always override per run — the saved default only pre-selects the recommendation; it never skips the question (unless `--depth=` was passed).

`interview_depth` is a **plugin-wide** setting (documented with the rest in [`../implement/references/settings.md`](../implement/references/settings.md)), not implement-only. A skill reads it if the file is present; if the file is absent it simply defaults the question to medium — there is **no hard dependency** on `implement` having run first, and the skill never creates the settings file just to read this key.

The opening question is also where the skill states what the level will *do* to this run («easy → I'll decide the reversible calls myself and list my assumptions; hard → I'll walk every decision and run the full analysis suite»), so the user picks with eyes open.

## What each level governs (the four axes)

| Axis | **easy** | **medium** (default) | **hard** |
|---|---|---|---|
| **Question volume + autonomy** | Skill decides the reversible / low-stakes calls itself with sensible defaults; asks ONLY the irreversible / high-blast-radius / genuinely-un-inferable ones. **States every assumption it made** (an assumptions ledger) so the user can veto. | The balanced Socratic walk — one `AskUserQuestion` per real decision, trivial convention-defaults bundled. | Walks **every** decision; each question **foregrounds the trade-off** (what you gain / lose / the hidden catch); probes edge cases harder. |
| **Ideation analyses** (`specify` step 3) | Skip the suite — deep-dive answers only. | `researcher` (competitive/web) + `devils-advocate`. | Full suite: `researcher` + `strategist` (3 approaches) + `analyst` (multi-perspective) + `devils-advocate`, then the Claude-proposed RICE/feasibility confirm. |
| **Diagram confirmation** (`design` C4, `sequences` flows) | Write the diagram + a **one-line prose summary**, then proceed — no per-diagram question (per [`diagram-presentation.md`](./diagram-presentation.md)). | Prose description + `AskUserQuestion` confirm **per diagram**. | Same as medium — prose description + confirm per diagram (never raw Mermaid). |
| **Edge-case / ambiguity probing** | Only the edges that change the blast radius. | The spec's stated error/authz/edge criteria. | Adversarial — hunt for unstated edges, run the full `devils-advocate` pass, push on every «what if». |

Read the axes together, not in isolation: **easy** is «trust the defaults, show me what you assumed»; **medium** is «walk the real decisions with me»; **hard** is «interrogate me, run everything, leave nothing un-probed». The dial scales *effort spent asking*, not *effort spent being correct*.

## The assumptions ledger (easy only)

At `easy`, every decision the skill made **for** the user (instead of asking) is recorded as a one-line ledger entry and surfaced together before the write-point:

```
- Assumed: <decision> = <chosen value>  — because <default rationale>.  [veto?]
```

The user gets ONE `AskUserQuestion` to veto/adjust the ledger as a batch (or accept all). An assumption the user vetoes becomes a real question (medium-style) for that one item. This is the easy-level safety net: autonomy without silent commitment — the user sees every default before it's locked, just not as N separate prompts. (At medium/hard there is no ledger — those levels asked the question directly.)

## The coverage floor is depth-independent (correctness, not a preference)

Depth tunes **how many questions** and **how much autonomy** — never **what gets covered**. The completeness guarantees hold at **every** level:

- Every spec §4 user story has ≥1 acceptance criterion; §5 keeps ≥1 AC of each of the 5 coverage types (`specify`).
- Every §5 AC maps to a flow, a branch, or an explicit N/A (`sequences` AC→flow coverage check).
- Every AC traces end-to-end spec → sequences → data-model → api → tasks → implement (`review`).

`easy` reaches these by **deciding** the «how» with defaults and listing them in the ledger; `hard` reaches them by **asking**. The destination is identical. A skill must never drop an AC, a coverage type, or a flow because the level is `easy` — that's a correctness bug, not a depth choice. If easy can't infer the «how» for a coverage-relevant decision, that decision is one of the «irreversible / un-inferable» ones it **must** ask about regardless of level.

## Per-skill adaptation (the delta each consuming skill applies)

- **`specify`** — the level gates step 3's ideation suite (table above) and the volume of the step-2 deep-dive + step-7 Socratic validation. The §5 coverage gate (≥1 of each of the 5 AC types) is **floor, not dial** — enforced at every level.
- **`clarify`** — the level gates how aggressively the self-sweep + `devils-advocate` hunt (easy: only build-divergence that changes behavior, with assumptions stated; hard: adversarial, every fork surfaced) and the per-finding question volume. Every surfaced ambiguity is still Resolved or Deferred at every level — none dangling.
- **`design`** — the level gates the per-section Socratic question volume (easy: decide convention-defaults itself + ledger, ask only blast-radius decisions; hard: walk every decision, foreground each trade-off) and the C4 diagram confirmation (per [`diagram-presentation.md`](./diagram-presentation.md)). The blast-radius → ADR gate and the §11 owner+due rule are floors, enforced at every level.

A consuming skill adds a one-line pointer to this file at its depth-selection step and otherwise reads the level as a parameter into its existing loop — it does not re-implement the dial.
