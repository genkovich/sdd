---
name: interview
model: inherit
effort: high
agents: []
description: >
  Use BEFORE roadmap or specify to get the idea OUT OF YOUR HEAD and onto disk — a Socratic
  interview that surfaces hidden assumptions, names tradeoffs, exposes imprecisions and proposes
  fresh angles, then writes `docs/idea-brief.md` (8 sections) so the next stage has a source to
  read instead of guessing. Scope is any idea (product, content, business, architecture, refactor
  approach); outside a git repo it stays talk-only and writes nothing. Triggers on "interview
  {slug}", "idea brief", "write the brief", "stress test {slug}", "challenge this", "poke holes",
  "rip this apart", "/sdd:interview {slug}", "бриф ідеї", "погрилити", "розбери цю ідею",
  "розʼєби". Runs 3 phases (understand intent → surface tradeoffs and weak spots → propose new
  angles) via AskUserQuestion, ends with the brief on disk + the next step. Optional — reach for
  it whenever the idea itself isn't settled yet; `roadmap` needs its output.
---

# Skill: interview

Pressure-tests an idea **before** it becomes a roadmap or a spec, and writes down what came out.
The user shares a raw idea; across **3 phases** you surface hidden assumptions, name tradeoffs,
expose imprecisions and propose fresh angles — then the survivor lands in `docs/idea-brief.md`.

Two things are being produced at once, and the second is the one that matters downstream:
a **sharper idea in the user's head**, and the **context an agent cannot read anywhere else**.
The repo holds what the agent can discover on its own (`survey` maps it); this file holds what
only the person knows. `roadmap` hard-refuses without a source — this is that source.

**Scope: any idea.** Product, content, business, architecture, refactor approach — all in scope.
The boundary: this is an interview about the *idea*, not codebase archaeology. Ask the user to
articulate the idea in words first. Consult files only if the user explicitly invites it; default
is interview-first, no unprompted grep/find/read.

**Language.** Respond in the user's language; the instructions here are English for clarity. Brief
prose follows `artifact_language`, headings + frontmatter keys stay English →
[`../_shared/artifact-language.md`](../_shared/artifact-language.md).

The depth dial and the Socratic posture are SDD-wide:
→ [`../_shared/interview-depth.md`](../_shared/interview-depth.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

## Owner

The idea's author — whoever has the thing in their head (PM / lead / engineer / the solo maintainer).

## Inputs

- The raw idea, in the user's own words. Nothing else is required.
- (Optional) a `<slug>` — kebab-case, short. Not given → propose 2–3 and let the user pick.
- (Optional) prior notes / a ticket / links the user chooses to drop in.

## The write gate — where the brief lands (and when it doesn't)

Run `git rev-parse --show-toplevel` once, before the final summary:

- **Inside a git repo** → the brief is written to `<repo root>/docs/idea-brief.md` (protocol
  steps 6–8). This is the SDD case: the next stage reads it from disk.
- **Outside a repo** → write **nothing**. The final summary is the whole artifact, the self-check
  runs against the summary's own format (per [`../_shared/self-check.md`](../_shared/self-check.md)
  step 1), and there is no commit. A life / content / strategy idea in a scratch folder must not
  leave a file behind — that's the case this gate exists for.

An existing `docs/idea-brief.md` is **updated**, never silently rebuilt: read it first, and say in
the handoff which sections changed.

## Protocol

1. **Set the depth dial.** One `AskUserQuestion`, then commit (**default medium**). The dial is
   SDD-wide; interview's delta — the **3–4 / 6–10 / 10–15** question budget per level and each
   level's posture — is the canonical `interview` row in
   [`../_shared/interview-depth.md`](../_shared/interview-depth.md) (no table duplicated here).
   The adversarial triggers (grill / rip apart / розʼєби / погрилити) imply **hard** unless the
   user says otherwise. State the depth in one line, then start. Resolve the write gate above in
   the same breath (silently — one `git rev-parse`, no question about it).
2. **Phase 1 — understand the idea** (see [Phases](#phases)).
3. **Phase 2 — stress-test tradeoffs and imprecisions.** The core of the run.
4. **Phase 3 — propose new angles.**
5. **Final summary** in plain text (mini/full format below). This is what the user reads; §1–§8
   of the brief are filled from it, not the other way round.
6. **Write** — *repo only*. Fill [`./templates/idea-brief.md`](./templates/idea-brief.md) →
   `docs/idea-brief.md`; set `updated_at` (today) and `depth` (the level this run actually used).
   §1 Raw idea carries the user's own words verbatim — never the polished rewrite.
7. **Structural self-check** — *repo only*, per
   [`../_shared/self-check.md`](../_shared/self-check.md): re-read the file **from disk** and
   verify **5 items**: (1) all eight `## <n>. <Heading>` sections present verbatim and none empty;
   (2) zero template `<!-- instruction … -->` comments survived into the file; (3) zero tech tokens
   in the body — `\b(Postgres|PostgreSQL|MySQL|SQLite|Redis|Kafka|RabbitMQ|MongoDB|Elasticsearch|
   gRPC|GraphQL|JSONB|p95|p99)\b` (the `\b` boundaries matter — without them `chi` matches inside
   «architecture»); (4) the frontmatter carries **exactly** the template's four keys (`status` / `owner` /
   `updated_at` / `depth`) with none invented — `updated_at` = today, `depth` = the level
   used, `status: Draft`;
   (5) the file exists at `<repo root>/docs/idea-brief.md` (`test -f`). Fix + re-check ≤2 cycles;
   surface the rest. *Outside a repo* the summary checked against its mini/full format IS this
   skill's structural self-check — nothing on disk to re-read.
8. **Commit + handoff.** *Repo only:* propose commit `interview: idea brief for <slug>`. Then
   **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility
   variant — `/clear` optional), per «Hand off» below. Outside a repo: the handoff block still
   prints, with *Review* naming the summary instead of a path and no commit line.

## Phases

Use **1-3 questions per phase**, targeting the count from the depth dial. Move on from a phase
when answers repeat, the user says "next" / "хватить", or the latest answer added nothing.

### Phase 1 — Understand the idea
If the idea isn't stated in one sentence yet, ask for it in plain text (no AskUserQuestion).
Then unpack: who suffers without this · what success concretely looks like · whether it's new
or a refinement. Don't ask what's already obvious. → §1 Raw idea, §3 Users.

### Phase 2 — Stress-test tradeoffs and imprecisions
The core. Hunt **hidden assumptions** ("this assumes X — what if X is false?"), **tradeoffs**
(time vs quality, scope vs depth, reach vs focus), **imprecisions** (vague terms, ambiguous
metrics), **attention competition**, and **cost of failure**. Every question offers positions,
not yes/no. → §2 Problem, §4 Why now, §5 Out of scope, §6 Risks.

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
strongest bet, with reasoning in `description`. → §7 Recommendation, §8 Open questions.

## Hard rules

1. **Every question goes through AskUserQuestion**, not free text — 2-4 concrete options, the
   first marked `(Recommended)`, each option's `description` spelling out what follows from it.
   Free text slips into "I don't know" and loses signal. **On a host that has no native
   `AskUserQuestion`** (Codex CLI, Cursor) the same question is asked as **numbered plain text** —
   the same options with the same descriptions, one question at a time, then stop and wait for the
   answer. That is the documented host adapter, not the open-ended free text this rule forbids →
   [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md).
2. **One question at a time.** The user answers with full context on the previous answer, and
   you adapt the next question to it. Batching two or three questions per call is the SDLC
   toolkit's behaviour, not this one — it costs exactly the adaptation that makes the interview
   worth running.
3. **Recommendation is mandatory.** Always carry a position inside the Recommended option — a
   neutral interviewer surfaces less than one with a take the user can argue against.
4. **Don't skip phases.** No alternatives before intent is clear; no grilling tradeoffs before
   the idea is understood.
5. **Fabricating an answer voids the run.** Fabricating means answering *for* the user, from the
   model's own guesses — a brief filled that way is a reconstruction, not an interview, and every
   downstream stage inherits the fiction. A **missing native `AskUserQuestion` is not that case**:
   it's a host difference the adapter in rule 1 already covers, so ask in numbered plain text and
   carry on — never stop over it. STOP only when **nobody can answer**: a headless / `-p` run, a
   non-interactive session, or a denied tool call with no human left in the loop. Then say so
   plainly and write nothing.

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
{one concrete verb — usually "/sdd:roadmap" or "/sdd:specify <slug>"}
```

A full annotated medium-depth pass → [`references/annotated-pass.md`](references/annotated-pass.md).

## Definition of Done

- **In a repo:** `docs/idea-brief.md` exists with all eight sections filled, `updated_at` = today,
  `depth` = the level used, §1 in the user's own words, and no tech tokens in the body. The step-7
  **structural self-check** passed and its result is reported in the handoff.
- **Outside a repo:** the final summary matches its mini/full format; nothing written to disk.
- Either way: the depth dial was set, every question actually fired, and the handoff block named
  the next command.

## Hand off

**Emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility
variant — `/clear` optional):

- *What I did* — the revised idea + its weakest spot + «self-check: 5/5 pass» + the proposed commit.
- *Review* — `docs/idea-brief.md` (§2 Problem and §5 Out of scope are the two the next stage leans
  on hardest). Outside a repo: «nothing on disk — the summary above is the artifact».
- *Run next* — **`/sdd:roadmap`** when the brief covers a whole product that needs decomposing into
  steps (this is the file `roadmap` refuses to start without); **`/sdd:specify <slug>`** when the
  survivor is one buildable feature. Neither, when the idea wasn't an engineering one — resume
  whatever you were doing.

Never end on a bare «Next: …».

## Anti-patterns

- Asking "what exactly do you mean by X?" instead of offering 3 interpretations to pick between.
- Generic advice ("think about the user") instead of a specific take.
- Ending without a recommendation, or without naming the next step.
- Dragging past the depth-dial ceiling — at medium the target is 6-10, not a marathon.
- Reaching into the repo / running grep unprompted — the idea is articulated in words first.
- **Writing the brief from the model's summary instead of the user's answers.** §1 is verbatim;
  §2–§8 quote what was actually said, not what would read well.
- **Growing the brief into a spec.** Eight short sections. Acceptance criteria, user stories, NFRs
  and KPIs are `specify`'s job, and it runs its own ideation suite — a second copy here means two
  pipelines producing the same document twice.

## Edge cases

- **Idea already mature** — skip most of Phase 1, sometimes to 1 question.
- **User aborts with "ok summary"** — go straight to the final block with what's gathered.
- **Idea turned out weak mid-interview** — say so plainly, then propose the reframe.
- **Idea is for someone else** — re-route: "what would they say to question X?"
- **`docs/idea-brief.md` already exists** — read it, update the sections this run changed, keep
  the rest; the commit message says what moved.

### Stuck protocol
If the user picks **Other twice in a row** OR writes "I don't know" / "не знаю", switch to a
single open text question ("In your own words — what's bugging you most about this right now?").
Once they answer, resume AskUserQuestion with a new angle.

## References & template

- [`./templates/idea-brief.md`](./templates/idea-brief.md) — the 8-section brief scaffold.
- [`references/probing-frames.md`](references/probing-frames.md) — the 6 lenses with worked before/after questions.
- [`references/annotated-pass.md`](references/annotated-pass.md) — a full annotated medium-depth interview.
- [`../_shared/interview-depth.md`](../_shared/interview-depth.md) — the SDD-wide easy/medium/hard dial.
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — the AskUserQuestion option-writing contract.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — how each Claude Code mechanism maps to Codex CLI / Cursor (asking included).
- [`../_shared/artifact-language.md`](../_shared/artifact-language.md) — prose switches language, structure stays English.
- [`../_shared/self-check.md`](../_shared/self-check.md) — the structural self-check contract.
- [`../_shared/handoff.md`](../_shared/handoff.md) — the stage-handoff block format.
