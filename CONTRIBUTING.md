# Contributing to SDD

## Adding or editing a skill

A skill lives in `skills/<name>/` and is the **source of truth** for its stage.

1. **`SKILL.md` is a short spine.** Frontmatter (`name` + a third-person `description` with
   3–5 trigger phrases, EN plus 2–3 UA) then a numbered Protocol. Keep it lean — target well
   under ~140 lines. Heavy detail goes in `references/`; output scaffolds go in `templates/`.
2. **Don't duplicate shared logic.** The 4-state Socratic machine, the clean-context critic,
   the size matrix, and the `AskUserQuestion` style live once in `skills/_shared/`. Reference
   them with a relative link and keep only a short per-skill **delta** (your decision-types,
   your section list, your F6 specialization).
3. **Stay stack-agnostic.** No hard-coded language, tracker, test framework, or load tool.
   Detect what the repo uses, or name the detected tool as «whatever your repo already uses».
4. **Gate your inputs.** If a prerequisite artifact is missing, hard-refuse with a pointer to
   the skill that produces it.
5. **One level of `references/`.** No nested reference folders.

## Subagents

Engine subagents live in `agents/*.md` with `name` / `description` / `model: inherit`
frontmatter and a system prompt that instructs them to read upstream artifacts directly.

## Before you open a PR

Run the validator locally — it's the same gate the `validate` GitHub workflow runs, and it now
enforces the plugin's **conventions**, not just its structure:

```bash
python3 scripts/validate_plugin.py
```

It checks that the plugin + marketplace manifests agree on name / version / description, that the
version is semver, that every skill and agent carries its required frontmatter (and that `_shared/`
stays reference-only), **and** the consistency invariants in the checklist below. It also greps for
references to the excluded legacy dirs. (The check count is a moving target — CI asserts exit 0, not
a fixed number.)

### Pre-PR checklist

- [ ] **`python3 scripts/validate_plugin.py` passes** (exit 0).
- [ ] **One canonical source / DRY.** Shared logic — the Socratic machine, the critic, the size
      matrix, the ask-style, the surface taxonomy, the handoff block — lives once in
      `skills/_shared/`. Link to it with a relative path and keep only your per-skill *delta*; never
      copy a `_shared/` table (e.g. the surface taxonomy) into a `SKILL.md`.
- [ ] **Stack-agnostic.** No hard-coded language, tracker, test framework, or build/load tool —
      detect what the repo uses, or name it «whatever your repo already uses».
- [ ] **Every skill ends with the handoff block** ([`skills/_shared/handoff.md`](./skills/_shared/handoff.md))
      as its final step.
- [ ] **Invocation form is `/sdd:<name>`** — the namespaced form, never the hyphenated `/sdd-<name>`.
- [ ] **Relative links resolve.** A `[text](./path.md)` target is a real file. The one exception is a
      template-runtime path (`../spec.md`, `../sad.md`, `../contracts/…`, …) that resolves only inside
      a generated `docs/features/<slug>/` folder — those are allowlisted in the validator.
- [ ] **References in `references/`, templates in `templates/`** — one level deep, no nested folders.
