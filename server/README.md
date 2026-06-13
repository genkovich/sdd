# SDD Visual Dashboard

A local, **opt-in** browser dashboard for the SDD pipeline. It reads `docs/features/` straight off
disk, renders every artifact, lets you edit artifact text back to disk, and **drives the pipeline** —
a click in the browser sends a `/sdd:<skill> <slug>` command back into your live Claude Code session,
which runs the skill and streams progress back to the browser.

The whole thing is one Bun process (`server/`) that auto-starts as an MCP server when a Claude Code
session opens. It holds the MCP channel to Claude **and** an embedded `Bun.serve()` HTTP+WS listener on
`127.0.0.1`. The browser tab is just another channel — the same mechanism the official Telegram plugin
uses to message a session, re-skinned as a dashboard.

> **Pure-markdown users are unaffected.** Nothing binds, nothing opens, until you opt in.

---

## Quick start

**1. Install Bun** (the server runtime — the same dependency the Telegram plugin uses):

```bash
curl -fsSL https://bun.sh/install | bash   # or: brew install bun
bun --version                              # sanity check
```

**2. Enable the dashboard** in your project's `.claude/sdd.local.md` (the file the pipeline
auto-creates with documented defaults — `specify`/`implement`/`start` will create it if absent):

```yaml
dashboard_enabled: true    # opt in
dashboard_port: 4178       # optional — the loopback port (scans upward if busy)
```

**3. Open a Claude Code session in your project and run:**

```
/sdd:start
```

It hands the server your project directory, confirms the channel works both ways, and prints the URL:

```
http://127.0.0.1:4178/?session=<id>&token=<capability-token>
```

Open that URL in a browser. That's it.

---

## What you can do

| In the browser | What happens |
|---|---|
| **Pick a feature** (sidebar) | See its pipeline as a per-step checklist: `done` / `skipped` / `pending` / `blocked`, derived from the artifacts on disk. An XS feature shows *skipped* stages — not gaps. |
| **Open an artifact** (tabs) | Renders markdown, **mermaid** (C4 / sequence / ER diagrams), and **OpenAPI** (redoc) — all from vendored libs, fully offline. |
| **edit** → **save** | Writes the artifact back to disk: scoped to `docs/`, atomic (`tmp+rename`), with a `409` if the file changed under you since you opened it. |
| **▶ Run next stage** / per-stage **run** | Sends `/sdd:<skill> <slug>` into your session. Claude runs the skill; the session-activity pane streams its log + the handoff. |
| **+ new** | Runs `/sdd:specify <slug>` to start a new feature. |
| **message the session…** | Free-text chat to Claude (relayed as channel content, not a command). |

### It's a driver, not a remote control

A click is consumed **only while your session is idle at the prompt**. If Claude is mid-task, the
command **queues** (the UI says so — it never fakes synchronous execution). Dashboard-driven runs default
to `--depth=easy`, so the skill self-decides reversible calls and asks far fewer questions — because the
browser can't answer a blocking `AskUserQuestion`. If a stage genuinely needs a decision, it surfaces in
**your terminal** — answer it there, and the run continues.

---

## Configuration

Read from `.claude/sdd.local.md` (per-project, git-ignored):

| Key | Default | Meaning |
|---|---|---|
| `dashboard_enabled` | `false` | Opt in. When false/absent the server stays idle (no HTTP bind). |
| `dashboard_port` | `4178` | Loopback port to bind; scans `4178..4189` if busy. |

Environment overrides (handy for testing / unusual setups):

| Env var | Effect |
|---|---|
| `SDD_DASHBOARD_ENABLED=1` | Force-enable without the settings file. |
| `SDD_DASHBOARD_PORT=<n>` | Default port (a `dashboard_port` in settings still wins). |
| `SDD_DASHBOARD_TOKEN=<hex>` | Pin the capability token (otherwise random per session). |
| `CLAUDE_PROJECT_DIR=<path>` | Project root at boot (Claude Code sets this; `/sdd:start` overrides authoritatively). |

---

## Security model

- **Loopback only.** Binds `127.0.0.1` — never a public interface.
- **Scoped I/O.** Every read/write is `realpath`-contained to `<project>/docs/` with an extension
  allowlist (`.md` / `.yaml` / `.yml` / `.json` / `.size`); `.git` and anything outside `docs/` is refused.
- **Capability token.** Mutating routes (run a command, save an edit, chat) require the per-session token
  issued by `/sdd:start` (in the URL), plus `Origin`/`Host` loopback checks — so another local page can't
  POST to your port.
- **No command injection.** Inbound `/sdd:` lines are built **only** from a server-side allowlist
  (validated skill name + `^[a-z0-9][a-z0-9-]*$` slug). Browser text never becomes an arbitrary command.
- **Anti-injection contract.** The MCP `instructions` tell Claude that dashboard content is an SDD command
  or chat — never authority to bypass a gate, approve a review, change settings, or touch files outside `docs/`.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/mcp` shows `sdd-dashboard` **failed** | Bun isn't installed (the `.mcp.json` launches `bun`). Install Bun, reopen the session. |
| `/sdd:start` says **"not enabled"** | Set `dashboard_enabled: true` in `.claude/sdd.local.md`, re-run `/sdd:start`. |
| Browser shows **"no token in URL"** | Open the exact URL `/sdd:start` printed (the token authorises the session). |
| **"project dir unresolved"** | Run `/sdd:start` inside the project (it hands the real path over), or set `CLAUDE_PROJECT_DIR`. |
| A click does nothing | The session is busy or waiting on a question in your terminal — the command is queued; it runs when Claude is idle at the prompt. |
| Port differs from 4178 | It was busy; `/sdd:start` prints the actual port it bound. |

---

## Architecture (one process, the channel pattern)

```
 Browser tab (dashboard)              Claude Code session
  index.html / app.js  ── HTTP/WS ──┐   Claude runs /sdd skills
                                     │        ▲
                       ┌─────────────┴────────┴──────────────┐
                       │  sdd-dashboard MCP server (Bun)      │
                       │  • StdioServerTransport ⇄ Claude     │
                       │  • Bun.serve() HTTP+WS ⇄ browser     │
                       │  • reads/writes <PROJECT>/docs/ only │
                       │  • inbound: notifications/claude/    │
                       │      channel  (/sdd:<skill> <slug>)  │
                       │  • outbound: dashboard_* MCP tools   │
                       └──────────────────────────────────────┘
```

- `server.ts` — MCP server + `Bun.serve()`, lifecycle hygiene, project-root resolver, the JSON API.
- `state.ts` — disk → pipeline-stage derivation (the signal→stage table).
- `channel.ts` — outbound `dashboard_*` tools + the inbound command allowlist.
- `paths.ts` — `docs/` containment + extension allowlist.
- `../dashboard/` — the static UI (vanilla JS) + vendored render libs (`marked`, `mermaid`, `redoc`).

**Deferred (designed, not built):** live `fs.watch` updates (so terminal-driven runs also refresh the
dashboard) and multi-session parallelization (a shared hub with leader election). The MVP's choices —
token per session, `session_id`-tagged WS frames, `/sdd:start` project handover — are already
hub-compatible.
