# Tool adapters — running SDD under Codex CLI / Cursor (the cross-tool mapping)

> **Reference-only.** Not a skill. The skills are written against Claude Code's mechanisms
> (`/sdd:<name>` invocation, `AskUserQuestion`, named subagents, `TeamCreate` / `Workflow`,
> `/clear`). SKILL.md is the open Agent Skills format, so Codex CLI and Cursor run the **same
> files unchanged** — `install.sh` copies the repo subtree verbatim and each Claude-specific
> mechanism maps to the host tool's equivalent per the table below. At install time every skill
> name gets an `sdd-` prefix (the bare `review` / `design` / `api` would collide with generic
> names), so the Claude form `/sdd:specify` keeps its mapping: `sdd-specify`.

## The mapping

| Mechanism (as written in the skills) | Claude Code | Codex CLI | Cursor |
|---|---|---|---|
| Invoke a stage | `/sdd:specify <slug>` | `$sdd-specify <slug>` | type `/`, pick `sdd-specify` |
| Ask the user (`AskUserQuestion`) | the native tool | numbered questions in plain text — **stop and wait** for the answer, never assume one | same as Codex |
| Spawn a subagent (`subagent_type: "sdd:researcher"`) | the named plugin agent | custom agent `sdd-researcher` installed into `.codex/agents/` (dispatch via `/agent`), or run the agent file's instructions inline | subagent `sdd-researcher` installed into `.cursor/agents/`, or inline |
| `TeamCreate` / `Workflow` (the `implement` engine modes) | native | sequential single-agent TDD — already the documented fallback floor | same as Codex |
| Fresh context between stages | `/clear` | `/new` | start a new chat |
| `model:` / `effort:` frontmatter | honored | advisory — the installer rewrites the generated agents' `model:` to `inherit`; the frontmatter in the verbatim skill/agent copies stays as documentation | same as Codex |
| Shared artifacts (`.size`, `.route`, `spec.md` + the other `docs/features/<slug>/…` files, `.claude/sdd.local.md`) | repo-relative files the **model itself** reads/writes with its file tools | identical — no host involvement, so they work unchanged; `.claude/` is just a directory in the repo here, not a host config dir | same as Codex |
| Design-tool MCP (Figma / Pencil — used by `design-system` / `screens`) | the session's connected Figma / Pencil MCP tools, per the committed `docs/design-system.md` `tool` choice | MCP not available in the host/session → **`code` mode**: inline markdown wireframes in `screens.md` + a **named degradation** in the manifest §Source and the handoff — never a blocked stage | same as Codex |

The `CLAUDE_CODE_*` env vars the roster mentions (`CLAUDE_CODE_SUBAGENT_MODEL`,
`CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_FORK_SUBAGENT`) are **Claude Code-only** — Codex CLI and
Cursor ignore them; use the host's own model settings instead.

## The rule

When a mechanism is unavailable in the host tool, **degrade to the inline sequential
equivalent — never block the stage** on a missing host feature. The same rule covers a missing
**model tier**: when the selected model is unavailable to the account, retry the dispatch once on
`inherit` and continue — canonical in [`agent-roster.md`](./agent-roster.md) §Model availability.
The stage-handoff block ([`handoff.md`](./handoff.md)) is still printed in full every run; only
substitute the host's invocation + fresh-context forms from the table above.
