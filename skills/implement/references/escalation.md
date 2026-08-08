# Escalation — when RED won't go GREEN

A test that stays red after a normal GREEN attempt is a signal, not a nuisance. Climb this ladder in order; never short-circuit it by weakening the test.

## The ladder (in order)

1. **Re-attempt** up to `max_red_retries` times. Re-read the failing line, the task `acs`, and the relevant `data-model` / `openapi` / `adr`. Often the GREEN missed a detail the contract already specifies.
2. **More-capable model.** If retries stall, re-dispatch the GREEN step on a stronger model (raise `model_implementer` for this task — a stronger tier when the account has one; otherwise raise effort on the same model). A harder task sometimes just needs more capability.
3. **Split the task.** If the task turns out to bundle two concerns (e.g. a validation rule *and* an audit write), split it into two with a dep edge, and drive each with its own RED. Update `tasks.json` + `tracker.md` so the DAG stays the source of truth.
4. **Ask a human — the test may encode a wrong AC.** If the code is right and the *test* asserts something the AC doesn't actually require (or the AC itself is wrong), STOP and ask. Surface: the failing line, the AC text, and why they conflict. **Never** edit the test to be less strict to make a wrong AC pass — fixing the AC is a `specify`/`clarify` change with the human in the loop.
5. **Rollback to the last green.** If none of the above resolves it, revert this task's working changes to the last green commit so the tree is never left broken.

## `stop_on_red` decides what happens to the rest

After the ladder is exhausted on a task:

- **`stop_on_red: true`** (default) → halt the run. Report the blocked task, the failing line, and where in the ladder it stalled. Nothing half-done is committed.
- **`stop_on_red: false`** → drop this task, **auto-block its transitive dependents** (their deps will never complete), and continue the independent branches. The final summary lists every dropped + blocked task with the reason.

## Never

- **Never weaken a test** to get green. The test is the spec made executable; if it's wrong, that's a human decision (step 4).
- **Never commit a red or a skipped hard-gate** as "done". A NON-red integration tier is labelled, not hidden.
- **Never leave the tree broken.** Rollback (step 5) is the floor.
