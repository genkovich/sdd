# Blast-radius heuristic — when an architectural decision becomes ADR-worthy

> **TL;DR.** *Blast radius* — how painful it would be to reverse a decision three months from now. Three criteria: (1) rework ≥3 days (irreversible); (2) seen by ≥2 modules; (3) a legitimate alternative exists. **2 of 3 → ADR.** 0 → inline in sad.md. Expect 5–12 ADRs per M feature.

The skill makes 15–30 decisions per pass. Without a gate you'd either spawn one ADR per decision (noise — kills the genre) or zero (loses the *why* of the important ones). The blast-radius heuristic picks the right 5–12. It is design's per-skill Socratic gate, run on every **Approved** decision (see [`./socratic.md`](./socratic.md)).

## The three criteria

A decision crosses the threshold if it scores **2 of 3** (a single criterion = borderline, ask explicitly).

### 1. Irreversible

> If we picked a different option three months from now, would the rework take ≥3 days?

**Fires** for, e.g.:

- **Storage shape** — relational vs document vs object store; moving later means a data migration measured in weeks.
- **Sync vs async module coupling** — a direct call vs a background event changes the data shape and the failure model of everything downstream.
- **ID strategy** — random vs time-sortable vs auto-increment; switching later needs a *backfill* (a script that walks every existing row and rewrites its id, read-locking those rows while it runs).
- **Auth model** — sessions vs per-request tokens; changes the shape of every request.
- **Sharding / partition key** — the key data is spread across servers by; changing it later means re-clustering everything.

**Does not fire** for, e.g.:

- **Library choice within the same language** (two equivalent libraries for the same job) — rework is search-and-replace, a few hours.
- **A configuration value** (a 5s vs 10s timeout) — one PR.
- **Naming** (`objective` vs `title`) — the IDE renames it in a minute.

### 2. Multi-module impact

> Does this decision change a contract seen by ≥2 modules?

**Fires** for: an event schema crossing module boundaries; a shared error-code namespace; a pagination convention used by several endpoints; a migration adding a column other modules read.

**Does not fire** for: an internal function name inside one module; a private method signature; a log format used by only one component.

### 3. Has legitimate alternatives

> Will a reader six months from now ask «why not X?» where X is a real, non-strawman alternative?

**Excludes:** decisions where the alternative is obviously worse (no strawman ADRs); decisions where the alternative is ruled out by an existing constraint (no ADR for «we used the language the repo is already written in»).

**Catches:** choices that look arbitrary from the code (why *this* cache TTL? why *this* circuit-breaker threshold?); trade-offs where two reasonable engineers would pick differently; anything where the option set was 2–3 serious options, not 1.

## Using the heuristic during the Socratic pass

After each `AskUserQuestion` choice:

1. **Score it** — how many of the three fire?
2. **Decide:** 0 → inline, no ADR. 1 → borderline (default inline, except §4 Solution Strategy where the bar is lower because strategy is broad by definition). 2+ → ADR.
3. **On a borderline,** ask explicitly: «This is borderline ADR-worthy because of <criterion>. Lock as ADR or keep inline?» with `Lock as ADR` (Recommended if irreversible) / `Inline only`.

## Why 5–12 per M feature

- **Below 5:** probably under-ADR-ing (missed an irreversibility) — unless the feature is genuinely XS/S (2–4 is fine).
- **5–12:** healthy for an M feature; each ADR is a real decision with reread value.
- **Above 12:** probably over-ADR-ing — bundle, re-scope, or move tactical detail inline. L/XL may justify 10–15.

## Closing self-review

1. Does §9 reference every file in `adr/`? No orphans.
2. Does every ADR have a Status (`Accepted`) and a Decision outcome (not just a Context)?
3. For each ADR — would the heuristic still gate it if you ran it again? (Did you ADR-ify a trivial config value?)
4. For inline decisions — does any feel like it should have been an ADR? Promote it.

## Anti-patterns

- **ADR-ifying the alternative you rejected.** The ADR is about the chosen path; alternatives go in `## Considered options`, not their own file.
- **An ADR with `Status: Proposed` from this skill.** Synchronous decisions with the user → `Accepted`. Use `decide-adr` for asynchronous Proposed → Accepted flows.
- **One ADR per quality goal.** Quality goals live in §10; ADRs document the specific *decisions* taken because of them.
- **A title that names the problem, not the decision.** `0003-rate-limiting.md` (bad) vs `0003-sliding-window-counter.md` (good).
