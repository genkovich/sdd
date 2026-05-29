---
name: specify
model: opus
effort: high
agents: [critic, researcher, strategist, analyst, devils-advocate]
description: >
  Use to turn a raw feature idea into a reviewed spec.md — a lightweight Socratic interview
  front (capture the idea, deep-dive the problem) merged with a full product spec (context,
  goals, user stories, acceptance criteria, NFRs, KPIs). Triggers on "specify {slug}",
  "spec for {slug}", "write the spec", "capture this idea", "draft requirements for {slug}",
  "/sdd:specify {slug}", "напиши специфікацію {slug}", "опиши вимоги", "зафіксуй ідею".
  Opens by setting the interview-depth dial (easy/medium/hard), drafts from templates/spec.md,
  validates each acceptance criterion Socratically, runs a clean-context critic, then writes
  docs/features/{slug}/spec.md. The ideation analyses (competitive research, strategic approaches,
  multi-perspective review, devil's-advocate) run as named subagents gated by the depth dial —
  easy skips them, hard runs the full suite.
---

# Skill: specify

Turns a one-line idea into a reviewed `spec.md`: a lightweight interview captures and stress-tests the idea, then the skill drafts a product spec (context → goals → user stories → acceptance criteria → NFRs → KPIs), validates it Socratically, and runs a clean-context critic before writing. Less typing, more reviewing. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the size matrix are **shared** — this skill keeps only its deltas:
→ [`../_shared/socratic-loop.md`](../_shared/socratic-loop.md) · [`../_shared/critic.md`](../_shared/critic.md) · [`../_shared/size-matrix.md`](../_shared/size-matrix.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

Depth governs question volume + autonomy (and which ideation analyses run) → [`../_shared/interview-depth.md`](../_shared/interview-depth.md).

## Owner

PM + Tech Lead (co-authors). PM drives goals / non-goals / KPIs; Tech Lead drives context patterns and the acceptance-criteria coverage.

## Inputs

- `<slug>` — kebab-case feature slug.
- (Optional) `docs/features/<slug>/CONTEXT.md` — glossary; if present, its roles/terms are canonical and override anything that contradicts them.
- `docs/features/<slug>/.size` — depth hint (MVP vs Full per the size matrix). **Read if present; established here if absent** (step 1 classifies + writes it), so downstream stages never silently default to M. `classify-size` re-classifies when scope changes.
- (Optional) prior notes / a reference module / a ticket the user already has.

## Protocol

1. **Read context + set interview depth.** If `CONTEXT.md` exists, load its `## Glossary` as session state (canonical roles + terms). If `.size` exists, read it to size the spec's depth; **if it's absent, establish it now** — classify the feature via the 4 signals in [`../_shared/size-matrix.md`](../_shared/size-matrix.md) (PR count / time-to-merge / new module·API·migration / breaking changes), confirm in one bundled `AskUserQuestion` (at `easy` depth, take the matrix default and record it in the assumptions ledger), and write `docs/features/<slug>/.size` — so every later stage reads a real size instead of silently defaulting to M (the gap that otherwise surfaces only at `plan-tests`). `classify-size` stays the utility to re-classify when scope changes. If `docs/architecture-map.md` exists (from `survey`), read it so the spec is **architecture-aware** — it informs §1 Context, §2 Constraints, and §3 Non-goals (what the existing system already does / can't do). Absent → suggest running `survey` first, but proceed (the spec is product-level and can be captured without it). **Do not leak the map's tech into §5 AC** — AC stay business-observable; the map shapes constraints, not acceptance criteria. **Then set the interview depth (the opening question):** **if `.claude/sdd.local.md` is absent, auto-create it** with the documented default frontmatter (every key + its allowed values explained inline) and patch `.gitignore` → [`../implement/references/settings.md`](../implement/references/settings.md); then read `interview_depth` from it (else default medium), and — unless a `--depth=easy|medium|hard` arg was passed (which skips the question) — ask ONE depth-selection `AskUserQuestion` phrased per [`../_shared/ask-style.md`](../_shared/ask-style.md), with the saved/medium value as the «(Recommended)» first option, overridable per run. The chosen level governs the step-2 deep-dive volume, the step-3 ideation suite, and the step-7 Socratic volume → [`../_shared/interview-depth.md`](../_shared/interview-depth.md). (Completeness — §5's 5-type AC floor — is unaffected by depth.)
2. **Capture the idea (interview front).** One `AskUserQuestion` for the raw idea in 1–3 sentences (persist verbatim as the baseline). Then a Socratic deep-dive across problem clarity / success criteria / constraints / strategic fit, delivered in batches of 2–3 — its volume scales with the depth dial (easy: only the few un-inferable ones, then a stated-assumptions ledger; medium: 3–5; hard: walk every angle, foreground each trade-off). Phrase every question per [`../_shared/ask-style.md`](../_shared/ask-style.md).
3. **Ideation suite (depth-gated, named subagents).** Run the ideation analyses as named-subagent dispatches gated by the **interview-depth dial** (size as a secondary trimmer) → [`./references/ideation.md`](./references/ideation.md): **easy** → skip the suite (deep-dive only; the chosen approach is recorded as a ledger assumption); **medium** → `researcher` (`sdd:researcher`, competitive/web) + `devils-advocate` (`sdd:devils-advocate`, failure-mode mode); **hard** → full suite `researcher` + `strategist` (`sdd:strategist`, 3 approaches) + `analyst` (`sdd:analyst`, multi-perspective) + `devils-advocate`, then the Claude-proposed RICE/feasibility confirm. Analyses stay **product-level** (no tech names — that's `design`); the confirmed recommendation becomes §1 ¶3. Dispatch with `subagent_type: "sdd:<name>"` per [`../_shared/agent-roster.md`](../_shared/agent-roster.md) (`general-purpose` fallback); `researcher` needs web — accept its `RESEARCH_LIMITED` output as a noted gap if web is unavailable.
4. **Reconcile the glossary in-flow (a hard rule, at every depth).** On every new or unknown domain term that surfaces in the interview or the draft, invoke `glossary <slug>` for it **immediately** — compare it against `CONTEXT.md` and add/update the definition before continuing. By the time the spec is written, every §4 role and §5 domain term is already glossary-canonical; the glossary is never a deferred batch. (Plan-mode nuance: still decide add/update per term in-flow; if writes are blocked until the spec write-point, persist the reconciled terms together with the spec, but never skip the per-term compare.)
5. **Ask which extra channels to read** (multi-select `AskUserQuestion`): reference module code / project docs / MCP-Atlassian (Confluence/Jira) / knowledge-base / none. For each picked channel ask the **specific** path/query — no silent broad scans.
6. **Read the template + draft §1–§8.** Read [`./templates/spec.md`](./templates/spec.md) (its `<!-- instruction -->` comments are the per-section contract). Draft per [`./references/draft-generation.md`](./references/draft-generation.md): per-section sources, the **5 AC coverage types** (happy / error / authorization / domain invariant / cross-context), and the **stack-agnostic forbidden-token** rule for acceptance criteria.
7. **Socratic validation.** Walk §4 US → §5 AC → §6 NFR → §7 KPI with the shared 4-state machine (per-decision question volume scales with the depth dial — at easy, the un-asked decisions land in the assumptions ledger for a batch veto). Specify delta → [`./references/socratic.md`](./references/socratic.md): AC has a 5th option «Add another AC»; the §5 coverage gate enforces **two floors** after drops/OQ-migrations — (a) ≥1 AC of each of the 5 coverage types, and (b) **≥1 AC per retained §4 user story** (regenerate/add a replacement if a type *or* a user story is left empty). **Both are floors, not dials — enforced at every depth;** only the question volume scales. The (b) floor closes the §4→§5 link so the downstream `sequences` use-case coverage + `review` trace can't be undermined by a user story that lost its only AC. Maintain the edits-log.
8. **Critic + write + commit.** Dispatch the [`critic`](../../agents/critic.md) agent — `subagent_type: "sdd:critic"` (carries `model: opus` + `effort: high`, clean-isolated context per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — with the specify delta in [`./references/critic.md`](./references/critic.md) (over [`../_shared/critic.md`](../_shared/critic.md)) — inline the draft + edits-log, it Reads `CONTEXT.md` + the idea source itself. Resolve findings via `AskUserQuestion` (Accept revert / Accept amendment / Override-with-rationale → §1 ¶4 bullet). Run the forbidden-token regex scan as the F6 backstop. On pass, write `docs/features/<slug>/spec.md` (glossary already reconciled in-flow per step 4) and propose commit `spec: <slug>`. **Register on the roadmap:** add/promote this feature to **Now** in `docs/roadmap.md` (via `roadmap`) — an outcome one-liner + a link to this feature folder + status; if it existed as a Next candidate, move it up. (If there's no roadmap yet, skip — it's optional.) Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`spec.md`, `.size`) + *Run next* (`/clear`, then `/sdd:clarify <slug>`). (If `critic` is unavailable, fall back to a `general-purpose` Agent with the same delta.)

## Definition of Done

- `docs/features/<slug>/spec.md` written; all sections filled (or `<!-- N/A: reason -->`).
- `docs/features/<slug>/.size` exists after this stage (read if it was present, else classified + written here) — the backbone no longer reaches `design`…`plan-tests` on a silent M default.
- §5 holds ≥1 AC of each of the 5 coverage types after drops/OQ-migrations, **every §4 user story has ≥1 AC** (the use-case floor — no retained US left with zero ACs), and **0 forbidden tokens** (HTTP verbs / URL paths / status-code numerics / `module.error_name` strings / JSON fragments / SQL constructs).
- §4 roles match the `CONTEXT.md` glossary exactly (no invented `user`/`admin`).
- §8 Open Questions each carry owner + due (no lone «TBD»).
- Edits-log maintained; critic ran on the post-Socratic draft; every finding resolved or overridden.

## Anti-patterns

- **Skipping the interview front** and reconstructing the idea from the model's guess. Capture + deep-dive must actually fire `AskUserQuestion`.
- **Naming concrete technologies in §1–§3** (a specific datastore, broker, framework, or library). The spec is WHAT + WHY; technology choices belong to `design`.
- **Implementation leak in AC** — HTTP/status/error-code/SQL detail. That mapping lives in `api` and `decide-adr`.
- **Running the full ideation suite at `easy` depth** — over-production. The depth dial gates it (easy skips entirely; medium runs research + devil's-advocate; hard runs all). Feature size only *trims volume* within a level — it's no longer the gate.
- **Inventing competitors / RICE numbers** to fill the ideation pass. Better `N/A — internal tool` than fake research; accept the `researcher` agent's `RESEARCH_LIMITED` over fabricated rows.

## References & template

- [`./references/ideation.md`](./references/ideation.md) — depth-gated ideation orchestration: which named subagent (`researcher` / `strategist` / `analyst` / `devils-advocate`) runs at which level, what each returns, how outputs feed the spec.
- [`../_shared/interview-depth.md`](../_shared/interview-depth.md) — the easy/medium/hard dial set in step 1 (question volume, autonomy, which analyses run).
- [`./references/draft-generation.md`](./references/draft-generation.md) — per-section sources, 5 AC coverage types, stack-agnostic forbidden tokens.
- [`./references/socratic.md`](./references/socratic.md) — specify's delta over the shared Socratic loop.
- [`./references/critic.md`](./references/critic.md) — specify's delta over the shared critic (F6 = forbidden tokens).
- [`./templates/spec.md`](./templates/spec.md) — output scaffold; inline comments are the per-section generation contract.
