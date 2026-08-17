---
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
judgment_model: sonnet     # tier alias (haiku|sonnet|opus|fable), inherit, or a full model id — one switch for ALL judgment agents; sonnet = supported path without Opus access
effort_test_author: medium    # per-role effort; raised to high on escalation
effort_implementer: medium
effort_reviewer: high
---

Per-project SDD settings. Full key documentation lives in the plugin's
`skills/implement/references/settings.md`.
