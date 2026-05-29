# Dynamic-workflow execution (`workflow_mode: auto`)

When the decision tree selects the workflow, the engine **generates a `Workflow` script** from the DAG and runs it. This is the unattended, maximally-parallel mode: each independent task flows through its own pipeline, and a failure drops only that task's subtree while other branches keep going.

## Why a generated workflow (not a fixed one)

The shape of the work is `tasks.json` — different every feature. So the engine emits a script tailored to this DAG: validate → layer → fan-out → per-task pipeline. The script is data-driven from the tasks array; the engine fills it in and invokes `Workflow`.

## Generated script shape

```js
export const meta = {
  name: 'sdd-implement-<slug>',
  description: 'TDD-implement <slug> from tasks.json (dynamic DAG)',
  phases: [{ title: 'Implement' }, { title: 'Review' }],
}

// tasks + deps are inlined from tasks.json by the engine
const TASKS = /* [{id, title, acs, dod, files_hint, deps, layer}, ...] */;

// Kahn layers → phases; within a layer, fan out up to the parallel cap.
// Each task is one independent pipeline: write-test → implement → verify → [review] → commit.
const done = new Set();
for (const layer of kahnLayers(TASKS)) {              // computed from deps
  await parallel(layer.map(t => () =>
    pipeline([t],
      () => agent(redPrompt(t),     { phase:'Implement', label:`red:${t.id}`,   schema: RED_VERDICT }),
      r  => agent(greenPrompt(t,r), { phase:'Implement', label:`green:${t.id}`, schema: GATE_VERDICT }),
      g  => agent(verifyPrompt(t,g),{ phase:'Implement', label:`verify:${t.id}`,schema: GATE_VERDICT }),
      v  => agent(reviewPrompt(t,v),{ phase:'Review',    label:`review:${t.id}`,schema: REVIEW_VERDICT }),
    ).then(res => { if (res?.gate_green) done.add(t.id); return {t, res}; })
  ))
}
```

- **Schema-validated verdicts.** Each stage returns a structured verdict (`RED_VERDICT { class: GOOD|BAD|false_pass|NON, failing_line }`, `GATE_VERDICT { unit, integration, lint, vet, gate_green }`, `REVIEW_VERDICT { ac_satisfied, issues[] }`) so the orchestrator branches on data, not prose.
- **Fail drops the subtree.** A stage that throws (or returns `gate_green: false` past retries) drops that task to `null`; the engine removes it from `done`, so every transitively-dependent task is skipped (its deps never complete). Independent branches finish unaffected — this is the workflow's advantage over a team halt.
- **Parallel cap.** `parallel(...)` respects `max_parallel_agents` (the workflow runtime also caps concurrency); a wide layer queues the overflow.

## Serialization inside the workflow

The same lanes as the team apply: `layer: migration` tasks are forced into a single ordered sub-sequence (don't place two migrations in the same parallel layer — chain them via synthetic deps before computing Kahn layers), and tasks with overlapping `files_hint` get a synthetic dep so they never land in the same parallel batch. Each migration task **promotes** its staged `docs/features/<slug>/migrations/<NN>_*` file into the live `migrations/` (next free number, in ordinal order) before applying it — see [`./inputs.md`](./inputs.md).

## Commit + integration

- Commits are produced by the `commit` step of each pipeline (or batched by the engine after the workflow returns, if `auto_commit: per_phase`), with `SDD-Task`/`SDD-AC` trailers, serialized in dependency order.
- Integration tier follows `require_integration`: in CI (Docker present) the integration RED→GREEN runs inside the verify stage; locally under `auto` with no Docker it's NON-red and the proving run relies on CI for the integration green.

## Graceful fallback

If the `Workflow` tool is **not available** at runtime, this whole mode is skipped by the decision-tree guard — the engine falls through to the team (if eligible) or to sequential single-agent TDD. The generated script is never a hard dependency.
