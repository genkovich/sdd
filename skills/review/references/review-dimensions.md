# Review dimensions + dispatch

The independent review (step 2) probes the feature diff along these dimensions. For a small change, one [`reviewer`](../../../agents/reviewer.md) pass covers them all; for a large diff, fan out one reviewer per dimension and merge findings.

## Stage 1 — does it do what the spec says (the gate that can block ship)

- **AC compliance.** For every AC the change claims (the `SDD-AC` trailers / `tasks.json` `acs`): does the code actually produce the business-observable outcome the AC names, and is there a test that asserts *that outcome* (not a tautology)?
- **Coverage.** Is any in-scope AC silently uncovered? Cross-check spec §5 against the diff.
- **Contract fidelity.** Does the change honour `data-model.md`, `contracts/openapi.yaml`, and the Accepted ADRs (e.g. the audit-in-transaction decision), or does it quietly diverge?

A stage-1 finding means the feature does not yet meet its spec — it blocks ship until fixed or explicitly de-scoped (a spec change with the owner in the loop).

## Stage 2 — is it good code (quality, usually non-blocking)

- **Conventions.** Matches the repo's patterns for each layer (error handling, wiring, naming, module boundaries).
- **Error + edge handling.** Are the spec's error / authorization / invariant criteria handled, not just the happy path? Concurrency, empty/oversized input, idempotency where the contract requires it.
- **Security.** Identity from the session not from input; no new injection/leak surface; secrets not logged.
- **Boundary violations.** Stayed inside the module(s) the tasks named; no weakened test; no forbidden DB construct vs the repo's migration rules.
- **Test adequacy.** Do the tests exercise the real behaviour, including the failure paths — or only the happy path?

## Dispatch shape

Reuse the clean-context discipline from [`../../_shared/critic.md`](../../_shared/critic.md): the reviewer has read-only tools, re-reads `spec.md` / contracts / ADRs itself, and emits **cited** findings only:

```
- **[stage-N] <headline>** — file:line; AC: <id|n/a>; problem: <what>; suggested: <fix>.
```

A clean review returns `REVIEW_CLEAN: <scope>`. Drop any finding without a `file:line` + a concrete reason — it isn't actionable. Prioritise correctness and AC-compliance over style; judge against the artifacts, not personal taste (if the spec says hide-existence, a 404-style response is correct, not a bug).
