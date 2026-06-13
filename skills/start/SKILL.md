---
name: start
model: sonnet
effort: low
description: >
  Use to open the SDD visual dashboard — the local browser UI that shows every feature's
  pipeline stage, renders its artifacts (markdown, mermaid C4/sequence/ER, OpenAPI/swagger),
  lets you edit artifact text back to disk, and drives the pipeline by sending /sdd:<skill>
  commands back into this live session. Triggers on "start the dashboard", "open the SDD
  dashboard", "sdd dashboard", "/sdd:start", "show the pipeline UI", "відкрий дашборд",
  "запусти панель SDD". The sdd-dashboard MCP server auto-starts at session open (via .mcp.json),
  resolves the project from CLAUDE_PROJECT_DIR, binds its loopback HTTP listener, and writes the
  dashboard URL (with a per-session capability token) to ~/.claude/sdd-dashboard/current.url —
  so start's job is simply to READ that file and print the URL. No MCP tool call, no channel
  round-trip on the common path. Opt-in: requires dashboard_enabled: true in .claude/sdd.local.md
  and Bun installed; if either is missing it prints guidance and exits cleanly (pure-markdown
  skills are unaffected).
---

# Skill: start

Opens the **SDD visual dashboard** — a local, loopback-only browser UI served by the
`sdd-dashboard` MCP server (Bun + `Bun.serve()`), embedded in the same process that holds this
session's MCP channel. The dashboard reads `docs/features/` off disk, renders every artifact, and —
the point of it — **drives the pipeline back into this session**: a click in the browser sends a
validated `/sdd:<skill> <slug>` command through the channel, this Claude runs it, and progress
streams back to the browser live.

`start` is **not** "start the server" — the server auto-starts when the session opens (declared in
`.mcp.json`). On boot it resolves the project from `CLAUDE_PROJECT_DIR`, binds the HTTP listener, and
**writes the dashboard URL to `~/.claude/sdd-dashboard/current.url`**. So on the common path `start`
just **reads that file and prints the URL** — a plain file read, no MCP tool, no channel message.

## Owner

The developer running the session. No artifact is produced — this is a connection skill.

## Inputs

- `.claude/sdd.local.md` — read `dashboard_enabled` (must be `true`). Auto-created with documented
  defaults by `specify`/`implement` → [`../implement/references/settings.md`](../implement/references/settings.md).
- `~/.claude/sdd-dashboard/current.url` — the file the server writes when it binds: line 1 is the
  dashboard URL (with the capability token), line 2 is the project dir it resolved. **This is the
  primary input** — present whenever the server bound HTTP at boot.
- (Fallback only) the `sdd-dashboard` MCP server's `dashboard_handshake` tool — used **only** when the
  URL file is absent (the server couldn't resolve the project at boot, e.g. `CLAUDE_PROJECT_DIR` unset).

## Protocol

1. **Gate on opt-in.** Read `.claude/sdd.local.md`.
   - **Absent** → the dashboard is opt-in and off by default. Auto-create the file with the documented
     defaults per [`../implement/references/settings.md`](../implement/references/settings.md) (which
     include `dashboard_enabled: false` + `dashboard_port: 4178`), then tell the user: «The dashboard is
     opt-in — set `dashboard_enabled: true` in `.claude/sdd.local.md` and re-run `/sdd:start`.» **Stop.**
   - **Present, `dashboard_enabled` not `true`** → print the same one-line enable instruction and **stop**.
     (Pure-markdown users are unaffected.)
2. **Read the URL file (the common, channel-free path).** Read `~/.claude/sdd-dashboard/current.url`
   (e.g. `cat "$HOME/.claude/sdd-dashboard/current.url"`).
   - **Present** → line 1 is the live dashboard URL. **Print it and go to step 5. Do NOT call any MCP
     tool** — the server is already up and bound; nothing else is needed. (Optionally note line 2, the
     project dir, if it differs from the current project — that would mean another session's server is
     bound; tell the user rather than guessing.)
   - **Absent** → the server is connected but idle (it couldn't resolve the project at boot). Continue to step 3.
3. **(Fallback) check Bun + the MCP server.** Run `bun --version`; if Bun is missing, print «The dashboard
   needs Bun — install from https://bun.sh, then re-run `/sdd:start`. The markdown skills work without it.»
   and **stop**. If the `dashboard_handshake` tool is unavailable, tell the user to check `/mcp` (the
   `sdd-dashboard` server may have failed to boot — Bun missing, or `.mcp.json` not picked up; re-open the
   session) and **stop**.
4. **(Fallback) hand the project over.** Determine the absolute project root — prefer
   `git rev-parse --show-toplevel`; fall back to the cwd that contains `docs/` or `.git`. Call
   **`dashboard_handshake`** with `project_dir` set to that path. It binds HTTP, writes
   `current.url`, and returns the URL. Use the returned URL.
5. **Print the URL + how it behaves.** Show the URL prominently
   (`http://127.0.0.1:<port>/?session=<id>&token=<cap>`) and offer to open it. Then state the
   **load-bearing UX truth** so the user isn't surprised:
   - The dashboard is a **driver + observer**, not a synchronous remote control.
   - A click is consumed **only while this session is idle at the prompt**; mid-task it **queues**.
   - Dashboard-driven runs default to **`--depth=easy`** (the skill self-decides reversible calls and
     asks far fewer questions) because the browser can't answer a blocking `AskUserQuestion`; if a stage
     genuinely needs a decision, it surfaces in **this terminal** — answer it here.
6. **Handoff.** **Emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   (utility variant) — *What I did* (printed the dashboard URL) + *Review* (open the URL; the dashboard
   mirrors `docs/features/` and the session activity pane streams runs) + *Run next* (open the dashboard
   and click **Run next stage** on a feature, or run a backbone command here, e.g. `/sdd:specify <slug>`).
   `/clear` is **optional** for this utility.

## Definition of Done

- `dashboard_enabled: true` confirmed (or guidance printed + stopped).
- The dashboard URL printed — read from `~/.claude/sdd-dashboard/current.url` on the common path, or
  (fallback only, when that file is absent) obtained from `dashboard_handshake` after a Bun check.
- The queued/busy/`--depth=easy` behaviour stated so the user knows the dashboard is a driver, not a remote control.
- The stage-handoff block emitted (utility variant).

## Anti-patterns

- **Calling `dashboard_handshake` when `current.url` already exists.** The common path is a plain file
  read — the server is already bound. Only hand over via the tool when the URL file is absent.
- **Treating `start` as "boot the server".** The server auto-starts via `.mcp.json`; `start` only prints
  the URL. Never try to spawn `bun` yourself.
- **Proceeding when `dashboard_enabled` is not `true`.** It is opt-in — print the enable line and stop.
- **Fabricating the URL.** It comes only from `current.url` (or the `dashboard_handshake` result) — never
  invent a port or token.
- **Running a dashboard-triggered stage at `--depth=hard`.** Browser-driven runs default to `--depth=easy`;
  a Socratic prompt the browser can't answer would block the queue.

## References

- [`../implement/references/settings.md`](../implement/references/settings.md) — `.claude/sdd.local.md`,
  including the `dashboard_enabled` / `dashboard_port` keys this skill gates on.
- [`../_shared/handoff.md`](../_shared/handoff.md) — the stage-handoff block (utility variant) this skill emits.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — Codex/Cursor mapping for the Claude-specific
  mechanisms (the dashboard channel is Claude Code-only; non-Claude hosts use the markdown skills directly).
