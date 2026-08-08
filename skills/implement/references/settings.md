# Settings — `.claude/sdd.local.md` (step 2)

The engine is configured per-project by a plugin-settings file with YAML frontmatter. On first run, **lazy-create** it with the defaults below and tell the user where it is; on later runs, read it.

> **Plugin-wide, not implement-only.** Most keys below configure the `implement` engine, but a few are read by **other skills too**. `interview_depth` is read by the Q&A skills (`specify` / `clarify` / `design`) to pre-select the depth dial. `artifact_language` is read by **every artifact-writing skill** — it sets the language pipeline documents are written in (prose only; structure stays English → [`../../_shared/artifact-language.md`](../../_shared/artifact-language.md)). The file is **auto-created with documented defaults the first time any skill needs it** — normally `specify` at the start of the backbone — so the rest of the pipeline finds a real file instead of silently falling back. If for any reason it's still missing, a reader falls back to its own default (medium): there is **no hard ordering dependency** on `implement` having run first.

## Auto-create when absent

Created **automatically** the first time a skill needs it — normally `specify` at the start of the backbone (it ensures the file alongside establishing `.size`), or `implement` if you jump straight to it. **Idempotent:** if the file already exists it is read, never overwritten.

1. If `.claude/sdd.local.md` is absent, write it with **the documented frontmatter below, followed by the «What each key does» section as the file's markdown body** — so the file is self-documenting: every key carries its default, its allowed values, and a plain explanation inline, with no need to open the plugin docs.
2. **Patch `.gitignore`** (create it if absent) to include `.claude/*.local.md` and `.worktrees/` — these are per-developer and must not be committed. (The `.claude/*.local.md` glob already covers `sdd.local.md`; don't add a redundant explicit line.)
3. Tell the user: «Wrote `.claude/sdd.local.md` with documented defaults — edit it to change how the pipeline behaves.»

## The documented frontmatter

<!-- This block is written verbatim to the top of `.claude/sdd.local.md`; the «What each key does»
     section below becomes the file's body. Keep the inline comments — they list the allowed values. -->

```yaml
interview_depth: medium    # easy | medium | hard — plugin-wide default for specify/clarify/design (see _shared/interview-depth.md)
artifact_language: en      # en | uk (any language tag) — language pipeline DOCUMENTS are written in; headings + machine tokens stay English (see _shared/artifact-language.md)
tdd: true                  # enforce red→green→refactor
team_mode: false           # true → agent team via TeamCreate
workflow_mode: auto        # auto → dynamic Workflow; off → never
max_parallel_agents: 3     # integer ≥1 — fan-out cap for team/workflow modes (1 = sequential)
isolation: worktree        # worktree | inplace (parallel>1 ⇒ forces worktree)
stop_on_red: true          # halt on a red that survives escalation, vs drop-and-continue
max_red_retries: 3         # integer ≥1 — RED→GREEN attempts before escalation
gate_lint: true            # true | false — include lint in the per-task gate
gate_vet: true             # true | false — include vet / static-analysis in the per-task gate
require_integration: auto  # auto | always | never (Docker-probed)
auto_commit: per_task      # per_task | per_phase | off
branch_strategy: feature   # feature | current
cmd_test_unit: ""          # empty = autodetect (escape hatch)
cmd_test_integration: ""
cmd_lint: ""
cmd_vet: ""
model_test_author: sonnet     # per-role model (see _shared/agent-roster.md); inherit = session model
model_implementer: sonnet
model_reviewer: opus
judgment_model: opus       # tier alias (haiku|sonnet|opus|fable), inherit, or a full model id — one switch for ALL judgment agents (reviewer/critic/devils-advocate/strategist/analyst); sonnet = supported path without Opus access; an explicit value always wins over the floor default; per-role model_<role> wins for its role
effort_test_author: medium    # per-role effort; raised to high on escalation
effort_implementer: medium
effort_reviewer: high
dashboard_enabled: false   # true → opt into the SDD visual dashboard (the sdd-dashboard MCP server + browser UI); see skills/start
dashboard_port: 4178       # integer — loopback port the dashboard binds (scans upward if busy); read by the server
```

## What each key does

- **`interview_depth`** — `easy | medium | hard`. The plugin-wide default for the **Q&A skills'** depth dial (`specify` / `clarify` / `design`), which governs how much each skill decides on its own vs. interrogates you (question volume, autonomy, which ideation analyses run, per-diagram confirm vs. proceed). It only **pre-selects** the recommended option in each skill's opening depth question — the user can still override per run, or pass `--depth=` to skip the question. It does **not** affect AC-completeness (that's a floor at every level). Full semantics → [`../../_shared/interview-depth.md`](../../_shared/interview-depth.md). (Not read by the `implement` engine itself.)
- **`artifact_language`** — `en | uk` (any language tag; default `en`). The language **pipeline documents** are written in — read by **every artifact-writing skill** (spec, SAD, ADRs, sequences, data-model, contracts, tasks, test plan, review/fix records, changelog, roadmap, CONTEXT.md), not by the `implement` engine. Only **prose** switches (paragraphs, table cells, diagram labels, the prose fields of `tasks.json` / `openapi.yaml`); **structure stays English** — section headings verbatim from the template, frontmatter keys+values, verdict literals, tracker states, Mermaid keywords, machine fields. Precedence when editing: an existing file's language wins over the setting, a new file matches its feature-folder neighbours, never retro-translate. Full rule + the never-translate token list → [`../../_shared/artifact-language.md`](../../_shared/artifact-language.md).
- **`tdd`** — when false, RED is skipped and the engine writes code directly (warns; you lose the safety net).
- **`team_mode` / `workflow_mode`** — feed the decision tree (see [`decision-tree.md`](./decision-tree.md)). `team_mode` wins when both could apply.
- **`max_parallel_agents`** — fan-out cap for team/workflow modes. `1` forces sequential.
- **`isolation`** — `worktree` gives each parallel agent its own git worktree under `.worktrees/`; `inplace` edits the checkout directly and **forces parallelism to 1**.
- **`stop_on_red`** — `true`: a red that survives escalation halts the run. `false`: drop that task, auto-block its dependents, continue other branches.
- **`max_red_retries`** — RED→GREEN attempts before escalation (see [`escalation.md`](./escalation.md)).
- **`gate_lint` / `gate_vet`** — include lint / vet in the per-task gate (skipped gracefully if no command is detected — see [`command-detection.md`](./command-detection.md)).
- **`require_integration`** — `auto`: run integration tests if a Docker daemon answers, else mark NON-red; `always`: BLOCK before dispatch if Docker is absent; `never`: skip the integration tier entirely.
- **`auto_commit`** — `per_task` (default), `per_phase`, or `off` (leave commits to the user).
- **`branch_strategy`** — `feature`: ensure work is on a feature branch (create one if on the default branch); `current`: commit on the current branch.
- **`cmd_*`** — explicit command overrides; non-empty values short-circuit detection (the escape hatch for unusual repos).
- **`dashboard_enabled`** — `true | false` (default `false`). Opt into the **SDD visual dashboard**: the `sdd-dashboard` MCP server (auto-started from `.mcp.json`) binds a loopback HTTP+WS listener and serves the read-only browser UI that shows every feature's pipeline stage, renders its artifacts, and drives the pipeline by sending `/sdd:<skill> <slug>` commands back into the live session. When `false` (or absent), the server stays idle — the markdown skills are unaffected. Run `/sdd:start` after enabling. Needs **Bun** installed. (Not read by the `implement` engine — read by the dashboard server + the `start` skill.)
- **`dashboard_port`** — integer (default `4178`). The loopback port the dashboard binds; if busy the server scans upward (`4178..4189`) and `/sdd:start` prints the actual port. Only `127.0.0.1` is ever bound; mutating routes require the per-session capability token issued by `/sdd:start`.
- **`model_*` / `effort_*`** — per-role model + effort for the three agents, applied when the engine spawns them (it overrides the agent's frontmatter default). Roster defaults + rationale → [`../../_shared/agent-roster.md`](../../_shared/agent-roster.md). Precedence: env var > this setting > agent frontmatter > session.
- **`judgment_model`** — a tier alias (`haiku|sonnet|opus|fable`), `inherit` (the session model), or a full model id; default `opus`. One switch for **all judgment agents** — `reviewer` / `critic` / `devils-advocate` / `strategist` / `analyst` — set in one place without touching `agents/*.md`: `sonnet` is the supported path for accounts without Opus access; `fable` raises the five to the Fable tier. **The default is a floor, not a pin** — when the key is unset and the session runs a stronger tier than `opus`, judgment agents dispatch with `inherit` (never silently downgrade judgment below the session); an explicit value is always honored literally. If the chosen model turns out unavailable to the account, degrade per the roster rule (retry once on `inherit` — never block); the floor + degrade rules are canonical in [`../../_shared/agent-roster.md`](../../_shared/agent-roster.md). A per-role `model_<role>` key still wins for its role. Full precedence (highest wins): `env > invocation > model_<role> > judgment_model > frontmatter > session`. Execution agents (`test-author` / `implementer`) and `explorer` / `researcher` are unaffected.
  - **Env path:** the engine also exports `CLAUDE_CODE_EFFORT_LEVEL` / `CLAUDE_CODE_SUBAGENT_MODEL` for the dispatch when these keys are set — the reliable lever (see [`agent-roster.md`](../../_shared/agent-roster.md) for why frontmatter alone may not suffice).
  - **`.size` scaling:** the engine raises the default effort for **L/XL** features (execution agents → `high`) before dispatch, and keeps the cheap defaults for **XS/S** — a cross-module change is where reasoning depth pays off. It prints the resolved per-role model+effort in the banner.

## Reading semantics

Unknown keys are ignored (forward-compatible). A missing key falls back to the default above. A malformed file → warn and fall back to all-defaults rather than failing the run.
