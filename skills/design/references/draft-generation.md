# Draft generation — per-section sourcing for design's in-memory draft

The authoritative format for each section is the `<!-- … -->` comment in [`../templates/sad.md`](../templates/sad.md). This file is the operational glue: where each of the 12 Arc42 sections gets its content, and the pre-Socratic hygiene checks. The draft is held **in memory** — `sad.md` is not touched between the bootstrap copy and the per-section write (the shared disk-write discipline → [`../../_shared/socratic-loop.md`](../../_shared/socratic-loop.md)).

## Inputs in priority order

1. **`CONTEXT.md` `## Glossary`** — canonical for role names + domain terms. Anything that contradicts it loses.
2. **`spec.md`** — §2 Goals, §3 Non-goals, §6 NFR (numeric targets + measurement), §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, and any §1 ¶4 «Decision override» bullets.
3. **The brownfield scan** (the Step-4 Explore subagent) — primary language + frameworks + versions; module layout; layering/ports conventions; data stores; inter-module communication style; whatever in the repo constrains this feature. Greenfield → null; note `<!-- brownfield: N/A — greenfield repo -->` in §3 and skip repo-pattern citations.
4. **Earlier-section in-memory decisions** — §4 strategy constrains §5/§6/§7/§8; §5 boundaries constrain §6 flows; §10 scenarios reference §1 quality goals. Read your own in-memory draft for later sections (no re-reading the file).

## Per-section sources

Item-banks below are guidance, not a cap. Pick how many items to draft from the size class (`.size`) and spec signal.

- **§1 Introduction & goals.** Intent (1 ¶) from spec §2 Goals + §1 Context. **Top-3 quality goals** (≥3, 1-liners) from spec §6 NFR ranked by criticality; full scenarios live in §10. Stakeholders table from spec §4 user-story roles + CONTEXT glossary (add a Tech Lead sign-off row).
- **§2 Constraints.** **Technical** — language/framework/datastore + versions + architecture convention from the brownfield scan (a spec §6 NFR pin override wins). **Organisational** — spec deadline + effort budget if quoted, else `<TBD by PM>` + a §11 row. **Conventions** — link the repo's convention file + any module-level patterns. **Regulatory** — spec §6.1 verdict + abuse-case controls. Never N/A.
- **§3 Context & scope.** 2–3 sentences of business context from spec §1. External-systems table from spec §6.1 cross-context entries + the scan's communication/data-store rows. **C4 Context (L1)** Mermaid block — actors from CONTEXT roles + spec §4, external systems from the scan; 5–10 elements. Syntax → [`./c4-mermaid-syntax.md`](./c4-mermaid-syntax.md). Never N/A.
- **§4 Solution strategy.** **Top-3 strategic choices** (≥3) — the ADR seeds; each 2–3 sentences of rationale citing relevant quality goals + constraints. Decision-bank, **Target surface(s) first** (`backend-service` / `web-frontend` / `mobile-app` / `desktop-app` / `cli` / `worker` / `library-sdk` — derived from spec §1 «for whom» + §4 roles, written to frontmatter `target_surfaces`, gates §5 + every downstream stage → [`../../_shared/surfaces.md`](../../_shared/surfaces.md)); then module-to-module integration (sync call / async events / shared transaction); persistence (single store / per-module store / read-write split); **UI-architecture, one per declared UI surface** (web → server-rendered / SPA / hybrid; mobile → native / cross-platform; + state-management + routing if warranted — this **replaces** the old single "read-side delivery" item, lifting it to a per-surface decision); concurrency (optimistic / pessimistic / event-sourced); cache tier (none / in-process / shared). The blast-radius gate fires almost always here — plan ≥2 ADRs from §4.
- **§5 Building block view.** 1 ¶ on the layering style + why. Decision-bank: extend an existing module vs a new one; layering style (default = the repo's convention; only ask on divergence); internal sub-package layout. **C4 Container (L2)** Mermaid block — **one `Container` per declared `target_surface`** (a fullstack `[backend-service, web-frontend]` draws both the backend-API container and the web/SPA container; a `[backend-service, mobile-app]` draws the API + the mobile app), plus the feature's other modules/services as `Container`, datastores as `ContainerDb`. Syntax → [`./c4-mermaid-syntax.md`](./c4-mermaid-syntax.md).
- **§6 Runtime view.** Seed the **primary critical flow(s)** here — happy path always; a failure-mode flow if §4 picked async or has an external dependency; an event-propagation flow if §4 picked events. design **seeds**; the `sequences` stage then covers **every §5 AC** (no cap — a flow per critical user story, branches for the rest). One `sequenceDiagram` per flow, actors + ≥2 participants + ≥3 arrows, referencing §5 containers by name (no inventing). Messages are semantic — no HTTP verbs / paths / status codes (those arrive at the `api` stage). Never N/A for M+; XS/S keeps ≥1 happy-path flow.
- **§7 Deployment view.** Topology in 2–3 sentences (where it runs, replicas, scaling thresholds). Monitoring rows (metrics / alerts / tracing) from the repo's observability conventions + spec NFR latency targets. Scaffold → [`../templates/deployment.md`](../templates/deployment.md). XS/S with no deployment change → `<!-- N/A: reuses existing deployment unit, no infra change -->` (still write a one-sentence justification).
- **§8 Crosscutting concepts.** Table rows: logging / auth / errors / ID strategy / i18n / observability / events / rate-limiting (where applicable). **Default = inherit the repo's conventions**, bundled as one question («I'm assuming the repo's defaults. Override?» / `Keep defaults` / `Custom for §X`). Per-feature override only if spec §6 NFR or §6.1 Security signals it.
- **§9 Architecture decisions.** Table auto-populates as ADRs spawn in §4–§8 (the blast-radius gate). No drafting here — starts empty, fills during the Socratic walk.
- **§10 Quality requirements.** **≥3 scenarios** (one per §1 quality goal) in When / Then / How-verify form. Numbers from spec §6 NFR **verbatim** — no inventing, no rounding (a critic F6 hit). Forbidden: «fast» / «scalable» / «highly available» without a number. How-verify = a concrete test / chaos drill / load-test / metric, not «integration test».
- **§11 Risks & technical debt.** Auto-generated at the end of the walk from the edits-log + spec §8 Open questions + the scan's brownfield gotchas. Decision-bank: outbox/queue lag during an outage; schema-versioning debt; brownfield drift; security debt accepted in v1; accepted-debt rows. **Open-architectural-decision rows** come from Save-as-OQ resolutions (severity literal `Open question`). Never N/A.
- **§12 Glossary.** Auto-extract CONTEXT terms that appear in the body + any domain terms surfaced during the walk that aren't in CONTEXT (flag those for a `glossary` follow-up). Never N/A.

## Pre-Socratic hygiene

Before handing the in-memory draft to the Socratic walk, self-check and regenerate the offending section if any of these fail (the critic is the second backstop):

- §1 Stakeholders + §3 actors use CONTEXT glossary roles verbatim (no invented `user`/`admin` when the glossary names specific roles).
- §2 Constraints reflect the scan (no contradicting the repo's conventions without an Override note pointing at §11).
- §3 + §5 Mermaid blocks declare every element before any `Rel` line (no dangling references; no `Container_Bondary` typos).
- §10 numeric targets cite the spec §6 NFR row exactly (no inventing, no rounding `≤250ms` to `≤300ms`).
- §6 sequence diagrams reference §5 Container participants by name.
- §11 includes ≥1 row from the scan's brownfield gotchas (or `<!-- N/A: greenfield -->`).

## Cadence (size-aware) — design's question budget

The 4-state machine, the mini-recap-every-5, and the soft per-section budget all come from [`../../_shared/socratic-loop.md`](../../_shared/socratic-loop.md). design's per-section targets:

| Section | Typical Qs | Note |
|---|---|---|
| §1 Intro & goals | 0–1 | Usually pulled from the spec. Ask if the top-3 quality goals are unclear. |
| §2 Constraints | 1–2 | One bundled «any stack/version overrides?» |
| §3 Context | 0–1 | Mostly drawn from spec + the scan. |
| §4 Solution strategy | 2–4 | The dense one — strategic choices, expect ADRs. |
| §5 Building blocks | 1–3 | Module boundaries, layering style. |
| §6 Runtime | 1–2 | Which failure modes get a diagram. |
| §7 Deployment | 0–2 | Often `<!-- N/A -->` for a feature inside an existing unit. |
| §8 Crosscutting | 1 bundled | «Repo defaults + overrides?» |
| §9 ADR index | 0 | Auto-populated. |
| §10 Quality reqs | 1–2 | Numbers from spec NFR + verify method. |
| §11 Risks | 1–2 | «Top-3 risks?» then refine. |
| §12 Glossary | 0 | Auto-extracted. |

**Total target: 8–20 questions across the whole pass.** Above 25 is fatigue territory — bundle harder (one question per *uncertainty*, not per *parameter*: a single «keep the repo's logging/error/ID defaults?» beats three separate questions). Slow down when the user starts replying single words three times running.
