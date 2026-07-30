# Focused progress reporting — optional conversation contract

> **Reference-only.** Not a skill. Only the long-running `implement`, `fix`, and `review` skills
> read this contract, and it changes their output only when `.claude/sdd.local.md` sets
> `progress_style: focused`. Missing, malformed, or unknown values mean `standard`, which preserves
> the existing conversational behaviour. All other skills ignore this setting.

## Scope

Focused reporting shapes **conversation only** during implementation, bug fixing, and review. It
never shortens, caps, restructures, or removes content from `spec.md`, `sad.md`, ADRs, contracts,
task files, test plans, review records, fix records, or any other pipeline artifact. Artifact
templates, coverage floors, traceability rules, structural self-checks, and stage gates remain
authoritative.

Do not emit progress noise for an atomic operation that will immediately finish with the canonical
stage handoff. Use focused updates only when a run spans multiple meaningful phases, decisions,
tasks, or tool turns.

## Progress update

After a meaningful milestone, emit one compact update:

```md
**Progress** — Phase: <stage or activity> · Requirement: <AC / decision / task, or N/A> ·
Completed: <observable evidence> · Next: <one bounded action>
```

Rules:

- **Phase** names the active SDD stage or activity, not a vague status such as “working”.
- **Requirement** names the active acceptance criterion, user story, design decision, task ID, or
  review finding. Use `N/A` only when the skill genuinely has no traceable requirement.
- **Completed** names evidence: an artifact written, a decision resolved, a RED failure observed, a
  test/gate passed, or a finding closed. Never report intention as completion.
- **Next** is one bounded action. Do not add unrelated improvements or an invitation to continue.
- Report at phase boundaries or roughly every five interactive decisions, not after every tool call.

The existing Socratic cadence still applies. Focused mode may replace its mini-recap with the compact
progress update, but it must not increase question volume.

## Blocked or failed work

Report a blocker or failure without drama and without a success-shaped fallback:

```md
**Blocked** — Location: <artifact, file, command, task, or gate> · Cause: <specific cause> ·
Required fix: <smallest action that unblocks the run>
```

If the cause is not proven, say `Cause: unconfirmed — current hypothesis: ...`. Do not present a
hypothesis as fact. Existing stop, retry, rollback, escalation, and user-decision rules still govern
what happens next.

## Focus and clarification

- Finish the active requirement before raising an unrelated improvement.
- Correctness, safety, security, missing prerequisites, and cross-artifact contradictions may
  interrupt immediately because they can invalidate the active work.
- Preserve useful tangents in the artifact location the owning skill already defines: risks, open
  questions, follow-ups, reviewer findings, or a fix record. Never silently discard them.
- Resolve one ambiguity per `AskUserQuestion`, following [`ask-style.md`](./ask-style.md). Focused
  mode does not shorten option explanations or remove trade-offs.

## Completion and handoff

The canonical [`handoff.md`](./handoff.md) block remains the final output contract. A focused progress
update never replaces it, adds a fourth handoff section, or changes its route/`/clear` semantics.
The handoff remains the complete stage summary; progress updates exist only to keep a long run
oriented before that final gate.
