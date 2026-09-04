# Probing frames — worked examples

Six internal lenses for Phase 2. These are lenses for *you*, not labels for the
user — never announce "now I'll do a premortem". For each frame below: what it
catches, a **flat** question (what a neutral interviewer asks) and the **framed**
question (sharper, forces a position). Mix frames; don't iterate the list in order.

Every framed question still obeys the hard rules: it goes through AskUserQuestion
(or its host adapter — numbered plain text on Codex CLI / Cursor, see
[`../../_shared/tool-adapters.md`](../../_shared/tool-adapters.md)) with 2-4 concrete
options, the first marked `(Recommended)`.

---

## 1. Premortem — "it's six months later and this failed. Why?"

Catches the failure mode the user is avoiding looking at.

- **Flat:** "What are the risks?"
- **Framed:** "It's six months out and you quietly dropped this. Which is the most likely cause?"
  - *(Recommended)* You ran out of energy before it compounded — solo cadence is the real constraint
  - The audience never showed up — the demand wasn't there
  - It worked but wasn't worth the time it ate
- **Surfaces:** whether the threat is motivation, demand, or opportunity cost — three very different fixes.

## 2. Second-order — "it succeeds. What breaks next door?"

Catches the cost of winning that the user hasn't priced in.

- **Flat:** "What happens if it works?"
- **Framed:** "Say it takes off and doubles your inbound. What's the first thing that buckles?"
  - *(Recommended)* Your calendar — you can't service the demand you create
  - Quality — the bar you set in week 1 is unsustainable
  - Focus — it pulls you off the thing that actually pays
- **Surfaces:** success has a bill; naming it now changes the scale you should aim for.

## 3. Naive listener — "how does this sound to someone hearing it cold?"

Catches insider language and the unearned assumption.

- **Flat:** "Is the message clear?"
- **Framed:** "A sharp person outside your bubble hears the one-liner. What do they misread first?"
  - *(Recommended)* They think it's for beginners when you mean seniors
  - They can't tell what they'd *do* differently after consuming it
  - They assume it's a sales funnel and tune out
- **Surfaces:** the gap between what you mean and what lands — usually an audience or promise problem.

## 4. Inversion — "what if you did the exact opposite?"

Catches whether the chosen shape is a real choice or a default.

- **Flat:** "Is this the right format?"
- **Framed:** "Instead of long-and-thorough, what if it were short-and-frequent?"
  - *(Recommended)* Short-and-frequent — momentum matters more than depth here
  - Long-and-rare — depth is the whole differentiator, keep it
  - A mix — a short cadence with one deep piece a month
- **Surfaces:** the user defends or abandons their default — either way the choice becomes conscious.

## 5. Cost of waiting — "what changes if this slips a quarter?"

Catches false urgency and real urgency alike.

- **Flat:** "When do you want to launch?"
- **Framed:** "If you started this in three months instead of now, what's actually lost?"
  - *(Recommended)* Nothing structural — so de-risk first, start smaller
  - A window closes — a trend or audience moment you can't get back
  - Compounding — every month of delay is a month of audience you don't build
- **Surfaces:** whether "now" is a real constraint or anxiety wearing a deadline.

## 6. The other person — "what would they say if asked this?"

Catches the idea-for-someone-else where the user is answering on their behalf.

- **Flat:** "Will your team go for it?"
- **Framed:** "Your most skeptical teammate is in the room. Which objection do they raise first?"
  - *(Recommended)* "We tried this and it died" — there's prior history you're discounting
  - "Who owns it when you're out?" — the bus-factor question
  - "This competes with X we already do" — an overlap you haven't named
- **Surfaces:** objections the user is too close to see; re-routes the interview through the real decider.

---

## Picking a frame

- Idea is **vague** → naive listener (force a crisp one-liner) + inversion (is the shape chosen or defaulted).
- Idea is **ambitious** → premortem + second-order (price the failure and the success).
- Idea is **urgent** → cost of waiting (test the deadline).
- Idea is **for a team / someone else** → the other person (re-route through them).

When a lens produces a question you can't reduce to 2-4 concrete options, it's not
ready — pick a different lens rather than asking it open-ended.
