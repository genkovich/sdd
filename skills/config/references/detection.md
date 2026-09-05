# Host detection — the signals, ranked, and the rule that they are never enough

> **Reference-only.** Read by [`../SKILL.md`](../SKILL.md) step 4. Which tool is running the
> session decides whether three settings keys are usable at all: `team_mode` and `workflow_mode`
> ride `TeamCreate` / `Workflow`, and `max_parallel_agents` only means something when one of them
> can run. Both mechanisms are **Claude Code-only** — on Codex CLI and Cursor the engine degrades
> to sequential single-agent TDD ([`../../_shared/tool-adapters.md`](../../_shared/tool-adapters.md)).

## The rule

**A guess is evidence for a question, never an answer.** State which signals you saw, what they
point at, and how confident that makes you — then ask. The confirmed answer is what gets written.

**Contradictory traces are named out loud.** A repo can carry install artifacts from a tool nobody
uses here any more; two tools can share one checkout. When signals disagree, say which ones
disagree and let the user settle it — a tidy single guess built on a conflict is the failure this
rule exists to prevent. The pattern is the same one `design-system` uses to detect design-tool
MCPs: probe, report, ask.

## Signals, strongest first

| # | Signal | How to read it |
|---|---|---|
| 1 | **The invocation form the user typed** | `/sdd:config` → Claude Code · `$sdd-config` → Codex CLI · picked `sdd-config` from the `/` menu → Cursor. The strongest signal there is: it is the host speaking, in this session, right now. |
| 2 | **Is `AskUserQuestion` available at all?** | Present → Claude Code. Absent → not Claude Code, and the six questions are asked as **numbered plain text, one at a time, stop and wait** ([`../../_shared/ask-style.md`](../../_shared/ask-style.md)). A missing native tool is never a reason to skip a question or answer it for the user. |
| 2b | **`# set by install.sh (<tool>)` comments inside the settings file** | The installer writes the host-correct `team_mode` / `workflow_mode` / `max_parallel_agents` and stamps each with the tool it ran for. Present → that tool installed here, and those three keys are already clamped: confirm rather than re-clamp, and never present them as if the user had chosen them. |
| 3 | **Install directories written by `install.sh`** | `.agents/skills/sdd/` plus `sdd-`prefixed `.toml` agents under `.codex/agents/` → the Codex install ran here. `.cursor/skills/sdd/` plus `sdd-`prefixed `.md` agents under `.cursor/agents/` → the Cursor install ran here. Strong, but historical: the directory outlives the tool that made it. |
| 4 | **`~/.codex/config.toml`** | Exists → Codex CLI is installed on this machine. A `plugins."sdd@…"` entry means the marketplace install path was used. Machine-level, not session-level — it says what is installed, not what is running. |
| 5 | **A `CLAUDE.md` in the repo** | The **weakest** signal, and easy to over-read: `.claude/` is an ordinary directory under Codex and Cursor too (they read the repo's files with their own file tools — [`../../_shared/tool-adapters.md`](../../_shared/tool-adapters.md)), and plenty of repos carry a `CLAUDE.md` that no Claude session has opened in months. Never decide on this alone. |

## What the answer changes

| Confirmed host | Clamps applied and stated |
|---|---|
| Claude Code | none — `team_mode`, `workflow_mode` and `max_parallel_agents` are asked normally |
| Codex CLI · Cursor · anything else | `team_mode: false` · `workflow_mode: off` · `max_parallel_agents: 1` — written as **derived, not asked**, with the reason: `TeamCreate` and `Workflow` do not exist here, so the engine runs sequential single-agent TDD, which is the documented floor everything degrades to anyway |

The clamp is a **write**, so it appears in the `old → new` output like any other change — but in the
*derived* list, never mixed in with what the user chose.
