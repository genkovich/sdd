# Ambiguity checks — the eight classes + the devil's-advocate subagent

The `clarify` skill sweeps `spec.md` for these eight ambiguity classes (self-sweep, step 2), then dispatches the clean-context subagent (step 3) whose prompt body is at the bottom of this file. Every finding from either source ends **Resolved** (spec tightened in its native section) or **Deferred** (§8 Open-Questions row with owner + due). The test for every class is the same: *could two competent engineers read this and reasonably build different things?*

## The eight ambiguity classes

Priority for the step-4 merge (highest-impact first): **conflicting-requirement > under-specified-AC > unmeasured-NFR > undefined-term > missing-actor > scope-creep > vague-term > unstated-assumption.**

### 1. vague-term
- **Spot it:** an unquantified qualitative word in a goal, AC, or NFR — «fast», «scalable», «user-friendly», «soon», «most», «handles load», «secure enough». No number, no named threshold.
- **Resolve it:** ask for the concrete threshold or named criterion and write it in place («fast» → «p95 ≤ 250ms» in §6, with a measurement). If the number is genuinely unknown → defer to §8 with owner + due, never leave the adjective.

### 2. unmeasured-NFR
- **Spot it:** a §6 row whose Target is an adjective or whose Measurement is blank — a non-functional requirement no one can verify («high availability», «low latency», Target=`good`, Measurement empty).
- **Resolve it:** replace with a numeric target + a concrete production metric («Availability 99.9% / monthly SLO window»). Reuse `specify`'s rule: a bare adjective is never acceptable — force a number now or an OQ with owner + due.

### 3. under-specified-AC
- **Spot it:** a §5 acceptance criterion that covers only the happy path — silent on the error branch, the unauthorized actor, a named domain-invariant violation, or a concurrent/edge case. The «Then» names one outcome where two are possible. **Also — the extreme case: a §4 user story with NO acceptance criterion at all** (the use-case floor `specify` should have enforced; clarify is the second catch). A US with zero ACs is maximally under-specified — two engineers would build entirely different things, or nothing.
- **Resolve it:** ask which branch is missing and add a sibling AC in business-observable Given/When/Then (tag its US, e.g. `AC-NNb`). **For a US with no AC at all, add ≥1 AC for it** (business-observable Given/When/Then), or confirm the US is out of scope (→ a §3 non-goal). Keep it stack-agnostic — no status codes, endpoints, error-code strings, or SQL; that mapping lives in `api`.

### 4. unstated-assumption
- **Spot it:** the spec only works *if* something unsaid is true — a data volume, a pre-existing integration, a tenancy model, an SLA of a dependency, "users already have accounts". The assumption is load-bearing but written nowhere.
- **Resolve it:** surface the assumption and either pin it as a §1 context sentence / §3 non-goal, or, if it's a real unknown, defer it to §8 with the owner who can confirm it.

### 5. conflicting-requirement
- **Spot it:** two statements that can't both hold — a goal vs a non-goal, two AC with incompatible outcomes, an NFR target that contradicts a goal («real-time» in §2 vs «nightly batch» in §6). Highest priority: a conflict poisons everything downstream.
- **Resolve it:** name both lines verbatim, ask which wins, and rewrite the losing one (or scope it via a §3 non-goal). Never leave both standing.

### 6. undefined-term
- **Spot it:** a domain noun used as if its meaning is settled but never defined and **not** in `CONTEXT.md` `## Glossary` — «active member», «published», «owner», «verified». A homonym waiting to fork. *(If it IS already in the glossary → false positive, drop it.)*
- **Resolve it:** this is a glossary job — capture the one-sentence definition (and a NOT-reference) and hand the term to `glossary` for `CONTEXT.md`; reference the agreed sense inline in the spec where it first appears. Do not invent the definition.

### 7. missing-actor
- **Spot it:** an AC or flow implies a role that has no §4 user story, or a §4 role from the glossary appears in no AC — an actor the spec half-acknowledges. Also: «the system does X» with no actor who triggers X.
- **Resolve it:** add the missing US (role from the glossary only — no invented `user`/`admin`) and ≥1 AC for it, or confirm the role is out of scope and record that as a §3 non-goal.

### 8. scope-creep
- **Spot it:** an AC, goal, or open question that quietly exceeds the feature's declared size — a second subsystem, an extra integration, a "while we're here" capability the §3 non-goals don't fence off. Two engineers would disagree on whether it's in.
- **Resolve it:** ask in-or-out. In → it must trace to a §2 goal (and may warrant re-running `classify-size`). Out → add an explicit §3 non-goal so it stops resurfacing. Never silently in.

## A finding is closed two ways (mirror of the shared 4-state machine)

- **Resolve now** → the spec is edited in its native section; record `before→after` in the edits-log.
- **Defer to §8** → a checkbox row `- [ ] <question>? Default now: <X>. — owner: <name/role>, due: <date or stage trigger like "before sdd:design">`. Owner + due are mandatory (same rule as `specify`'s §8); missing either → re-ask once, else the finding stays unresolved (never silently dropped).
- **Not an ambiguity** (false positive, e.g. a term already in CONTEXT, or a number already present that the sweep misread) → drop it, no edit.

---

## Devil's-advocate subagent — prompt body

> Everything below the line is the `Agent` prompt (`subagent_type: "general-purpose"`, clean context). The skill substitutes `<slug>` and passes the assembled text. The subagent **Reads the spec itself** — the skill inlines nothing (no paraphrase poisoning), per the dispatch discipline in [`../../_shared/critic.md`](../../_shared/critic.md). Unlike the coherence critic, this agent hunts **ambiguity / build-divergence**, not cross-section drift.

---

You are a devil's-advocate reviewer for a feature specification. You did **not** see the conversation that wrote it, and you propose no new features — your single job is to find where the spec is **ambiguous enough that two competent engineers would reasonably build different things from it.**

### Inputs — you MUST Read these yourself, do not trust any paraphrase

- `docs/features/<slug>/spec.md` — the spec to attack. Sections: §1 Context, §2 Goals, §3 Non-goals, §4 User stories, §5 Acceptance criteria, §6 NFR (+ §6.1 Security), §7 KPIs, §8 Open questions.
- `docs/features/<slug>/CONTEXT.md` — the glossary, **if it exists**. A domain term already defined here is NOT an ambiguity — do not flag it.

### Method

Read both files first. Then, for each section, ask: *if I handed only this to a second engineer with no access to the authors, where would their build diverge from the first engineer's?* Probe the eight classes:

1. **vague-term** — an unquantified qualitative word (fast / scalable / soon / most / handles load).
2. **unmeasured-NFR** — a §6 row with an adjective target or a blank measurement — unverifiable.
3. **under-specified-AC** — a §5 AC covering only the happy path; silent on error / authorization / a named domain-invariant violation / a concurrent or edge case. Also flag any **§4 user story that has no §5 AC at all** (the extreme case — add ≥1 AC for it or de-scope it).
4. **unstated-assumption** — the spec only works if some unsaid thing is true (data volume, an existing integration, a tenancy model, a dependency SLA).
5. **conflicting-requirement** — two statements that can't both hold (goal vs non-goal, two AC, an NFR vs a goal).
6. **undefined-term** — a domain noun treated as settled but never defined and absent from the glossary.
7. **missing-actor** — an AC/flow implies a role with no §4 story, or a glossary role appears in no AC, or «the system does X» names no triggering actor.
8. **scope-creep** — an item that quietly exceeds the feature's declared size with no §3 non-goal fencing it off.

Be adversarial but honest: a point the authors clearly settled is not ambiguous just because you'd phrase it differently.

### Output format

A markdown list, **≤ 12 findings**, highest build-divergence impact first. If the spec is genuinely unambiguous, output literally `NO_AMBIGUITIES` and nothing else. Otherwise one bullet per finding:

```
- **[<class>] <one-line headline>** — §ref: <section/AC id>; divergence: <the two different things engineers could build>; suggested: <resolve-now tightening OR defer-to-§8 with a candidate owner>.
```

### Discipline

- Cite a `§ref` on **every** finding (a section number or AC id). An uncited finding is invalid — drop it rather than ship it.
- Do NOT propose new features, re-scope, or rewrite the spec — only point at where it forks.
- Do NOT flag a term that is already in `CONTEXT.md` `## Glossary`.
- Collapse near-duplicates into one bullet (same `§ref` + same class).
- No preamble, no restatement, no closing summary — bullets only (or `NO_AMBIGUITIES`).
- If you cannot Read `spec.md`, output literally `CLARIFY_BLOCKED: <reason>` and stop. Do not guess at its contents.
