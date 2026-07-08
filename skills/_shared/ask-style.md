# Ask-style — junior-friendly `AskUserQuestion`

> **Reference-only.** Not a skill. Every skill that calls `AskUserQuestion` reads this for the
> canonical shape of questions and options. The rule: an **option label is the next mechanical
> step the skill takes**, not just a name; the **description explains, in plain words, what will
> happen** — written so a first-year junior can pick correctly without a senior beside them.

> **Volume vs. style.** How **many** questions a Q&A skill asks scales with the interview-depth dial
> (easy asks few, hard asks all — see [`interview-depth.md`](./interview-depth.md)). The **per-question
> explanatory rule below is unchanged at every depth** — even a single easy-level question is glossed
> and explained in full. Depth tunes the count; it never licenses a dry question.

## The one rule that matters most

**Never ask dryly.** The most common failure is a terse, jargon-dense question — a few words plus acronyms, no context — that forces the user to already know the project to answer. Fix it two ways, every time:

1. **Gloss every technical term inline, on first use** — the plain meaning in parentheses, right there. Not "order by RICE" but "order by RICE — a quick score, Reach × Impact × Confidence ÷ Effort, where higher = more value per unit of work". Not "forces a worktree" but "forces a worktree — a separate working copy of the repo so two agents don't edit the same files". The reader should never have to look a term up to choose.
2. **Spend the words on the WHY and the trade-off**, not the WHAT. A short label is fine; the *description* is where you explain — in plain language — what happens, what you gain and lose, and the hidden catch.

If a question reads like a config dump or a spec excerpt, it's wrong. Write it as if explaining the choice to a capable colleague who just joined and doesn't know your acronyms yet. **More explanation always beats less here** — a long, clear description is a feature, not bloat.

## Shape

- **`question`** — 3–4 sentences in three blocks:
  - **CONTEXT** — why this decision, what scenario to picture, what exactly we're deciding (one sentence with a concrete example).
  - **WHY IT MATTERS** — which quality goal / NFR / spec vector it touches; reversibility (irreversible? multi-module? affects performance / security / UX?); the main trade-off in play.
  - **READ OPTIONS** — a nudge to read the descriptions before choosing.
- **Each option**:
  - `label` — 1–5 words, **action form** = the next mechanical step: "Approve", "Edit", "Save as Open Question", "Drop", "Lock as ADR". Add "(Recommended)" to the first option when you recommend it.
  - `description` — 3–5 sentences with four mandatory elements (below).

## The four mandatory elements of a `description`

1. **What technically happens** — concrete names: tables / endpoints / files / ADR numbers. Not "modify the API" but "add field `is_active BOOLEAN` to table `members` and a new route in the module's handler".
2. **What you gain / what you lose** — the trade-off in plain words, **every technical term glossed**:
   - not "backfill migration" → "a script that walks every existing row and fills the new field; while it runs the rows are read-locked for writes"
   - not "cursor pagination" → "the client sends the last id it saw so the next page starts after it; avoids `OFFSET`, which slows down on large pages"
   - not "GIN index" → "a special index type that lets you search inside JSON columns, but takes 3–5× more space and writes slower"
3. **The skill's next mechanical step** — "I spawn ADR-NNNN titled X, add a row to the §9 ADR table, the schema is locked for the data-model stage".
4. **Hidden trade-off** — if there's a condition under which the choice breaks ("only works if Redis is already in your stack", "in 6 months you'll need downtime for a backfill", "existing users have to re-login"), state it **right in the description**, not in a follow-up. A junior won't see that trigger on their own.

## Language

- **Conversation language is a per-project switch** — `conversation_language` in `.claude/sdd.local.md`
  (default `en`, any language tag). It governs the **question + option text** (labels + descriptions)
  shown in `AskUserQuestion`. Write both in the configured language so the whole prompt reads natural
  to the user; default `en` keeps everything English.
- **Technical identifiers stay in their original form** (ADR, JSONB, JWT, UUID, FK, OpenAPI) regardless
  of language — they are names, not words. The *actions* are the localized part (e.g. under `en`:
  "Approve" / "Edit" / "Save as §11 OQ" / "Drop").
- Glossary roles and domain-invariant **names** (natural-language phrases like "no published lessons")
  are allowed — they are business terms.
- This section governs **conversation** (question + option text) only. The language documents are
  *written in* is a separate per-project switch — `artifact_language` in `.claude/sdd.local.md` →
  [`artifact-language.md`](./artifact-language.md). The two are independent: you can ask in one
  language and write artifacts in another.

## Forbidden

- Terse labels ("Approve", "Edit", "Drop", "Reword" with no explanatory description behind them).
- One-line descriptions.
- Technical terms without a gloss (UNION, backfill, GIN, cursor, idempotent, transactional…).
- Trade-offs hidden in a follow-up ("if you pick this I'll later ask about X, which has complexity Y").

## Counter-example (deprecated) vs correct

```
# DON'T — opaque next step, no gloss
- label: "Approve"
  description: "Apply decision."

# DO — action-form label, description names the concrete step + glossed trade-off
- label: "Approve JSONB column (→ spawn ADR-0002)"
  description: "A single `body` column of type jsonb stores the whole array of blocks as JSON. PROS: editing a lesson is one UPDATE; a new block type needs no schema migration. CONS: block validation moves to the app layer (the DB doesn't know the types); searching inside body needs a GIN index (a special Postgres index type for searching in JSON — 3–5× more space, slower writes). RESULT: I spawn ADR-0002 with 3 considered options, add a §9 row, and the schema is locked for the data-model stage."
```

## The 4-state actions, phrased this way (canonical set)

```
- label: "Approve as is"
  description: "I keep the decision verbatim and run the next check (the gate, if there is one for this section)."
- label: "Edit"
  description: "You give new wording/value; I regenerate the decision under the new constraint and ask once more (one round — the second answer is final)."
- label: "Save as Open Question"
  description: "I remove the decision from the section and add a row to the Open-Questions table with owner+due (asked next). Without both, the decision becomes a Drop."
- label: "Drop"
  description: "I remove the decision. If it's mandatory — I reframe the options and ask again; if it's optional — I leave it out with no replacement."
```

## Dry → explanatory (worked rewrite)

```
# TOO DRY (jargon-dense, no context — the failure to avoid):
Question: "Prioritize Next by RICE or manual?"
Options:
  - label: "RICE"
    description: "RICE score, ordered desc."
  - label: "Manual"
    description: "Manual order."

# EXPLANATORY (context + why + glossed terms — do this):
Question:
  "How should we decide the ORDER of the not-yet-started ideas in the roadmap's «Next» list?
   This only affects which problem we pick up next — nothing is committed yet, and you can always
   reorder. The trade-off: a scoring formula is more objective but takes a minute per idea; eyeballing
   it is faster but drifts with mood. Read both options below."
Options:
  - label: "Score each idea (Recommended)"
    description: "I rate every Next idea with RICE — a quick score = Reach (how many users it touches) ×
      Impact (how much it moves the needle, 3 down to 0.25) × Confidence (how sure we are, as a %) ÷
      Effort (rough person-weeks). It gives one sortable number per idea, so «Next» orders itself by
      value-per-effort. You can still override any ranking by hand. Costs ~a minute of estimating per idea."
  - label: "Just order them by hand"
    description: "No formula — you (or I) drag the ideas into the order that feels right; row position =
      priority. Faster and fine for a short list, but with many ideas it gets subjective and the order
      tends to drift over time. You can switch to scoring later if the list grows."
```

The dry version is unanswerable without knowing what RICE is; the explanatory version teaches the term in the act of asking and makes the trade-off obvious.

## Why (feedback)

The user is a PM, methodist, or junior dev opening the repo for the first time. Terse questions give them neither the substance of the decision nor the difference between options. The recurring feedback: make the explanations more understandable for people who are literally juniors in development, and make interview questions more explanatory — the earlier prompts were too dry and packed too many terms into a short text. That's why this file leads with the "never ask dryly / gloss every term" rule above.
