---
name: implement
model: inherit
effort: medium
agents: [test-author, implementer, reviewer]
description: >
  Use to implement a feature from its tasks.json with test-driven development — writes a failing
  test first, makes it pass, refactors, gates, and commits per task. Triggers on "implement {slug}",
  "build {slug}", "TDD {slug}", "code up the tasks for {slug}", "/sdd-implement {slug}",
  "імплементуй {slug}", "реалізуй фічу {slug}", "напиши код за задачами". Reads
  docs/features/{slug}/tasks.json + the upstream artifacts, detects the repo's test/lint/vet
  commands stack-agnostically, builds a dependency DAG, and runs one of three modes — sequential
  single-agent TDD, an agent team (TeamCreate), or a dynamic Workflow — chosen from settings +
  DAG shape with graceful fallback. Hard-refuses if tasks.json is missing.
---

# Skill: implement

The implementation engine. It turns `tasks.json` into committed, tested code through a strict TDD cycle per task — `SELECT → RED → GREEN → REFACTOR → GATE → COMMIT` — and orchestrates that cycle in one of three modes (sequential / agent-team / dynamic-workflow) picked by an unambiguous decision tree. Everything is stack-agnostic: the test, lint, and vet commands are **detected**, never hard-coded.

This file is the spine. Each step delegates to a file in `references/`.

## Owner

Tech Lead drives; the engine runs the cycle. The three subagents ship with the plugin: [`test-author`](../../agents/test-author.md) (RED), [`implementer`](../../agents/implementer.md) (GREEN/REFACTOR/GATE), [`reviewer`](../../agents/reviewer.md) (read-only review).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** `docs/features/<slug>/tasks.json`. Missing → «run `tasks <slug>` first».
- Read for context (the agents read these directly, not via paraphrase): `spec.md` (AC), `data-model.md` + the **staged** migrations under `docs/features/<slug>/migrations/` (a `layer: migration` task **promotes** these into the live `migrations/` tree — see [`./references/inputs.md`](./references/inputs.md)), `contracts/openapi.yaml`, `test-plan.md`, `sad.md`, Accepted `adr/`.
- Settings: `.claude/sdd.local.md` (lazy-created with defaults on first run) → [`./references/settings.md`](./references/settings.md).

## Protocol (10 steps)

1. **Preconditions.** Verify `tasks.json` exists and parses; load the upstream artifacts list. Detail → [`./references/inputs.md`](./references/inputs.md).
2. **Settings.** Read `.claude/sdd.local.md`; if absent, lazy-create it with the documented defaults and patch `.gitignore` (`.claude/*.local.md`, `.worktrees/`). → [`./references/settings.md`](./references/settings.md).
3. **Detect commands.** Run the stack-agnostic cascade (settings override → Makefile → package scripts → language manifests → Docker probe for the integration tier) to resolve unit / integration / lint / vet commands. Print what was detected. → [`./references/command-detection.md`](./references/command-detection.md).
4. **Build the DAG.** Parse `tasks.json`, validate `deps` is acyclic, topologically sort into phases (Kahn). Compute `task_count`, `longest_chain`, `parallel_width`. Mark serialization lanes (`layer: migration`; tasks with overlapping `files_hint`).
5. **Pick the mode.** Run the decision tree (below; full form → [`./references/decision-tree.md`](./references/decision-tree.md)). Apply the guards.
6. **Generate the run-plan.** Sequential → an ordered task list. Team → a shared TaskList with the full task text in each body. Workflow → a generated `Workflow` script (DAG → Kahn phases → fan-out pipeline). → [`./references/team-exec.md`](./references/team-exec.md) / [`./references/workflow-exec.md`](./references/workflow-exec.md).
7. **Banner.** Print the active mode and the settings that drove it: `mode=<…> tdd=<…> isolation=<…> parallel=<n> integration=<…>`. The user sees exactly how the engine will behave before it acts.
8. **Execute** in the chosen mode. Every task runs the TDD cycle → [`./references/tdd-loop.md`](./references/tdd-loop.md). A `layer: migration` task first **promotes** its staged migration(s) (`docs/features/<slug>/migrations/<NN>_*`) into the live `migrations/` tree — assigning the real sequence number / timestamp per the repo's convention, in ordinal order — *then* applies + reverts them; detail → [`./references/inputs.md`](./references/inputs.md).
9. **Per-task gate + commit.** After GREEN+REFACTOR: unit + (integration if available) + lint + vet must be clean, then commit task-scoped with trailers `SDD-Task: <id>` and `SDD-AC: <id>` (one per satisfied AC). Update `tracker.md` → `done`.
10. **Summary + hand off.** Report covered AC, commits made (with `SDD-Task` trailers), any task dropped/blocked, and the per-task gate results. Then hand off to the independent review gate: **next is `review <slug>`** (a clean-context pass over the whole diff), then `ship <slug>`. In team mode the [`reviewer`](../../agents/reviewer.md) may also run per-task, but the authoritative independent review of the whole change lives in the `review` skill — `implement` does not self-certify.

## Decision tree (compact)

```
parallel_eligible := isolation==worktree AND max_parallel>1 AND parallel_width>=2
                     AND (size in {M,L,XL} OR task_count>=4)

if team_mode AND parallel_eligible:                          → AGENT TEAM (TeamCreate) over the DAG
elif workflow_mode=="auto" AND parallel_eligible AND Workflow-available: → DYNAMIC WORKFLOW
else:                                                        → SEQUENTIAL single-agent TDD (topo order)
```

**Guards (apply before dispatch):** `team_mode` but not eligible → warn + downgrade to the next mode. `max_parallel>1` with `isolation: inplace` → clamp parallel to 1 (no two agents edit one tree). `workflow_mode: off` → never generate a Workflow. `tdd: false` → skip RED (warn loudly — you lose the safety net). `require_integration: always` but Docker absent → **BLOCK** before dispatch; `auto` → run unit-only and mark integration NON-red; `never` → skip the integration tier. Full table → [`./references/decision-tree.md`](./references/decision-tree.md). Graceful degrade: if `Workflow`/`TeamCreate` is unavailable at runtime, fall through to sequential.

## TDD cycle (per task)

`SELECT → RED → GREEN → REFACTOR → GATE → COMMIT`. The RED step is load-bearing: write the test first, run it, and **classify the first run** — GOOD red (assertion fails / unimplemented) vs BAD red (the test itself won't compile → fix the test) vs false-pass (green immediately → the test is too weak, strengthen it) vs NON-red (skipped because Docker is absent → governed by `require_integration`, counts as neither red nor green). Quote the failing line before writing any production code. Escalation on persistent red → [`./references/escalation.md`](./references/escalation.md): more-capable model → retry → split the task → if the test encodes a wrong AC, **ask a human** (never weaken the test) → rollback to the last green. `stop_on_red` decides halt vs drop-and-continue (dependents auto-block).

## Definition of Done

- Every task in `tasks.json` is either committed (test-first, gate-clean, `SDD-Task`/`SDD-AC` trailers) or explicitly reported as dropped/blocked with the reason.
- Unit gate green; integration green where available (or NON-red recorded with the policy reason); lint + vet clean per the detected commands.
- The active mode + settings were printed in the banner before execution.
- `tracker.md` reflects final status; the summary reports the gate results and hands off to `review` (the independent review gate) — `implement` does not self-certify the whole change.

## Anti-patterns

- **Code before the test.** RED first, always (unless `tdd: false`, which warns).
- **Weakening a test to make it pass.** If the AC is wrong, ask a human and fix the AC; never edit the test to be less strict.
- **Skipping the RED classification.** A false-pass that looks green hides a useless test.
- **Parallel agents editing one working tree.** Parallelism requires worktree isolation — the guard clamps it.
- **Committing with a red or skipped gate** and calling it done. A NON-red integration tier must be labelled, not hidden.
- **Spawning a team for <4 tasks** — coordination overhead exceeds the gain; the eligibility check forbids it.
- **Claiming integration passed when Docker was absent.** Report NON-red honestly.

## References

`inputs.md` · `settings.md` · `command-detection.md` · `decision-tree.md` · `tdd-loop.md` · `team-exec.md` · `workflow-exec.md` · `escalation.md` — all in [`./references/`](./references/).
