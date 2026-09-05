---
name: config
model: inherit
effort: medium
agents: []
description: >
  Use to create and tune the per-project settings file `.claude/sdd.local.md` — the one place that
  decides how deeply the pipeline interviews you, which model tier its judgment agents run at, how
  strict the TDD gates are, how tasks execute and commit, and what language your documents are
  written in. Triggers on "config", "settings", "configure sdd", "tune the pipeline", "change the
  judgment model", "set the interview depth", "write documents in Ukrainian", "/sdd:config",
  "налаштування", "налаштуй sdd", "зміни модель", "глибина опитування", "мова документів".
  Creates the file with documented defaults FIRST (so you have a working config before answering
  anything), reads what already differs from the defaults, then asks six grouped questions and
  patches only the keys you confirm — preserving your comments, key order and unknown keys.
  Never touches the pipeline's artifacts; the settings file is gitignored, only the .gitignore
  patch is committed.
---

# Skill: config

The settings file has many creators and **one editor: this one**. Six pipeline skills
(`interview` / `survey` / `roadmap` / `scaffold` / `specify` / `implement`) — and this skill too —
write `.claude/sdd.local.md` with documented defaults, so the pipeline always finds a real file.
None of the six offers to change a value. That offer lives here, and only here.

Everything about the file itself — the template, the create procedure, the `.gitignore` patch, the
key semantics, the edit rules — is canonical in
[`../_shared/settings-file.md`](../_shared/settings-file.md). This skill is the **conversation**
over it.

## Owner

Whoever owns the repo's setup — usually the lead who runs the pipeline first, once per project.

## Inputs

- Nothing is required. No gate, no upstream artifact: a bare repo is a valid starting point.
- (Optional) an existing `.claude/sdd.local.md` — read, diffed against the defaults, patched in
  place. Never regenerated.

## Protocol

1. **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md`
   is absent, create it now from the canonical template — documented defaults + the self-documenting body — and
   patch `.gitignore`; if it exists, read it and never overwrite. The one procedure lives in
   [`../_shared/settings-file.md`](../_shared/settings-file.md). Creating is unconditional;
   **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say one line:
   «`.claude/sdd.local.md` created with documented defaults — `/sdd:config` to tune it».
   (Here that line is the opening move, not a footnote: the user has a working config before the
   first question.)

2. **Read the current state.** Report in three lines: which keys **differ from the documented
   defaults** (with both values), which **unknown keys** and inline comments are present (they are
   preserved verbatim — say so), and whether the frontmatter parsed. **A malformed frontmatter is
   never repaired silently** — print the lines that failed to parse and offer exactly two ways
   forward: rewrite from the template (naming what will be lost) or stop so the user fixes it by
   hand.

3. **One forking question: defaults or tune?** Ask it per [`../_shared/ask-style.md`](../_shared/ask-style.md).
   «Stay on defaults» → skip to step 7 and print the handoff; the file is already on disk and
   working, so this is a legitimate exit, not an abort.

4. **Guess the host, with the evidence.** Which tool is running this session decides whether three
   keys are even usable. Rank the signals and **name them out loud** — the guess is never written
   silently, and contradictory traces are reported as contradictory. Signals + the always-confirm
   rule → [`./references/detection.md`](./references/detection.md).

5. **Ask the six grouped questions in three `AskUserQuestion` calls.** Questions are grouped by
   **decision**, not by key — a person tunes «how strict are the gates», not `gate_vet`. The six:
   host confirmation · model tier · strictness and gates · execution and commits · interview depth ·
   document language. Together they cover **21 of the 25 keys**. The four `cmd_*` keys are **not
   asked**: empty means the detection cascade reads the repo's own Makefile / package scripts /
   manifests, which is the better answer than a pinned command that rots. Verbatim wording, the
   options, and the question → keys map → [`./references/interview.md`](./references/interview.md).
   Model tier is asked **directly** rather than probed, because the session cannot enumerate the
   models an account actually has.

6. **Write the confirmed keys, key by key.** Patch only the lines whose values were confirmed;
   preserve comments, key order and unknown keys exactly. Print a `old → new` line per changed key,
   and **separately** list what was **derived rather than asked** — a non-Claude host clamping
   `team_mode: false` / `workflow_mode: off` / `max_parallel_agents: 1` (`TeamCreate` and `Workflow`
   exist only in Claude Code), and the `cmd_*` keys left empty for autodetect. A value the user did
   not choose must never read as if they had. Nothing else on disk is touched.

7. **Structural self-check + handoff.** Run the **structural self-check** per
   [`../_shared/self-check.md`](../_shared/self-check.md) — re-read the file **from disk** and verify
   **6 items**: (1) `.claude/sdd.local.md` exists (`test -f`); (2) its frontmatter parses and every
   confirmed key holds the confirmed value; (3) every key present before the run is still present —
   none dropped, including unknown ones; (4) every inline comment that was there is still there;
   (5) `.gitignore` contains `.claude/*.local.md` and `.worktrees/`, each exactly once; (6) no file
   outside `.claude/sdd.local.md` + `.gitignore` was modified (`git status --short`). Fix + re-check
   ≤2 cycles; surface anything unresolved. Then propose commit `chore: gitignore sdd settings`
   **only if `.gitignore` actually changed** — the settings file is gitignored and has nothing to
   commit. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   — *What I did* (the changed keys + the self-check line) + *Review* (`.claude/sdd.local.md`) +
   *Run next* (utility variant: `/clear` optional, resume your backbone stage — name the likely one).

## Definition of Done

- `.claude/sdd.local.md` exists and parses, whichever branch the run took (defaults or tuned).
- Every key the user confirmed holds the confirmed value; every key they didn't confirm is
  byte-identical to what was there before.
- Unknown keys, key order and inline comments survived the run.
- Every derived value (host clamp, autodetect) was named out loud, separately from the asked ones.
- `.gitignore` covers `.claude/*.local.md` and `.worktrees/`.
- The 6-item check in step 7 is this skill's structural self-check; its result is one line in the
  handoff.

## Anti-patterns

- **Asking before creating.** The file lands with documented defaults first; a user who answers
  nothing still ends up better off than before the run.
- **Regenerating the file from the template** because a key looked stale. That is how a
  hand-written comment or a hand-added key disappears. Patch key by key.
- **Writing a detected host silently.** Detection is evidence for a question, never an answer.
- **Offering `team_mode` / `workflow_mode` on a non-Claude host.** They clamp, and the clamp is
  stated — an option that cannot work is worse than no option.
- **Asking about `cmd_*`.** Empty = autodetect, which is the recommended answer; asking invites a
  pinned command that goes stale.
- **A settings question inside another skill.** The six pipeline skills create and read.
  Only `config` tunes.
- **Touching pipeline artifacts.** This skill writes two files and no others.

## References

- [`../_shared/settings-file.md`](../_shared/settings-file.md) — the canonical template, procedure and key semantics.
- [`./references/detection.md`](./references/detection.md) — host signals, ranked, and the always-confirm rule.
- [`./references/interview.md`](./references/interview.md) — the six questions verbatim + the question → keys map.
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — how every question is phrased.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — what each Claude mechanism maps to under Codex CLI / Cursor.
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — what the model tier actually changes.
- [`../implement/references/settings.md`](../implement/references/settings.md) — the engine-side delta.
