# SDD — Spec-Driven Development for Claude Code

A self-contained Claude Code plugin that carries a feature from a one-line idea to
**reviewed, verified, shipped** code through **17 atomic, stack-agnostic skills** and a
**TDD implementation engine** — with a living roadmap above the per-feature flow.

Every skill is Socratic (it walks decisions with you, it doesn't dump a wall of output),
gated (a stage hard-refuses when its prerequisite artifact is missing), and stack-agnostic
(no language, tracker, or test tool is hard-coded — the skills detect what your repo uses).
The Q&A skills (`specify` / `clarify` / `design`) are also **depth-tunable** — an easy / medium / hard
dial decides how much the skill decides for you vs. interrogates you with trade-offs.

## Install

**Claude Code** — native plugin:

```text
/plugin marketplace add genkovich/sdd
/plugin install sdd@sdd
```

After updating to a new release: re-run `/plugin install sdd@sdd`, then `/reload-plugins`.

**Codex CLI** — `cd` into your project first: the script installs into the **current directory**
(`.agents/skills/` + `.codex/agents/`). Add `--global` after `codex` to install under `~` instead,
or `--prefix DIR` to install under an arbitrary directory (useful for trying it out in a sandbox):

```sh
cd your-project
curl -fsSL https://raw.githubusercontent.com/genkovich/sdd/main/install.sh | bash -s -- codex
```

Then restart codex (skills are discovered at session start) and type `$sdd-specify`.

Alternative — the plugin marketplace. Note that `add` only **registers** the marketplace, it
installs nothing by itself:

```text
codex plugin marketplace add genkovich/sdd
```

then **inside codex** run `/plugins`, switch to the `sdd` marketplace tab and pick
**Install plugin**. One naming nuance: the marketplace install registers the **original** skill
names (`$specify`), while the installer script prefixes them — `$sdd-specify` — because bare
names like `review` / `design` / `api` collide with generic skills. **Pick one of the two paths,
not both** — they register different names for the same skills, so running both shows every
skill twice. To undo the script install: re-run `install.sh codex --uninstall` from the same
directory (or with the same `--global` / `--prefix`). To undo the marketplace install: `/plugins`
→ the sdd tab → uninstall (or remove the `[plugins."sdd@…"]` entry from `~/.codex/config.toml`).
The script warns when it detects a marketplace install already registered.

> **Windows note.** The installer is a bash script — run it from Git Bash or WSL. The directories
> it writes (`.agents/`, `.codex/`, `.cursor/`) start with a dot, which Explorer hides by
> default — enable «Hidden items» (or `dir /a`) to see them.

**Cursor** (2.4+) — the same script; `cd` into your project first (installs into
`.cursor/skills/` + `.cursor/agents/` of the current directory; `--global` for `~`,
`--prefix DIR` for an arbitrary directory):

```sh
cd your-project
curl -fsSL https://raw.githubusercontent.com/genkovich/sdd/main/install.sh | bash -s -- cursor
```

Then restart Cursor (or run **Developer: Reload Window**) and invoke a stage by typing `/` in
the chat and picking `sdd-specify`. (Cursor also reads `.agents/skills/`, so a Codex install is
already visible to Cursor.) Once the plugin is listed on the Cursor marketplace, installing from
the in-app marketplace panel works too — project- or user-scoped.

How every Claude-specific mechanism — `AskUserQuestion`, subagents, `/clear`, the implement
engine modes — maps to Codex / Cursor is one table:
[`skills/_shared/tool-adapters.md`](./skills/_shared/tool-adapters.md).

## Start here

The flow is a straight line: **each stage writes a file the next one reads.** Run them in order
(the diagram + table are just below).

```text
/sdd:survey                         ← once per repo: map an existing codebase, OR bootstrap an empty one
/sdd:specify checkout-discounts     ← interviews you, writes the spec (you don't bring one)
/sdd:design … → /sdd:implement … → /sdd:review … → /sdd:ship
```

Two things to know up front: **`survey` runs once per repo** — on an existing codebase it maps the
current architecture to `docs/architecture-map.md` (every later stage reads it); on an empty repo it
runs a short foundation session and scaffolds the skeleton ([detail below](#where-we-study-the-codebase--hold-the-current-architecture)).
And **`specify` *creates* the spec** from a short interview — you bring the idea, not the document.

From there you walk the backbone in order. Each step reads the previous step's file and
refuses if it's missing, so you can't skip ahead by accident.

**Every stage ends with a copy-ready handoff block** ([`skills/_shared/handoff.md`](./skills/_shared/handoff.md)):
*What I did* + *Review before continuing* (links to the files it wrote, so you can eyeball them at the
gate) + *Run next* — **`/clear`**, then the next `/sdd:…` command in a fenced block you copy in one
click. The `/clear` matters because each stage is gated and **re-reads its inputs from disk**, so it
needs no carryover — clearing keeps the context small and stops one stage's chatter from drifting into
the next. (Loop-backs are the exception — when `review` bounces back to `implement`, you stay in
context to iterate; utilities make `/clear` optional.) It looks like this:

```md
## ✅ specify — checkout-discounts

**What I did**
- wrote docs/features/checkout-discounts/spec.md — size M (from .size); proposed commit `spec: checkout-discounts`

**Review before continuing**
- docs/features/checkout-discounts/spec.md — goals, user stories, the §5 acceptance criteria

**Run next**
1. /clear — mandatory (fresh context; the next stage re-reads its inputs from disk)
2. then run:  /sdd:clarify checkout-discounts
```

## The flow

There are three kinds of skill. Most of your time is the **backbone** — a straight line you
walk in order. A few are **utilities** you call whenever you need them. Two **close the loop**
after the code is written.

```mermaid
flowchart LR
    SV[survey<br/>once per repo] --> S
    subgraph backbone["BACKBONE — run in order"]
        S[specify] --> CL[clarify] --> D[design] --> SQ[sequences] --> DM[data-model] --> API[api] --> T[tasks] --> PT[plan-tests] --> IM[implement]
    end
    IM --> RV[review] --> SH[ship]
    subgraph util["UTILITIES — call anytime"]
        CS[classify-size]
        GL[glossary]
        ADR[decide-adr]
        FX[fix]
    end
    SH --> done([shipped: PR + changelog])
```

### Step 0 — survey (once per repo, before the backbone)

| # | Skill | What it does | Reads → Produces |
|---|---|---|---|
| 0 | **survey** | Existing repo → scans once, persists the current architecture. Empty repo → level-adaptive foundation session → fixes the foundation + emits a scaffold `tasks.json` for `implement`. | the repo → `docs/architecture-map.md` (+ scaffold `tasks.json` on greenfield) |

### Backbone — the straight line (run in order)

| # | Skill | What it does | Reads → Produces |
|---|---|---|---|
| 1 | **specify** | Interviews you to capture the idea, writes the product spec + acceptance criteria (reads the architecture map for constraints) | *your idea*, `architecture-map.md` → `spec.md` |
| 2 | **clarify** | Sweeps the spec for ambiguities (a devil's-advocate pass), closes or defers each | `spec.md` → tightened `spec.md` |
| 3 | **design** | **Matches the feature to your existing architecture** (see below) + **declares the target surfaces**, writes the Arc42 SAD + C4 + ADRs | `spec.md`, `CONTEXT.md` → `sad.md`, `adr/*` |
| 4 | **sequences** | Draws the runtime flows as Mermaid sequence diagrams | `sad.md` → `sad.md §6` |
| 5 | **data-model** | Designs the schema and writes the actual forward+rollback migrations — **staged** under the feature folder, not the live tree (`implement` promotes them) | `spec.md`, `sad.md`, sequences → `data-model.md`, staged `migrations/*.up/down.sql` |
| 6 | **api** | Derives the OpenAPI contract from the data model + sequences + spec | `data-model.md`, sequences, `spec.md` → `contracts/openapi.yaml` |
| 7 | **tasks** | Breaks the work into atomic ≤1-day tasks + a `tasks.json` dependency DAG | all of the above → `tasks/*`, **`tasks.json`** |
| 8 | **plan-tests** | Maps every acceptance criterion to ≥1 test (inline in the spec for XS/S) | `spec.md`, `data-model.md` → `test-plan.md` (M+) or an inline `## Test plan` in `spec.md` (XS/S) |
| 9 | **implement** | The TDD engine: writes a failing test, makes it pass, gates, commits — per task; **promotes** each staged migration into the live `migrations/` as it builds | `tasks.json` + all artifacts → code + tests + promoted migrations, committed |

### Close the loop (after the code is written)

| # | Skill | What it does | Reads → Produces |
|---|---|---|---|
| 10 | **review** | An **independent, clean-context** code review of the *whole* change against spec/AC + quality | the diff + `spec.md` → review record, `PASS` / `CHANGES REQUESTED` |
| 11 | **ship** | **Verifies the feature actually runs** (not just green tests), writes the changelog, opens the PR | the reviewed change → changelog + PR (never auto-merges) |

`review` can bounce back to `implement` if it finds an unmet acceptance criterion. `ship` is the
end: a reviewed, verified change with a changelog and an open PR — merging to main stays your call.

> **"We test and review, right?"** Yes — in two places. `implement` runs a **per-task gate**
> (unit + integration + lint + vet) on every task as it goes, so each task is green before it's
> committed. Then `review` does the **independent, whole-change** code review a human reviewer
> would do on the PR, and `ship` **runs the feature for real** against its acceptance criteria.
> Tests-pass happens continuously inside `implement`; the cross-cutting review + real-world
> verification are the explicit `review` and `ship` steps.

### Utilities — call whenever you need them (not part of the line)

- **classify-size** — size the feature XS/S/M/L/XL (writes `.size`); later skills read it to decide MVP vs full depth. Run it at the start, or any time scope changes.
- **glossary** — capture a domain term in `CONTEXT.md` with a definition. Run it whenever a new term shows up; `design` and the spec read the glossary.
- **decide-adr** — write a standalone ADR after the fact, when `tasks` (or a review) flags a decision that needs recording but wasn't captured during `design`.
- **fix** — the **bugfix entry point**: reproduce, trace the symptom to the spec's acceptance
  criteria (regression / ambiguous AC / uncovered gap), pin it with a failing test, apply the
  minimal fix through the same gate `implement` runs, then patch the spec and write a fix record
  under `_fixes/`. Works on a repo with no specs at all (fixes code-first, recommends `survey`).

## Interview depth (easy / medium / hard)

The Q&A skills open by setting a **depth dial** — one `AskUserQuestion` per run that tunes how much
the skill decides on its own vs. interrogates you. It changes *how many* questions you get, never
*what gets covered*:

- **easy** — the skill makes the reversible, low-stakes calls itself with sensible defaults, asks
  only the irreversible / high-blast-radius ones, and **lists every assumption it made** so you can
  veto. Minimal analyses; diagrams written + summarized (no per-item question).
- **medium** (default) — the balanced Socratic walk: one question per real decision.
- **hard** — walk every decision with the trade-off foregrounded, run the **full ideation analysis
  suite** (competitive research, three strategic approaches, multi-perspective review,
  devil's-advocate), and probe edge cases harder.

The default is `interview_depth` in `.claude/sdd.local.md` (else medium); override it per run, or
pass `--depth=easy|medium|hard`. Full semantics: [`skills/_shared/interview-depth.md`](./skills/_shared/interview-depth.md).

Two things the dial **never** weakens — they hold at every level:

- **Readable diagrams.** `design` and `sequences` confirm each diagram **in prose** (a plain-language
  walk of the flow + branches) and write the source to the file (where Obsidian renders it) — they
  **never dump raw Mermaid into the terminal** as the thing to approve. If `mmdc` is installed, an
  image is rendered too. ([`skills/_shared/diagram-presentation.md`](./skills/_shared/diagram-presentation.md))
- **Full use-case + acceptance-criteria coverage.** Every spec §4 user story and §5 AC is covered
  end-to-end: `specify` enforces a **use-case floor** (every user story carries ≥1 AC) and `clarify`
  re-catches a story that lost it; `sequences` maps each user story to a flow and each AC to a flow,
  a branch, or an explicit non-runtime N/A (no flow cap); and `review` traces the whole set through
  spec → sequences → data-model → api → tasks → implement, flagging anything that dropped out. Even
  `easy`/XS covers every use-case + AC — it just asks fewer questions about *how*.

## Target surfaces (what's being built)

`design` opens §4 by declaring the feature's **target surface(s)** — *what's being built* — grounded
in C4 container types: `backend-service`, `web-frontend` (SSR or SPA), `mobile-app`, `desktop-app`,
`cli`, `worker`, `library-sdk`. The choice is derived from the spec's "for whom" (the spec stays
product-level — it never names a surface), gated by the blast-radius gate (multi-surface usually
spawns an ADR), drawn as **one C4 container per surface** in SAD §5, and written to the SAD
frontmatter `target_surfaces: [...]`. Downstream stages **read** that declaration and gate their
output by it — they never re-derive it:

- **`api`** picks the contract form from the surface (HTTP/OpenAPI · gRPC · events · `cli.md` ·
  `public-api.md`); a UI surface *consumes* the backend contract rather than authoring one.
- **`sequences`** draws **UI-driven flows** (`<user>` → `<ui>` → `<service>`) for a UI surface.
- **`tasks`** adds a **`ui`** task layer for a UI surface (backend-only stays domain/infra/app/ports).
- **`plan-tests`** adds the **component / visual-regression / e2e-through-UI** tiers (the frontend
  "testing trophy") for a UI surface; `implement` detects the actual tools (Playwright / Storybook / …).
- **`review`** traces every acceptance criterion through *its* surface — a UI AC to a component /
  e2e-through-UI test, not only a backend one.
- **Reuse, don't reinvent.** `survey` inventories the existing **design system / components / tokens /
  styling** into `architecture-map.md` §Frontend; `design` / `tasks` / `implement` **compose and
  extend** it (modelled on the closest existing screen) instead of hand-rolling new UI — the frontend
  echo of the backend's match-the-repo + copy-the-closest-precedent.

It's **Option B** — frontend-awareness threaded through the existing stages (a `ui` layer,
UI-architecture ADRs, UI flows, frontend test tiers); there is deliberately **no** separate
component-tree / design-token / screen artifact. Full semantics:
[`skills/_shared/surfaces.md`](./skills/_shared/surfaces.md).

## Where the spec comes from

It's not an input you have to write — **`specify` produces it.** Its interview front asks 3–5
questions about the problem, the users, and what success looks like, then drafts the spec,
validates each acceptance criterion with you, and runs a clean-context critic before writing
`spec.md`. The idea is the input; the spec is the output.

## Where we study the codebase / hold the current architecture

The existing system is studied **once, in `survey`** (Step 0), which persists
`docs/architecture-map.md` — the current architecture: module layout, layering, datastores,
conventions, and a C4 of what exists. That map is the single source of "what's already here":

- **`specify`** reads it so the spec's constraints / non-goals reflect the real system (without
  leaking tech into the acceptance criteria).
- **`design`** reads it and **matches** the feature to that reality — the SAD describes *your*
  system extended, not a greenfield design in a vacuum. It re-scans (via `explorer`) only if
  the map is missing or stale.
- **`data-model`** and **`implement`** read it for the persistence + wiring conventions the new
  code must follow, instead of each re-discovering them.

So you don't re-open "what's the current architecture?" at every stage — `survey` answers it once
and the map carries it. Refresh the map (`survey` again) when the repo has drifted past the
`reflects_commit` it records. In `design`, decisions expensive to reverse cross a blast-radius
gate and become ADRs.

**On an empty project there's no current architecture to study — so `survey` establishes one.**
Its greenfield mode gauges how you want to engage, then picks the stack / structure / data approach
/ conventions with you (defaults-heavy), fixes them as the foundation (the same map, marked
`mode: greenfield-bootstrap`, + foundational ADRs for the irreversible choices), and emits a
scaffold `tasks.json`. `implement` then materializes the skeleton — anchored on a smoke test
(«builds + boots + the test and migration tooling run») rather than per-folder TDD. After that the
repo is real and the per-feature flow builds into it normally.

## The roadmap (the portfolio layer)

The backbone builds **one feature at a time**. `roadmap` is the layer **above** it — one living
`docs/roadmap.md` that shows the work *across* features, kept at **outcome altitude** (the "why",
not a feature-and-date list, which is the biggest source of planning waste):

- **Now** — committed, spec'd, in progress. Each item links to its `docs/features/<slug>/` (it
  doesn't restate the spec) + a status.
- **Next** — problems/opportunities, deliberately *not* yet spec'd, ordered by a light **RICE**
  score (Reach × Impact × Confidence ÷ Effort). This is the candidate pool.
- **Later** — directional outcomes/themes, no detail.
- **Shipped** — what landed, with a link.

It stays current because the pipeline updates it: **`specify` promotes a feature to Now**, and
**`ship` moves it to Shipped** — delivery itself keeps the roadmap in sync, so it doesn't rot. It
carries a one-line "direction, not a promise" disclaimer and never carries dates.

## The implementation engine

`implement` reads `tasks.json`, builds a dependency DAG, and runs a **TDD cycle per task** —
`SELECT → RED → GREEN → REFACTOR → GATE → COMMIT`. It writes a failing test first, proves the
failure is for the right reason, writes the minimal code to pass, keeps refactors green, runs
the gate, and commits with `SDD-Task` / `SDD-AC` trailers.

Three execution modes, chosen automatically from settings + DAG shape (with graceful fallback):

- **Sequential single-agent TDD** — the default and the floor everything degrades to.
- **Agent team** (`team_mode: true`) — `test-author` → `implementer` → `reviewer`
  over the DAG, coordinated through a shared task list, one git worktree per agent.
- **Dynamic workflow** (`workflow_mode: auto`) — a generated `Workflow` pipeline that fans out
  independent tasks up to a parallelism cap.

## Models, effort & agents

Every skill and every agent declares an **execution profile** in its frontmatter — which model,
how much reasoning effort, and which agents it spawns:

```yaml
# a skill's frontmatter
model: opus        # haiku | sonnet | opus | inherit
effort: high       # low | medium | high | xhigh | max
agents: [critic]   # the agents this skill spawns
```

Model is chosen by the **kind of work**, not by taste:

| Kind of work | Model | Effort | Who |
|---|---|---|---|
| Judgment (spec, design, review, critique, ambiguity, strategy) | `opus` | `high` | specify, clarify, design, review · `reviewer` / `critic` / `devils-advocate` / `strategist` / `analyst` |
| Execution (write tests, write code) | `sonnet` | `medium` → `high` on escalation | `test-author`, `implementer` |
| Research / gathering (+ web) | `sonnet` | `medium` | `researcher` (competitive / adjacent-solution research) |
| Search / scan / derivation | `haiku` / `inherit` | `low` / `medium` | `explorer`; data-model, api, sequences, tasks |

The nine agents (`agents/`): **explorer** (brownfield scan), **test-author** (failing tests),
**implementer** (makes them pass), **reviewer** (independent review), **critic**
(coherence critique), **devils-advocate** (ambiguity + failure-mode hunt), **researcher**
(competitive / web research), **strategist** (three strategic approaches), **analyst**
(multi-perspective review) — the read-only ones run in **clean isolated context** (fresh eyes) and
emit only cited findings. The last three are the **ideation analyses**, dispatched by `specify` and
gated by the depth dial (easy skips them; hard runs the full suite).

The full policy — override precedence, the `.size` scaling, and the env-var fallback for the
`effort:` no-op some builds have — lives in one place: [`skills/_shared/agent-roster.md`](./skills/_shared/agent-roster.md).
Short version: if a run feels under-reasoned, set `CLAUDE_CODE_EFFORT_LEVEL`.

### Configuration — `.claude/sdd.local.md`

The pipeline **auto-creates** this per-project settings file (YAML frontmatter) with **documented
defaults** the first time a skill needs it — normally `specify` at the start — and adds it to
`.gitignore` (it's per-developer). The file is **self-documenting**: every key carries its default,
its allowed values, and a one-line explanation inline. Edit it to change behaviour. One key is
**plugin-wide** — `interview_depth` is read by the Q&A skills (`specify` / `clarify` / `design`) to
pre-select the depth dial; the rest configure
the `implement` engine:

```yaml
interview_depth: medium    # easy | medium | hard — default depth for specify/clarify/design
tdd: true                  # enforce red→green→refactor
team_mode: false           # true → agent team via TeamCreate
workflow_mode: auto        # auto → dynamic Workflow; off → never
max_parallel_agents: 3
isolation: worktree        # worktree | inplace (parallel>1 ⇒ forces worktree)
stop_on_red: true
max_red_retries: 3
gate_lint: true
gate_vet: true
require_integration: auto  # auto | always | never (Docker-probed)
auto_commit: per_task      # per_task | per_phase | off
branch_strategy: feature   # feature | current
cmd_test_unit: ""          # empty = autodetect (escape hatch)
cmd_test_integration: ""
cmd_lint: ""
cmd_vet: ""
model_test_author: sonnet  # per-role model + effort (see Models, effort & agents)
model_implementer: sonnet
model_reviewer: opus
effort_test_author: medium # raised to high on escalation / for L-XL features
effort_implementer: medium
effort_reviewer: high
```

Command detection is a stack-agnostic cascade: settings override → Makefile targets →
`package.json` scripts → language manifests (`go.mod`, `Cargo.toml`, `pyproject.toml`, …) →
Docker probe for the integration tier.

## Quick start (idea → shipped)

The argument every stage takes is the **feature slug** — a kebab-case name you make up once at
the start (here `checkout-discounts`). It becomes the folder every artifact lands in —
`docs/features/checkout-discounts/` — and is how each stage finds the previous stage's files,
so use the **same slug at every stage**.

```text
/sdd:survey                             # once per repo: map the current architecture
/sdd:specify       checkout-discounts   # interview → spec (reads the architecture map)
/sdd:clarify       checkout-discounts
/sdd:design        checkout-discounts
/sdd:sequences     checkout-discounts
/sdd:data-model    checkout-discounts
/sdd:api           checkout-discounts
/sdd:tasks         checkout-discounts
/sdd:plan-tests    checkout-discounts
/sdd:implement     checkout-discounts
/sdd:review        checkout-discounts   # independent review of the whole change
/sdd:ship          checkout-discounts   # verify it runs, changelog, PR
```

> **`/clear` between stages** — each stage is gated, re-reads its inputs from disk, and ends by
> printing the next `/sdd:…` command to copy (the handoff block). Loop-backs (`review` → `implement`)
> stay in context; utilities make `/clear` optional.

Three notes on the first run:

- **You don't need `classify-size` to start** — `specify` classifies the feature and writes
  `.size` itself when it's absent. Run `/sdd:classify-size <slug>` only to size it *before*
  specifying, or to re-classify when scope changes.
- **Skip the depth question** by passing the dial inline: `/sdd:specify checkout-discounts
  --depth=easy` (also on `clarify` / `design`; values `easy|medium|hard` — see
  [Interview depth](#interview-depth-easy--medium--hard)).
- Artifacts land in `docs/features/<slug>/`.

### Fast path (XS)

A small feature doesn't need the full backbone. For XS/S the optional stages are skipped **when
their work doesn't exist** — and the decision is made for you at each handoff: the stage's *Run
next* shows the skip as a `↳ or …` alternative (based on `.size` + the stage's N/A condition),
and you pick it. Example — a config-toggle-sized feature in one session:

```text
/sdd:specify  rate-limit-bump --depth=easy   # spec came out with zero open questions →
                                             #   handoff offers: ↳ or /sdd:design (skip clarify)
/sdd:design   rate-limit-bump                # one actor, no multi-step flow, no schema change →
                                             #   handoff offers: ↳ or /sdd:api — or straight to tasks
/sdd:tasks    rate-limit-bump                # never skipped: implement consumes tasks.json
/sdd:implement rate-limit-bump               # test plan lives inline in spec.md for XS/S
/sdd:review   rate-limit-bump
/sdd:ship     rate-limit-bump
```

The skip conditions (`clarify` — zero open questions; `sequences` — no multi-step flow;
`data-model` — no schema change; `api` — no contract change; `plan-tests` — inline in the spec)
are canonical in [`skills/_shared/size-matrix.md`](./skills/_shared/size-matrix.md) — they're
**N/A conditions, not size defaults**: an XS feature *with* a migration still runs `data-model`.

### When a stage refuses

Stages are gated: each one **hard-refuses when the artifact it consumes is missing** and names the
stage to run first. A refusal is not an error — it's the pipeline telling you which step was
skipped. The ones you're most likely to meet:

| Refusal | What it means | What to do |
|---|---|---|
| `design`: «run `specify` / `glossary` first» | there's no `spec.md` or `CONTEXT.md` for this slug yet (or the slug is spelled differently) | run `/sdd:specify <slug>`; check the slug matches the folder under `docs/features/` |
| `api`: «run `data-model` first» | the contract is derived from the data model's entities — it can't be invented field-by-field | run `/sdd:data-model <slug>` |
| `tasks`: «no Accepted ADR» | `design` spawned no ADR (rare — usually a sign the SAD walk was cut short) | run `/sdd:decide-adr <slug>` for the key decision, or re-run `/sdd:design <slug>` |

## Repository layout

```
.claude-plugin/   plugin.json + marketplace.json (self-marketplace)
.codex-plugin/    Codex CLI plugin manifest (+ .agents/plugins/marketplace.json — its self-marketplace)
.cursor-plugin/   Cursor plugin manifest (skills/ + agents/ auto-discovered from the root)
install.sh        Codex CLI / Cursor installer — copies the subtree, prefixes skill names, generates functional agents
agents/           explorer, test-author, implementer, reviewer, critic, devils-advocate, researcher, strategist, analyst
scripts/          validate_plugin.py (CI gate: manifests + skill/agent frontmatter + the consistency invariants — links resolve, /sdd: form, handoff block, single-source taxonomy, no _shared orphans)
skills/_shared/   canonical socratic-loop / critic / size-matrix / ask-style / interview-depth / diagram-presentation / surfaces / handoff / tool-adapters (referenced, not duplicated)
skills/<name>/    SKILL.md spine + references/ (heavy detail) + templates/ (output scaffolds)
.mcp.json         declares the sdd-dashboard MCP server (auto-starts at session open; opt-in via dashboard_enabled)
server/           the dashboard MCP server (Bun + TypeScript): server.ts (MCP stdio + Bun.serve HTTP/WS), state.ts (disk→pipeline derivation), channel.ts (dashboard_* tools + command allowlist), paths.ts (docs/ scoping)
dashboard/        the browser UI (vanilla JS, terminal-green): index.html + app.js + style.css + vendor/ (marked, mermaid, redoc — vendored, offline)
```

## Roadmap

Directions under consideration — not promises, no dates:

- **`sync`** — spec↔code drift detection: re-derive what the code actually does and diff it
  against the spec/SAD, so long-lived features don't quietly outgrow their documents.
- **Traceability matrix + adherence score** — `review`/`ship` emit a single AC × (flow / contract
  / task / test / commit) matrix with a coverage score, instead of prose-only tracing.
- **Tracker integration** — `tasks.json` ⇄ Jira / Linear / GitHub Issues two-way sync (today the
  export is one-shot and copy-paste).
- **Constitution file** — a repo-level set of inviolable rules (security, compliance, style) every
  stage reads and the validator enforces, complementing the per-feature artifacts.

**Shipped:** ~~MCP exposure~~ → see **[The visual dashboard](#the-visual-dashboard-opt-in)** below.

## The visual dashboard (opt-in)

The roadmap's *"MCP exposure — pipeline state served over MCP so external tools and dashboards can read
where every feature stands"* has shipped — and gained a control surface. The plugin now carries an
**`sdd-dashboard` MCP server** (`server/`, Bun + TypeScript) that auto-starts at session open and, when
enabled, serves a **local browser dashboard** (`dashboard/`) on `127.0.0.1`. It:

- **Reads** every feature off disk (`docs/features/<slug>/`) and shows its pipeline as a per-step
  checklist — `done` / `skipped` / `pending` / `blocked` — derived from the artifacts present (so an XS
  feature shows *skipped* stages, not gaps). It renders each artifact: markdown, **mermaid** C4 / sequence
  / ER diagrams, and **OpenAPI** (redoc) — all from **vendored** libs (offline, no CDN).
- **Edits** artifact text back to disk — scoped to `docs/`, atomic `tmp+rename`, with optimistic-concurrency
  `409` on a stale edit.
- **Drives the pipeline** — clicking *Run next stage* / *Create feature* sends a validated
  `/sdd:<skill> <slug>` command **back into this live session** over the same channel mechanism the official
  Telegram plugin uses (`notifications/claude/channel`). Claude runs the skill and streams progress + the
  handoff back to the browser. The dashboard is a **driver + observer**, not a synchronous remote: a click
  is consumed only while the session is idle at the prompt — otherwise it **queues** (shown honestly in the UI).

**Opt-in, two prerequisites.** It does nothing unless you ask for it:

1. Install **[Bun](https://bun.sh)** (the server runtime — the same dependency the Telegram plugin uses).
2. Set `dashboard_enabled: true` in `.claude/sdd.local.md` (see [Configuration](#configuration--claudesddlocalmd)).
3. Run **`/sdd:start`** — it hands the server your project dir, confirms the channel, and prints the URL
   (`http://127.0.0.1:<port>/?session=<id>&token=<cap>`). Pure-markdown users who skip this are unaffected.

**Setup, usage, config & troubleshooting:** [`server/README.md`](./server/README.md).

**Security:** binds loopback only; reads/writes are realpath-contained to `docs/` with an extension
allowlist; mutating routes require a per-session capability token; inbound commands are built **only** from
a server-side skill + slug allowlist (browser text never becomes an arbitrary `/sdd:` command).

## License

MIT © Kyrylo Genkov. See [LICENSE](./LICENSE).
