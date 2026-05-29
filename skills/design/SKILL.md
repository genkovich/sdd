---
name: design
model: opus
effort: high
agents: [explorer, critic]
description: >
  Use to produce a Software Architecture Document for a feature — Arc42 12 sections + C4 L1/L2
  inline + ADRs spawned on a blast-radius gate — once spec.md and CONTEXT.md exist. Triggers on
  "design {slug}", "architecture for {slug}", "SAD for {slug}", "arc42 for {slug}",
  "C4 context+container for {slug}", "/sdd-design {slug}", "спроектуй архітектуру {slug}",
  "SAD для {slug}", "архітектурний документ {slug}". Drafts §1–§12 in-memory, batch-validates each
  section Socratically (4-state machine), spawns an ADR only when a decision crosses the
  blast-radius threshold (irreversible / multi-module / has legitimate alternatives), writes each
  resolved section + its ADRs atomically, then runs a clean-context critic before finalizing.
  Brownfield: dispatches an Explore subagent to map the repo first. Hard-refuse if spec.md or
  CONTEXT.md is missing.
---

# Skill: design

Generator of the **Software Architecture Document** (`docs/features/<slug>/sad.md` — Arc42 12 sections, C4 Context inline in §3 and C4 Container inline in §5) plus supporting ADRs (`docs/features/<slug>/adr/NNNN-*.md`). It drafts all 12 sections in memory, walks them Socratically one section at a time, spawns an ADR only when a decision's *blast radius* (масштаб удару — how painful it is to reverse the decision later) crosses the gate, writes each resolved section and its ADRs as one atomic commit, and runs a clean-context critic over the finished SAD. The document itself is the state — resuming after an interrupt is free. L3 Component / L4 Code are out of scope. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the size matrix are **shared** — this skill keeps only its deltas:
→ [`../_shared/socratic-loop.md`](../_shared/socratic-loop.md) · [`../_shared/critic.md`](../_shared/critic.md) · [`../_shared/size-matrix.md`](../_shared/size-matrix.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

## Owner

Architect / Tech Lead (drives everything). PM is consulted only on §10 Quality goals and §11 Risk severities.

## Inputs

- `<slug>` — same feature slug used by every earlier stage.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md` AND `docs/features/<slug>/CONTEXT.md`. If either is absent → STOP and point: «run `specify <slug>` / `glossary <slug>` first — design reads the spec's goals/NFRs and the glossary's roles as canonical».
- (Optional) `docs/features/<slug>/.size` — depth hint (MVP vs Full + expected ADR count per the size matrix). Absent → default to M (full set).
- A git repo — so the Step-3 Explore subagent can read code on a brownfield.
- Skip if `sad.md` already has all 12 sections filled AND `adr/` has ≥1 file — suggest review instead.

## Protocol

1. **Gate + size.** `test -f docs/features/<slug>/spec.md && test -f docs/features/<slug>/CONTEXT.md` → either missing = refuse with the pointer above. Read `.size` if present (shapes ADR count + §6 flow count — see the size matrix).
2. **Read upstream.** `spec.md` (§2 Goals, §3 Non-goals, §6 NFR with numeric targets + measurement, §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, any §1 ¶4 «Decision override» bullets); `CONTEXT.md` `## Glossary` (canonical roles + domain terms — wins over anything that contradicts).
3. **Current architecture — read the map, don't re-scan.** Prefer `docs/architecture-map.md` (produced by `survey`): if it exists and is fresh (its `reflects_commit` ≈ current HEAD), read it — that IS the brownfield context (module layout, layering, datastores, conventions, the C4 of what exists). Re-scan only if the map is **absent or stale**: dispatch the [`explorer`](../../agents/explorer.md) agent — `subagent_type: "sdd:explorer"` (`model: haiku` + `effort: low`, clean-isolated per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — for «module layout, layering/ports conventions, datastores, inter-module comms, anything that constrains `<slug>`», and suggest the user run `survey` to persist it. Greenfield (no source + no map) → note `<!-- brownfield: N/A — greenfield repo -->` in §3. (Fallback to a `subagent_type: "Explore"` Agent if `explorer` unavailable.)
4. **Bootstrap + read template.** Copy [`./templates/sad.md`](./templates/sad.md) → `docs/features/<slug>/sad.md`; patch frontmatter (`updated_at`, `feature_size` from `.size`). Commit `design: <slug> bootstrap sad.md`. Read the template's `<!-- … -->` comments (the per-section contract) + [`./templates/adr.md`](./templates/adr.md) (MADR shape). This is the only file write between Step 4 and Step 6 — Step 5 drafts in-memory.
5. **Per-section draft (in-memory).** For each §1 → §12, draft proposed content + the decisions it contains, bundling trivial convention defaults into one question. Per-section sourcing, item-banks, the question budget, and pre-Socratic hygiene → [`./references/draft-generation.md`](./references/draft-generation.md). Do NOT write `sad.md` here.
6. **Socratic walk + blast-radius gate, per-section write.** For each §1 → §12: render the full section + its numbered decisions (big picture), walk one `AskUserQuestion` per decision with the shared 4-state machine, apply transitions in-memory, run the blast-radius gate on each **Approved** decision (spawn an ADR on 2-of-3), then write the resolved section + its spawned ADRs + commit `design: <slug> sad §N — <summary>`. Never return to a written section. design delta → [`./references/socratic.md`](./references/socratic.md) (section list, decision-types, the gate); gate scoring → [`./references/blast-radius.md`](./references/blast-radius.md); C4 syntax for §3/§5 → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md); design-specific question shapes → [`./references/ask-examples.md`](./references/ask-examples.md). Maintain the edits-log + an adjacent ADR-spawns log.
7. **Critic + finalize.** Dispatch the [`critic`](../../agents/critic.md) agent — `subagent_type: "sdd:critic"` (carries `model: opus` + `effort: high`, clean-isolated per [`../_shared/agent-roster.md`](../_shared/agent-roster.md); fallback `general-purpose` if unavailable) — with the design delta in [`./references/critic.md`](./references/critic.md) (over [`../_shared/critic.md`](../_shared/critic.md)) on the final `sad.md` + edits-log + ADR-spawns log; resolve each finding via `AskUserQuestion` (Accept revert / Accept amendment / Override-with-rationale → §1 ¶4 bullet). Run the pre-write backstop scans: **validate every Mermaid block in `sad.md` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint — fix any that don't parse, never commit a broken diagram); ADR title in decision-form kebab-case + Status `Accepted`; §9 closed against `adr/`; no `<placeholder>` stubs. On pass, write any amendments + commit `design: <slug> finalization (critic pass)`. Next: `sequences <slug>` (writes flows into §6).

## Definition of Done

- `docs/features/<slug>/sad.md` exists with all 12 Arc42 sections filled OR marked `<!-- N/A: <reason> -->`.
- §3 has a real `C4Context` block and §5 a real `C4Container` block — real names from CONTEXT + the scan, no `<placeholder>` stubs, no `Container_Bondary` typos. §6 has ≥1 `sequenceDiagram` (3–5 for M+).
- §9 ADR table is closed against `adr/` (every file has a row, every row a file). 2–4 ADRs for XS/S, 5–12 for M, 10–15 for L/XL; every ADR Status = `Accepted`, title in decision-form (`0003-sliding-window-counter.md` ✓ vs `0003-rate-limiting.md` ✗), no strawman options.
- §10 scenarios are testable (When / Then / How-verify) and cite spec §6 NFR numbers verbatim (no inventing, no rounding).
- §11 carries a row for every `save_as_oq` decision with both owner AND due (severity literal `Open question`); never N/A.
- §1 Stakeholders + §3 actors match the CONTEXT glossary exactly (no invented `user`/`admin`).
- Step-3 Explore ran on a brownfield (or §3 has the greenfield note). Edits-log maintained. The critic ran on the post-Socratic SAD; every finding resolved or overridden.

## Anti-patterns

- **An ADR for every decision** — kills the genre. Only blast-radius decisions become ADRs (5–12 for M, not 25). Conversely, missing an irreversibility under-ADRs the feature.
- **ADR `Status: Proposed` from this skill** — it is synchronous (you decide with the user now), so Status is `Accepted`. Use `decide-adr` for an async Proposed → Accepted flow.
- **ADR title in problem-form** (`0003-rate-limiting.md`) or with a **strawman option** (an alternative an existing constraint already excludes) — both dilute the ADR genre and trigger the critic's F6.
- **Inventing §10 numbers** the spec never agreed to — cite spec §6 NFR verbatim. **Naming a concrete stack in §2** that contradicts the repo's conventions without an Override note pointing at §11.
- **Skipping the Step-3 Explore on a brownfield** — guessing the layout produces a fictional §5 Container view and invented §2 Constraints.
- **Returning to a written section** — each section commits atomically; cross-section drift is the critic's job, not a re-walk. Re-opening §4 after writing §10 means you don't trust the per-section batch.
- **Save-as-OQ without owner+due** — capture both in the follow-up; missing either downgrades to Drop with a warning, never a half-filled §11 row.
- **Resolving critic findings unilaterally** (without `AskUserQuestion`) or **one giant end-of-pass commit** — both defeat the per-section, user-in-the-loop contract.
- **Spilling into C4 L3/L4** — out of scope; suggest a separate diagramming pass.

## References & template

- [`./references/draft-generation.md`](./references/draft-generation.md) — Step 5: per-section sourcing for §1–§12, item-banks, the question budget, pre-Socratic hygiene.
- [`./references/socratic.md`](./references/socratic.md) — design's delta over the shared Socratic loop (section list, decision-types, the blast-radius gate, the §11 OQ table).
- [`./references/blast-radius.md`](./references/blast-radius.md) — the 3-criteria ADR gate (irreversible / multi-module / legitimate alternatives), scoring, target counts.
- [`./references/critic.md`](./references/critic.md) — design's delta over the shared critic (F5 floor, F6 = NFR-leak + strawman-ADR + §2-vs-repo, F1 = strategic-vector drift).
- [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md) — C4Context + C4Container Mermaid cheatsheet for §3/§5.
- [`./references/ask-examples.md`](./references/ask-examples.md) — design-specific question shapes (strategic-with-ADR-spawn, blast-radius gate, Save-as-OQ follow-up).
- [`./templates/sad.md`](./templates/sad.md) · [`./templates/adr.md`](./templates/adr.md) · [`./templates/deployment.md`](./templates/deployment.md) — output scaffolds; inline comments are the per-section generation contract. (C4 syntax → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md).)
