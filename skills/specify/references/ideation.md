# Ideation orchestration — specify step 3 (depth-gated named subagents)

For a feature that's a real bet, the deep-dive answers aren't enough to commit to an approach. This pass grounds the committed approach in **§1 ¶3** of the spec. It is **read-only research + named subagents + user confirms** — nothing is written until the spec is. Everything stays at **product level**: no concrete datastore / broker / framework / library names (those are `design` decisions); every subagent is told the same.

What runs is governed by the **interview-depth dial** ([`../../_shared/interview-depth.md`](../../_shared/interview-depth.md)), with feature **size** as a secondary trimmer. The analyses that used to run inline are now **named-subagent dispatches** — each with a clean, isolated context (the value is fresh eyes), spawned with `subagent_type: "sdd:<name>"` per [`../../_shared/agent-roster.md`](../../_shared/agent-roster.md) §Dispatching, with a `general-purpose` fallback if the namespaced agent isn't available.

## When each agent runs (depth × size)

| Depth | What runs |
|---|---|
| **easy** | **Skip the suite.** No subagents — the step-2 deep-dive answers are enough. §1 ¶3 still names a committed approach, but Claude picks it from the deep-dive and records it as an **assumption in the easy ledger** (per the depth dial) for the user to veto — no research, no 3-approach fan-out. |
| **medium** (default) | `researcher` (competitive / web) **+** `devils-advocate` (failure modes). No strategist/analyst/RICE — a lighter grounding. |
| **hard** | **Full suite:** `researcher` **+** `strategist` (3 approaches) **+** `analyst` (multi-perspective over those approaches) **+** `devils-advocate`, then the Claude-proposed **RICE + feasibility** confirm. |

**Size is the secondary signal**, never the primary gate: the user's chosen depth wins, and size only *trims volume* within it — an XS/S feature at hard still runs the suite, but the `researcher` table may legitimately be one `N/A — internal tool` row and the RICE pass stays terse. (Pre-1.7 this pass was gated by size alone — "M/L/XL only". Depth is now the gate; size is the trimmer.)

## The dispatches

The dispatching prompt is the **only channel** to a clean-context agent (per the shared agent contract). For every agent below, the prompt inlines: the **captured idea (verbatim baseline)** + the **step-2 deep-dive answers** + (if it exists) the **`CONTEXT.md` path** for canonical terms. The spec is not written yet — there is no `spec.md` to read, so the material is inlined.

1. **`researcher`** (`sdd:researcher`) — *medium + hard.* Competitive + adjacent-solution research with web access. Returns a cited table (Product · URL · Features · Value 1–5 · Gap), each row footnoted with date + query, plus a one-line synthesis of the biggest gap. **Fallback:** a `general-purpose` Agent given the same prompt and `WebSearch`/`WebFetch`. **If web access is unavailable** in this run, accept its `RESEARCH_LIMITED` output and carry the gap as a noted gap (like the `mmdc` fallback elsewhere) — never invent competitors to fill the table.
2. **`strategist`** (`sdd:strategist`) — *hard only.* Generates the three strategic approaches — A Simplicity / B Differentiation / C Balanced — each with Name · Thesis · For-whom · Outcome-metric · Key-trade-off · Effort-signal. Dispatch it **together with `researcher`** in one message (they're independent).
3. **`analyst`** (`sdd:analyst`) — *hard only.* Multi-perspective review (Engineer / Executive / UX lenses) **of `strategist`'s three approaches** → a 3×3 synthesis matrix (+/0/−, ≤6-word justifications) + one synthesis line per approach. Dispatch it **after** `strategist` returns (it needs the three approaches inlined). The Engineer lens stays abstract — no product/library names.
4. **`devils-advocate`** (`sdd:devils-advocate`) — *medium + hard.* Run it in its **failure-mode mode** (not the clarify ambiguity mode): the prompt asks «there is no spec yet — here is the idea (+ approaches, at hard); find how this fails — 5–10 attack vectors with production signals: what breaks, how it shows up in monitoring / churn / an incident». Returns the cited vectors. It runs in parallel with the others (at hard, pass it the approaches so it attacks the leading one). **Fallback:** `general-purpose` with the same prompt.

> Ordering at hard: dispatch `researcher` + `strategist` + `devils-advocate` in one message; once `strategist` returns, dispatch `analyst` over its three approaches. At medium: dispatch `researcher` + `devils-advocate` together.

## RICE + feasibility (hard only — Claude-proposed, `AskUserQuestion` confirm)

These stay **inline** (computed from the upstream signals + confirmed with the user — not a subagent):

5. **Claude-proposed RICE.** Compute from upstream: Reach ← user segments; Impact ← problem severity + `analyst`'s Executive lens; Confidence ← inverse of unresolved TBDs; Effort ← the approaches' effort signal. Compute `R × I × C / E`. Confirm each number with the user (`Confirm` / `Adjust up` / `Adjust down` / `Mark TBD`) — never make the user invent the numbers (the «calculator game» anti-pattern). Phrase per [`../../_shared/ask-style.md`](../../_shared/ask-style.md).
6. **Feasibility (read-only repo scan + confirm).** Scan the repo for adjacent shipped features. Propose three checkboxes — Tech / Skills / Time — each justified by a cited adjacent feature. Confirm each (`Confirm ☑` / `Flip to ☐ — reason` / `TBD`).

## Recommendation → §1 ¶3

Claude picks one approach and writes a 3–5 sentence rationale, then confirms it with the user (`Accept` / `Pick different` / `Mark TBD`). The accepted approach becomes **§1 ¶3** of the spec. What the rationale must cite depends on what ran:

- **hard** — cite all four upstream signals: the RICE score, the feasibility state, ≥1 `analyst` synthesis-matrix cell, and ≥1 `researcher` competitive gap.
- **medium** — cite the `researcher` gap + `devils-advocate`'s sharpest vector + the deep-dive's success criterion (no RICE/matrix exist to cite). Still a real, confirmed recommendation — just lighter.
- **easy** — §1 ¶3 states the approach Claude inferred from the deep-dive, surfaced in the assumptions ledger; the user's veto/accept on the ledger *is* the confirm.

## How the outputs feed the spec

- **`researcher` gap** → cited in the §1 ¶3 recommendation; a competitor's deliberate omission may seed a §3 Non-goal.
- **`strategist` approaches** → the option set the recommendation chooses from (and the runners-up seed §8 if the user wants them tracked).
- **`analyst` matrix** → cited in §1 ¶3; a consistently `−` lens flags a §6 NFR or §11 risk to watch.
- **`devils-advocate` vectors** → the sharpest one is reserved for §6.1 Security/privacy + abuse cases (or §11 Risks); the rest seed §8 Open questions.
- **RICE / feasibility** → cited in §1 ¶3; the RICE score also feeds the roadmap's Next-ordering when `specify` registers the feature.

## Discipline

- **Depth is the gate.** easy skips the suite (ledger-an-assumption instead); medium = research + adversary; hard = the full SLDC-style pass. The dial is what keeps easy/medium light after the agent re-expansion.
- **Three approaches, not one** (at hard depth). One approach means the decision is already taken — nothing to evaluate. **All three perspectives** (at hard depth) — Engineer-only is blind to business/UX; Executive-only is blind to cost.
- **The adversary runs from clean context** — otherwise it inherits the upstream optimism.
- **Product-level only** — no concrete stack in any analysis or in §1 ¶3. Tech belongs to `design`.
- **Never invent** competitors or RICE numbers to fill the pass — better an honest `N/A — internal tool` row or a `Mark TBD` than fabricated research.
- **Planning-mode-friendly:** the whole pass is read-only. If the skill started in plan mode, keep everything in session memory and let the spec write happen after `ExitPlanMode`.
