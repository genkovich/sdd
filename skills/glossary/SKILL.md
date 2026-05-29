---
name: glossary
model: haiku
effort: low
agents: []
description: >
  Use to capture or update domain terms in CONTEXT.md before their meaning drifts —
  whenever a fuzzy word shows up in an interview, spec, or review and you want one
  canonical definition plus a NOT-reference so a homonym can't bite you in six months.
  Triggers on "add term {X}", "what is {X} in our domain", "add to CONTEXT", "fix the
  glossary", "define {X}", "/sdd:glossary {term}", "додай термін", "онови глосарій",
  "що означає {X}". Lazy-bootstraps docs/features/{slug}/CONTEXT.md (or repo-root
  CONTEXT.md) from a template, checks for a conflicting existing entry, asks for a
  one-sentence definition + the concept it's confused with, and appends one line to
  ## Glossary. Skip generic tech words (HTTP, queue, cache) — those are not domain terms.
  Output: created/edited CONTEXT.md. Runs anytime, no input gate; specify and design
  read its ## Glossary as the canonical source of role and domain-term names.
---

# Skill: glossary

Lazy utility that fixes the meaning of a domain term in `CONTEXT.md` the moment it first surfaces, so its sense doesn't drift across the pipeline. For each term it captures a one-sentence canonical definition and — when the word is ambiguous — a **NOT-reference** naming the concept it's confused with. Runs anytime, with no upstream gate: a single term mid-interview, or a batch handed over by `specify`. The output feeds `specify` (role + domain-term names) and `design` (invariants), which treat `## Glossary` as canonical and override anything that contradicts it.

This is a capture utility, not a Socratic stage — it does **not** run the shared Socratic loop or critic. The one shared dependency is question phrasing:
→ [`../_shared/ask-style.md`](../_shared/ask-style.md)

## Owner

Whoever drives the conversation — anyone who spots ambiguity. Tech Lead approves the canonical form when a term is contested.

## Inputs

- `<term>` — the domain word/phrase to fix. If not given, ask for it.
- (Optional) `<slug>` — feature slug; targets `docs/features/<slug>/CONTEXT.md`. Absent → repo-root `CONTEXT.md`.
- (Optional) `pending_glossary_terms` — a batch handed over by `specify` after it writes the spec. Process each term in turn.
- (Optional) proposed phrasings already surfaced in an interview/brainstorm — offer them as definition options instead of asking blank.

## Protocol

1. **Pick the target.** If `<slug>` is given → `docs/features/<slug>/CONTEXT.md`. Otherwise → repo-root `CONTEXT.md`. One glossary per file; don't split a term across both.
2. **Generic-term filter.** Reject words that name infrastructure or transport rather than the business domain (e.g. HTTP, queue, cache, the datastore, the broker, a framework). Refuse: «`<term>` is technical, not a domain word — its choice belongs in the SAD or an ADR, not the glossary». Continue only for genuine domain vocabulary.
3. **Bootstrap (lazy).** `test -f <target>`. Missing → copy [`./templates/CONTEXT.md`](./templates/CONTEXT.md) to `<target>`. Present → read it.
4. **Conflict check.** `grep -i "^- <term>" <target>`.
   - Found, identical sense → STOP, report «already in the glossary».
   - Found, different sense → escalate via `AskUserQuestion` (phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md)): «`<term>` is already defined as `<existing>` — same concept or a different one?». If different, propose a disambiguating pair of names (e.g. a billing-scoped vs a runtime-scoped variant) and fix both.
   - Not found → continue.
5. **Ask the canonical definition** — one `AskUserQuestion`: «Define `<term>` in this domain, in one sentence». Offer interview/brainstorm phrasings as options when available; otherwise free text.
6. **Ask the NOT-reference** — one `AskUserQuestion`: «Which concept does `<term>` get confused with, so a future reader doesn't mix them up?». No plausible homonym → `None`.
7. **Compose one line.** `- <term> — <one-sentence definition>. NOT <confused concept + how it differs>.` — or, when step 6 = None, `- <term> — <definition>.`
8. **Append under `## Glossary`.** Read the file, insert the line in `## Glossary` (alphabetical if the section is already sorted, else at the end). Never rewrite existing entries.
9. **Prune empty H2s.** On a fresh bootstrap, delete `## Invariants` / `## Out of scope` if they hold no real content — only `## Glossary` is mandatory. (A genuine invariant or out-of-scope note goes in its section, never as implementation detail.)
10. **Stamp + commit + handoff.** Set `updated_at: <today>` in the frontmatter. Propose `context: + <term>` (or `context: + <term>, <term2>` for a batch). May fold into the caller's intake/spec commit. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) (utility variant) — *What I did* + *Review* (`CONTEXT.md`) + *Run next*: resume your backbone stage (e.g. `/sdd:design <slug>`); `/clear` optional.

## Definition of Done

- `<target>` exists and contains `<term>` under `## Glossary` in the «one-sentence canonical + optional NOT-reference» format.
- Any conflict with an existing entry is resolved (reported as duplicate, or disambiguated into distinct names).
- Generic tech words are refused, not stored.
- Empty H2 sections are pruned on bootstrap; `## Glossary` remains.
- `updated_at` reflects today; a commit is proposed.

## Anti-patterns

- **Glossary as spec or scratch pad.** Implementation detail («counter stored with a 1-minute TTL») belongs in the SAD/ADR, not here.
- **Empty H2 «for completeness».** A heading with no bullets — prune it.
- **Silent edits.** Adding a term without confirming the definition; the author must control the glossary.
- **Batched «I'll add them later».** Capture each term the moment it surfaces — deferral loses it.
- **Storing generic tech words.** HTTP, queue, the datastore name — refuse them.
- **Rewriting on re-run.** The skill reads and appends; it never overwrites the file.
- **Ambiguous term with no NOT-reference.** A homonym without «NOT …» is a six-month confusion waiting to happen.

## References & template

- [`./templates/CONTEXT.md`](./templates/CONTEXT.md) — output scaffold; inline comments are the per-section contract (Glossary mandatory, Invariants/Out-of-scope pruned when empty).
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — phrasing for the definition / NOT-reference / conflict questions.

## Example invocation

> **User:** «add term tenant for rate-limiting-per-user»
> **Skill:** `<slug>` given → target `docs/features/rate-limiting-per-user/CONTEXT.md`. Generic filter: `tenant` is domain → continue. File missing → copy template. `grep "^- tenant"` → not found. Definition Q → «a billable customer organisation owning 1+ users». NOT-reference Q → «NOT user — a user is one person inside a tenant». Compose `- tenant — a billable customer organisation owning 1+ users. NOT user (a user is one person inside a tenant).` → append under `## Glossary` → prune empty `## Invariants`/`## Out of scope` → `updated_at: 2026-05-28` → commit `context: + tenant`.
