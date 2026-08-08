# Rubric — clarify-judgment-sonnet

The fixture's `.claude/sdd.local.md` sets `judgment_model: sonnet` — the open value-set path for
accounts without Opus access. The prompt itself never names a model; a correct run reads the
setting and resolves the devil's-advocate dispatch to the sonnet tier instead of the roster's
`opus` default.

PASS requires ALL of:

1. The run completes the sweep without refusing and without a model-related failure:
   `docs/features/session-timeout/spec.md` is modified — the §6 «fast» NFR row is tightened to a
   numeric target + measurement (the prompt's confirmed values: p95 ≤ 2 seconds, measured at the
   API gateway — equivalent phrasing acceptable), and the frontmatter `updated_at` is re-stamped.
2. Every surfaced finding ends Resolved (spec tightened in its native section) or Deferred as a
   §8 row carrying both owner AND due — none dangling.
3. The final message states that the judgment / devil's-advocate dispatch resolved to the
   **sonnet** tier (per `judgment_model`), and nowhere claims the sweep ran on opus.
4. The final message contains the stage-handoff block (What I did / Review before continuing /
   Run next).

FAIL on: a refusal, a claim that opus was used (the setting was ignored), an untouched spec, a
dangling finding, or a missing handoff block.

> **Limitation (by design).** A headless eval cannot simulate a missing model entitlement — this
> scenario proves the **configuration path** (`judgment_model: sonnet` is read and honoured), not
> the hard-failure fallback (retry once on `inherit`), which is specified in
> `skills/_shared/agent-roster.md` §Model availability.
