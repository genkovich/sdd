---
name: interview
model: inherit
effort: high
agents: []
description: >
  Use BEFORE specify to stress-test a raw idea — pressure-test it before you commit to a
  spec. A Socratic interview that surfaces hidden assumptions, names tradeoffs, exposes
  imprecisions, and proposes fresh angles. Scope is any idea (product, content, business,
  architecture, refactor approach), but in an SDD repo the natural exit is /sdd:specify on
  the surviving idea. Triggers on "interview {slug}", "stress test {slug}", "challenge this",
  "poke holes", "rip this apart", "/sdd:interview {slug}", "погрилити", "розбери цю ідею",
  "розʼєби". Runs 3 phases (understand intent → surface tradeoffs and weak spots → propose
  new angles) via AskUserQuestion, ends with a summary of risks, alternatives, and the next
  step. Optional — the backbone starts at specify; reach for interview when the idea itself
  isn't settled yet.
---

# Skill: interview

Pressure-tests an idea **before** it becomes a spec. The user shares a raw idea; across **3
phases** you surface hidden assumptions, name tradeoffs, expose imprecisions, and propose
fresh angles — then hand the survivor to `specify`. This is the optional pre-backbone step:
it makes `specify` cheaper by killing or reshaping a weak idea before any spec gets written.

**Scope: any idea.** Product, content, business, architecture, refactor approach — all in
scope. The boundary: this is an interview about the *idea*, not codebase archaeology. Ask the
user to articulate the idea in words first. Consult files only if the user explicitly invites
it; default is interview-first, no unprompted grep/find/read.

**Language.** Respond in the user's language; the instructions here are English for clarity.

The depth dial and the Socratic posture are SDD-wide:
→ [`../_shared/interview-depth.md`](../_shared/interview-depth.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

## Depth dial — set this first

One `AskUserQuestion`, then commit (**default medium**). The dial is SDD-wide; interview's
delta — the **3–4 / 6–10 / 10–15** question budget per level and each level's posture — is the
canonical `interview` row in [`../_shared/interview-depth.md`](../_shared/interview-depth.md)
(no table duplicated here).

The adversarial triggers (grill / rip apart / розʼєби / погрилити) imply **hard** unless the
user says otherwise. State the depth in one line, then start.

## Hard rules

1. **Every question goes through AskUserQuestion**, not free text — 2-4 concrete options, the
   first marked `(Recommended)`, each option's `description` spelling out what follows from it.
   Free text slips into "I don't know" and loses signal.
2. **One question at a time.** The user answers with full context on the previous answer, and
   you adapt the next question to it.
3. **Recommendation is mandatory.** Always carry a position inside the Recommended option — a
   neutral interviewer surfaces less than one with a take the user can argue against.
4. **Don't skip phases.** No alternatives before intent is clear; no grilling tradeoffs before
   the idea is understood.

## Phases

Use **1-3 questions per phase**, targeting the count from the depth dial. Move on from a phase
when answers repeat, the user says "next" / "хватить", or the latest answer added nothing.

### Phase 1 — Understand the idea
If the idea isn't stated in one sentence yet, ask for it in plain text (no AskUserQuestion).
Then unpack: who suffers without this · what success concretely looks like · whether it's new
or a refinement. Don't ask what's already obvious.

### Phase 2 — Stress-test tradeoffs and imprecisions
The core. Hunt **hidden assumptions** ("this assumes X — what if X is false?"), **tradeoffs**
(time vs quality, scope vs depth, reach vs focus), **imprecisions** (vague terms, ambiguous
metrics), **attention competition**, and **cost of failure**. Every question offers positions,
not yes/no.

**Probing frames** — internal lenses (premortem · second-order · naive listener · inversion ·
cost of waiting · the other person). Pick what fits, mix them, don't name the frame to the
user. Worked before/after examples per lens → [`references/probing-frames.md`](references/probing-frames.md).

**Intensity dial.** Default tone is Socratic; the adversarial triggers escalate phrasing
("Why do you think X is even true?"). The user dials back with "ease up" / "помʼякши".

**Drill vs move on.** Drill the same dimension when an answer surfaced a new assumption; move
on once the position is clear and the tradeoff named.

### Phase 3 — Propose new angles
Now actively propose via AskUserQuestion: 2-3 alternative shapes (different audience, format,
scale) or a twist (inversion, constraint, simplification). The Recommended option is your
strongest bet, with reasoning in `description`.

## Final summary (plain text, not AskUserQuestion)

≤4 questions → **mini**; ≥5 → **full**.

**Mini:** Revised idea (one sentence) · Weakest spot (one sentence) · Next action (one verb).

**Full:**
```md
## Revised idea
{one paragraph — the idea after the interview}

## What surfaced
- **Hidden assumptions**: …
- **Main tradeoff**: …
- **Weakest spot**: …

## Alternative angles
1. {strongest} 2. {second} 3. {the one they wouldn't have reached alone}

## Next step
{one concrete verb — usually "/sdd:specify <slug>" once the idea survives}
```

A full annotated medium-depth pass → [`references/annotated-pass.md`](references/annotated-pass.md).

## Hand off

interview writes **no files** — it sharpens the idea in the user's head, so the final summary
checked against its mini/full format is this skill's **structural self-check**
([`../_shared/self-check.md`](../_shared/self-check.md)) — nothing on disk to re-read. After the
summary, **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
(utility variant — `/clear` optional): *What I did* (the revised idea + its weakest spot) + *Review*
(nothing on disk — the summary above is the artifact) + *Run next*: when the idea is a feature
you intend to build, `/sdd:specify <slug>` turns the survivor into a spec; otherwise resume
whatever you were doing. Never end on a bare «Next: …».

## Anti-patterns

- Asking "what exactly do you mean by X?" instead of offering 3 interpretations to pick between.
- Generic advice ("think about the user") instead of a specific take.
- Ending without a recommendation, or without naming the next step.
- Dragging past the depth-dial ceiling — at medium the target is 6-10, not a marathon.
- Reaching into the repo / running grep unprompted — the idea is articulated in words first.

## Edge cases

- **Idea already mature** — skip most of Phase 1, sometimes to 1 question.
- **User aborts with "ok summary"** — go straight to the final block with what's gathered.
- **Idea turned out weak mid-interview** — say so plainly, then propose the reframe.
- **Idea is for someone else** — re-route: "what would they say to question X?"

### Stuck protocol
If the user picks **Other twice in a row** OR writes "I don't know" / "не знаю", switch to a
single open text question ("In your own words — what's bugging you most about this right now?").
Once they answer, resume AskUserQuestion with a new angle.

## References

- [`references/probing-frames.md`](references/probing-frames.md) — the 6 lenses with worked before/after questions.
- [`references/annotated-pass.md`](references/annotated-pass.md) — a full annotated medium-depth interview.
- [`../_shared/interview-depth.md`](../_shared/interview-depth.md) — the SDD-wide easy/medium/hard dial.
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — the AskUserQuestion option-writing contract.
- [`../_shared/handoff.md`](../_shared/handoff.md) — the stage-handoff block format.
