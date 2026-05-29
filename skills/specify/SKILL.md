---
name: specify
model: opus
effort: high
agents: [critic]
description: >
  Use to turn a raw feature idea into a reviewed spec.md — a lightweight Socratic interview
  front (capture the idea, deep-dive the problem) merged with a full product spec (context,
  goals, user stories, acceptance criteria, NFRs, KPIs). Triggers on "specify {slug}",
  "spec for {slug}", "write the spec", "capture this idea", "draft requirements for {slug}",
  "/sdd-specify {slug}", "напиши специфікацію {slug}", "опиши вимоги", "зафіксуй ідею".
  Drafts from templates/spec.md, validates each acceptance criterion Socratically, runs a
  clean-context critic, then writes docs/features/{slug}/spec.md. Heavy ideation (competitive
  research, strategic approaches, RICE) is offered only for M/L features.
---

# Skill: specify

Turns a one-line idea into a reviewed `spec.md`: a lightweight interview captures and stress-tests the idea, then the skill drafts a product spec (context → goals → user stories → acceptance criteria → NFRs → KPIs), validates it Socratically, and runs a clean-context critic before writing. Less typing, more reviewing. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the size matrix are **shared** — this skill keeps only its deltas:
→ [`../_shared/socratic-loop.md`](../_shared/socratic-loop.md) · [`../_shared/critic.md`](../_shared/critic.md) · [`../_shared/size-matrix.md`](../_shared/size-matrix.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

## Owner

PM + Tech Lead (co-authors). PM drives goals / non-goals / KPIs; Tech Lead drives context patterns and the acceptance-criteria coverage.

## Inputs

- `<slug>` — kebab-case feature slug.
- (Optional) `docs/features/<slug>/CONTEXT.md` — glossary; if present, its roles/terms are canonical and override anything that contradicts them.
- (Optional) `docs/features/<slug>/.size` — depth hint (MVP vs Full per the size matrix). If absent, suggest running `classify-size` first; default to M.
- (Optional) prior notes / a reference module / a ticket the user already has.

## Protocol

1. **Read context.** If `CONTEXT.md` exists, load its `## Glossary` as session state (canonical roles + terms). If `.size` exists, read it to size the spec's depth. If `docs/architecture-map.md` exists (from `survey`), read it so the spec is **architecture-aware** — it informs §1 Context, §2 Constraints, and §3 Non-goals (what the existing system already does / can't do). Absent → suggest running `survey` first, but proceed (the spec is product-level and can be captured without it). **Do not leak the map's tech into §5 AC** — AC stay business-observable; the map shapes constraints, not acceptance criteria.
2. **Capture the idea (interview front).** One `AskUserQuestion` for the raw idea in 1–3 sentences (persist verbatim as the baseline). Then a short Socratic deep-dive — 3–5 questions across problem clarity / success criteria / constraints / strategic fit, delivered in batches of 2–3. Phrase every question per [`../_shared/ask-style.md`](../_shared/ask-style.md).
3. **Depth gate.** For **M/L/XL** features, offer the heavy ideation pass (competitive research, 3 strategic approaches, multi-perspective review, devil's-advocate, Claude-proposed RICE/feasibility) → [`./references/ideation.md`](./references/ideation.md). For **XS/S**, skip it — the deep-dive answers are enough.
4. **Reconcile the glossary in-flow (hard).** On every new or unknown domain term that surfaces in the interview or the draft, invoke `glossary <slug>` for it **immediately** — compare it against `CONTEXT.md` and add/update the definition before continuing. By the time the spec is written, every §4 role and §5 domain term is already glossary-canonical; the glossary is never a deferred batch. (Plan-mode nuance: still decide add/update per term in-flow; if writes are blocked until the spec write-point, persist the reconciled terms together with the spec, but never skip the per-term compare.)
5. **Ask which extra channels to read** (multi-select `AskUserQuestion`): reference module code / project docs / MCP-Atlassian (Confluence/Jira) / knowledge-base / none. For each picked channel ask the **specific** path/query — no silent broad scans.
6. **Read the template + draft §1–§8.** Read [`./templates/spec.md`](./templates/spec.md) (its `<!-- instruction -->` comments are the per-section contract). Draft per [`./references/draft-generation.md`](./references/draft-generation.md): per-section sources, the **5 AC coverage types** (happy / error / authorization / domain invariant / cross-context), and the **stack-agnostic forbidden-token** rule for acceptance criteria.
7. **Socratic validation.** Walk §4 US → §5 AC → §6 NFR → §7 KPI with the shared 4-state machine. Specify delta → [`./references/socratic.md`](./references/socratic.md): AC has a 5th option «Add another AC»; the §5 coverage gate must keep ≥1 AC of each of the 5 types after drops/OQ-migrations (regenerate a replacement if a type breaks). Maintain the edits-log.
8. **Critic + write + commit.** Dispatch the [`critic`](../../agents/critic.md) agent — `subagent_type: "sdd:critic"` (carries `model: opus` + `effort: high`, clean-isolated context per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — with the specify delta in [`./references/critic.md`](./references/critic.md) (over [`../_shared/critic.md`](../_shared/critic.md)) — inline the draft + edits-log, it Reads `CONTEXT.md` + the idea source itself. Resolve findings via `AskUserQuestion` (Accept revert / Accept amendment / Override-with-rationale → §1 ¶4 bullet). Run the forbidden-token regex scan as the F6 backstop. On pass, write `docs/features/<slug>/spec.md` (glossary already reconciled in-flow per step 4) and propose commit `spec: <slug>`. Next: `clarify <slug>`. (If `critic` is unavailable, fall back to a `general-purpose` Agent with the same delta.)

## Definition of Done

- `docs/features/<slug>/spec.md` written; all sections filled (or `<!-- N/A: reason -->`).
- §5 holds ≥1 AC of each of the 5 coverage types after drops/OQ-migrations, and **0 forbidden tokens** (HTTP verbs / URL paths / status-code numerics / `module.error_name` strings / JSON fragments / SQL constructs).
- §4 roles match the `CONTEXT.md` glossary exactly (no invented `user`/`admin`).
- §8 Open Questions each carry owner + due (no lone «TBD»).
- Edits-log maintained; critic ran on the post-Socratic draft; every finding resolved or overridden.

## Anti-patterns

- **Skipping the interview front** and reconstructing the idea from the model's guess. Capture + deep-dive must actually fire `AskUserQuestion`.
- **Naming concrete technologies in §1–§3** (a specific datastore, broker, framework, or library). The spec is WHAT + WHY; technology choices belong to `design`.
- **Implementation leak in AC** — HTTP/status/error-code/SQL detail. That mapping lives in `api` and `decide-adr`.
- **Heavy ideation for an XS/S feature** — over-production. Run it only when size warrants.
- **Inventing competitors / RICE numbers** to fill the ideation pass. Better `N/A — internal tool` than fake research.

## References & template

- [`./references/ideation.md`](./references/ideation.md) — optional M+/L deep ideation (research / approaches / perspectives / devil's-advocate / RICE).
- [`./references/draft-generation.md`](./references/draft-generation.md) — per-section sources, 5 AC coverage types, stack-agnostic forbidden tokens.
- [`./references/socratic.md`](./references/socratic.md) — specify's delta over the shared Socratic loop.
- [`./references/critic.md`](./references/critic.md) — specify's delta over the shared critic (F6 = forbidden tokens).
- [`./templates/spec.md`](./templates/spec.md) — output scaffold; inline comments are the per-section generation contract.
