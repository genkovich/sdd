# Settings — the `implement` engine's delta (step 2)

**The canon lives in [`../../_shared/settings-file.md`](../../_shared/settings-file.md)**: the
documented template, the create-when-absent procedure, the `.gitignore` patch, the semantics of
every key, the edit rules, and the who-creates-who-changes-who-reads table. This file carries only
what is specific to the **engine** — which keys it consumes, how model + effort resolve at
dispatch, and how `.size` scales them. Values are changed by [`../../config/SKILL.md`](../../config/SKILL.md)
(`/sdd:config`) and by nothing else.

`implement` **ensures** the file the same way the other five creating skills do (protocol step 2:
absent → write the canonical template + patch `.gitignore`; present → read, never overwrite). The
file is normally already there — the backbone's earlier stages create it — so this is the
jump-straight-to-implement path, not the usual one.

## Keys the engine reads

| Group | Keys | Effect |
|---|---|---|
| TDD loop | `tdd`, `stop_on_red`, `max_red_retries` | skip RED; halt-vs-continue on a surviving red; attempts before escalation → [`escalation.md`](./escalation.md) |
| Execution mode | `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation` | feed the decision tree → [`decision-tree.md`](./decision-tree.md). `team_mode` wins when both could apply; `isolation: inplace` forces parallelism to 1 |
| Gate | `gate_lint`, `gate_vet`, `require_integration` | which tiers the per-task gate runs; `require_integration: always` BLOCKS before dispatch when no Docker daemon answers |
| Commands | `cmd_test_unit`, `cmd_test_integration`, `cmd_lint`, `cmd_vet` | a non-empty value short-circuits detection → [`command-detection.md`](./command-detection.md) |
| Git | `auto_commit`, `branch_strategy` | commit granularity; feature branch vs. current |
| Dispatch | `model_test_author`, `model_implementer`, `model_reviewer`, `effort_test_author`, `effort_implementer`, `effort_reviewer`, `judgment_model` | the model + effort each spawned agent runs at |

**Not engine keys, read elsewhere:** `interview_depth` (the Q&A skills' depth dial) and
`artifact_language` (the prose language of every pipeline document —
[`../../_shared/artifact-language.md`](../../_shared/artifact-language.md)). The engine neither
reads nor writes them; they live in the same file because it is one per-project settings file, not
an implement-only one.

## Model + effort at dispatch

Full precedence, highest wins: **`env` > invocation > `model_<role>` > `judgment_model` >
agent frontmatter > session**. Canonical, together with the roster defaults and the
model-availability degrade rule, in
[`../../_shared/agent-roster.md`](../../_shared/agent-roster.md).

- **`judgment_model`** covers all five judgment agents at once (`reviewer` / `critic` /
  `devils-advocate` / `strategist` / `analyst`); the execution agents (`test-author` /
  `implementer`) and `explorer` / `researcher` are unaffected. **The default `opus` is a floor,
  not a pin** — unset + a session running a stronger tier ⇒ dispatch with `inherit`, never a
  silent downgrade of judgment below the session. An explicit value is honored literally, and an
  unavailable model degrades per the roster rule (retry once on `inherit` — never block).
- **Env path.** The engine exports `CLAUDE_CODE_EFFORT_LEVEL` / `CLAUDE_CODE_SUBAGENT_MODEL` for
  the dispatch when these keys are set — the reliable lever (frontmatter alone may not suffice; see
  [`../../_shared/agent-roster.md`](../../_shared/agent-roster.md)). Claude Code only — Codex CLI
  and Cursor ignore them → [`../../_shared/tool-adapters.md`](../../_shared/tool-adapters.md).
- **`.size` scaling.** The engine raises the default effort for **L/XL** features (execution agents
  → `high`) before dispatch and keeps the cheap defaults for **XS/S** — a cross-module change is
  where reasoning depth pays off. An explicit `effort_<role>` in the settings always wins over the
  scaling.
- **Banner.** Step 7 prints the resolved per-role model + effort alongside the mode, so the user
  sees how the engine will behave before it acts.

## Reading semantics

Unknown keys ignored, a missing key falls back to its documented default, a malformed file → warn
and run on all-defaults. The engine is a **reader**: it never repairs, reformats or rewrites the
file — that is `config`'s job alone.
