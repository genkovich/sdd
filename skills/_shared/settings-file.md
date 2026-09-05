# The settings file — `.claude/sdd.local.md` (the one canonical template + procedure)

> **Reference-only.** Not a skill. Every skill that ensures, reads or edits the per-project
> settings file reads this. The template below is written **verbatim** — the frontmatter to the
> top of the file, the «What each key does» section as its body — so the file explains itself
> without opening the plugin docs. The engine-side delta (which keys `implement` actually reads,
> model precedence, `.size` scaling) stays in
> [`../implement/references/settings.md`](../implement/references/settings.md).

## TL;DR (короткий вступ українською)

`.claude/sdd.local.md` — це per-project файл налаштувань пайплайна. Він **завжди створюється з
задокументованими дефолтами** першим кроком шести скілів пайплайна (`interview`, `survey`,
`roadmap`, `scaffold`, `specify`, `implement`) і самого `config`, тому людина отримує робочий
конфіг ще до першого питання. У скіла з власним гейтом крок іде одразу після гейта, щоб відмова
нічого не писала. Створення безумовне й ідемпотентне: файл є — читаємо, ніколи не перезаписуємо.

**Значення міняє тільки [`config`](../config/SKILL.md)** (`/sdd:config`). Решта скілів файл
створює і читає, але ніколи не пропонує щось у ньому крутити. Файл gitignored — комітиться лише
правка `.gitignore`.

## Who creates it, who changes it, who reads it

| Role | Who | What they do with it |
|---|---|---|
| **Create** (unconditional, idempotent) | the six pipeline skills — `interview` · `survey` · `roadmap` · `scaffold` · `specify` · `implement` — **and `config` itself** | first protocol step: absent → write the template below + patch `.gitignore`; present → read, never overwrite. `interview` is subordinate to its own write gate — outside a git repo it writes nothing, settings included. |
| **Change values** (the only writer of existing keys) | [`config`](../config/SKILL.md) | asks, then patches confirmed keys in place. No other skill ever offers to tune a value. |
| **Read** `interview_depth` | `specify` · `clarify` · `design` · `sequences` · `ux-flows` | pre-selects the depth dial → [`interview-depth.md`](./interview-depth.md) |
| **Read** `artifact_language` | every artifact-writing skill | the prose language of pipeline documents → [`artifact-language.md`](./artifact-language.md) |
| **Read** `judgment_model` / `model_<role>` / `effort_<role>` | every skill that dispatches an agent | the tier each agent runs at → [`agent-roster.md`](./agent-roster.md) |
| **Read** the engine keys (`tdd`, `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation`, `stop_on_red`, `max_red_retries`, `gate_*`, `require_integration`, `auto_commit`, `branch_strategy`, `cmd_*`) | `implement` (`cmd_*` + gates also `fix`) | → [`../implement/references/settings.md`](../implement/references/settings.md) |

## Create when absent (the procedure)

Run this **first thing in the skill's protocol, after that skill's own gate** — `interview` resolves
its write gate first (outside a repo it writes nothing), `scaffold` clears its hard refuse and
`implement` its preconditions first, so a refusal leaves the repo untouched; the skills with no
preceding gate simply run it first. It is unconditional — a settings file the user never asked for
is strictly better than a stage that discovers it is missing three commands later — and idempotent.

1. **`.claude/sdd.local.md` exists?** → read it and stop here. **Never** overwrite, never
   regenerate it from this template, never «refresh» it because a key looks stale.
2. **Absent** → write it: the documented frontmatter below at the top, then the «What each key
   does» section as the file's markdown body. Keep the inline comments — they carry the allowed
   values, which is what makes the file self-documenting.
3. **Patch `.gitignore`** (create it if absent) so it contains `.claude/*.local.md` and
   `.worktrees/` — both are per-developer and must never be committed. The `.claude/*.local.md`
   glob already covers `sdd.local.md`; don't add a redundant explicit line, and don't duplicate a
   line that is already there.
4. **Say one line** and move on — no question, no menu:
   «`.claude/sdd.local.md` created with documented defaults — `/sdd:config` to tune it».
   Substitute the host's own invocation form when you're not in Claude Code (`$sdd-config` under
   Codex CLI, `sdd-config` from Cursor's `/` menu) → [`tool-adapters.md`](./tool-adapters.md).

The settings file itself is **never committed** (it's gitignored). The `.gitignore` patch is, and
rides along in whatever commit the stage proposes.

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
```

## What each key does

- **`interview_depth`** — `easy | medium | hard`. The plugin-wide default for the **Q&A skills'** depth dial (`specify` / `clarify` / `design`), which governs how much each skill decides on its own vs. interrogates you (question volume, autonomy, which ideation analyses run, per-diagram confirm vs. proceed). It only **pre-selects** the recommended option in each skill's opening depth question — the user can still override per run, or pass `--depth=` to skip the question. It does **not** affect AC-completeness (that's a floor at every level). Full semantics → `skills/_shared/interview-depth.md`.
- **`artifact_language`** — `en | uk` (any language tag; default `en`). The language **pipeline documents** are written in — read by **every artifact-writing skill** (spec, SAD, ADRs, sequences, data-model, contracts, tasks, test plan, review/fix records, changelog, roadmap, CONTEXT.md). Only **prose** switches (paragraphs, table cells, diagram labels, the prose fields of `tasks.json` / `openapi.yaml`); **structure stays English** — section headings verbatim from the template, frontmatter keys+values, verdict literals, tracker states, Mermaid keywords, machine fields. Precedence when editing: an existing file's language wins over the setting, a new file matches its feature-folder neighbours, never retro-translate. Full rule + the never-translate token list → `skills/_shared/artifact-language.md`.
- **`tdd`** — when false, RED is skipped and the engine writes code directly (warns; you lose the safety net).
- **`team_mode` / `workflow_mode`** — feed the `implement` decision tree. `team_mode` wins when both could apply. Both need Claude Code (`TeamCreate` / `Workflow`); on Codex CLI and Cursor they degrade to sequential → `skills/_shared/tool-adapters.md`.
- **`max_parallel_agents`** — fan-out cap for team/workflow modes. `1` forces sequential.
- **`isolation`** — `worktree` gives each parallel agent its own git worktree under `.worktrees/`; `inplace` edits the checkout directly and **forces parallelism to 1**.
- **`stop_on_red`** — `true`: a red that survives escalation halts the run. `false`: drop that task, auto-block its dependents, continue other branches.
- **`max_red_retries`** — RED→GREEN attempts before escalation.
- **`gate_lint` / `gate_vet`** — include lint / vet in the per-task gate (skipped gracefully if no command is detected).
- **`require_integration`** — `auto`: run integration tests if a Docker daemon answers, else mark NON-red; `always`: BLOCK before dispatch if Docker is absent; `never`: skip the integration tier entirely.
- **`auto_commit`** — `per_task` (default), `per_phase`, or `off` (leave commits to the user).
- **`branch_strategy`** — `feature`: ensure work is on a feature branch (create one if on the default branch); `current`: commit on the current branch.
- **`cmd_*`** — explicit command overrides; non-empty values short-circuit detection (the escape hatch for unusual repos). **Empty is the better default** — the detection cascade reads the repo's own Makefile / package scripts / language manifests, so a pinned command is one more thing to keep in sync.
- **`model_*` / `effort_*`** — per-role model + effort for the three execution agents, applied when the engine spawns them (it overrides the agent's frontmatter default). Roster defaults + rationale → `skills/_shared/agent-roster.md`.
- **`judgment_model`** — a tier alias (`haiku|sonnet|opus|fable`), `inherit` (the session model), or a full model id; default `opus`. One switch for **all judgment agents** — `reviewer` / `critic` / `devils-advocate` / `strategist` / `analyst` — set in one place without touching `agents/*.md`: `sonnet` is the supported path for accounts without Opus access; `fable` raises the five to the Fable tier. **The default is a floor, not a pin** — when the key is unset and the session runs a stronger tier than `opus`, judgment agents dispatch with `inherit`; an explicit value is always honored literally. A per-role `model_<role>` key still wins for its role. Full precedence + the degrade rule → `skills/_shared/agent-roster.md`.

## Editing an existing file (only `config` does this)

The file is the user's. It carries their edits, their comments, and possibly keys this version of
the plugin has never heard of. So:

- **Patch key by key.** Rewrite only the lines whose values the user just confirmed. Never
  regenerate the file from the template — that is how a hand-written comment or a hand-added key
  silently disappears.
- **Preserve comments, key order, and unknown keys** exactly as they are. An unknown key is a
  forward-compatibility feature, not garbage to clean up.
- **Write each value in its documented form** — bare `off`, not `"off"`; bare `3`, not `"3"`. The
  template above is the reference spelling; a re-quoted value reads as a different setting on the
  next diff.
- **Show `old → new`** for every key you touch, and separately name anything that was **derived
  rather than asked** (a host clamp, an autodetect left empty) — a value the user didn't choose
  must never appear as if they had.
- **A malformed frontmatter is never fixed silently.** Show what failed to parse and offer the
  choice: rewrite from the template (stating what will be lost) or stop and let the user fix it
  by hand.

## Reading semantics

Unknown keys are ignored (forward-compatible). A missing key falls back to the default above. A
malformed file → warn and fall back to all-defaults rather than failing the run; a **reader** never
rewrites the file to repair it.
