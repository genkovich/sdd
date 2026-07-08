#!/usr/bin/env bash
# SDD installer for Codex CLI and Cursor (Claude Code installs natively via /plugin).
#
# SKILL.md is the open Agent Skills format, so both tools run the repo's skills unchanged.
# The script copies the skills/ + agents/ subtree VERBATIM under <skills-root>/sdd/ (the
# relative cross-links between skills, _shared/ and agents/ keep resolving by construction),
# prefixes every skill name with `sdd-` (the bare review/design/api would collide with
# generic names), and generates the host tool's functional agents from agents/*.md.
# How each Claude-specific mechanism maps: skills/_shared/tool-adapters.md.
#
# Usage:
#   install.sh <codex|cursor|claude> --src DIR [--global] [--prefix DIR] [--uninstall]
#
#   codex | cursor   target tool (claude just prints the native /plugin commands)
#   --src DIR        install from a local checkout (REQUIRED — this fork installs from a
#                    vetted local tree only; there is no network download path)
#   --global         install under $HOME instead of the current directory
#   --prefix DIR     install under DIR (overrides --global and $PWD; mainly for testing)
#   --uninstall      remove a previous install from the chosen prefix and exit
#
# Dependencies: python3 only for Codex custom agents (optional — without it the skills
# still install and agent dispatch degrades to inline). No network access, ever.

set -euo pipefail

log()  { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

TOOL=""
PREFIX=""
GLOBAL=0
SRC=""
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    codex|cursor|claude) TOOL="$1" ;;
    --global)    GLOBAL=1 ;;
    --prefix)    shift; PREFIX="${1:?--prefix needs a directory}" ;;
    --src)       shift; SRC="${1:?--src needs a directory}" ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help)   usage; exit 0 ;;
    *) usage; die "unknown argument: $1" ;;
  esac
  shift
done

[ -n "$TOOL" ] || { usage; die "missing target tool: codex | cursor | claude"; }

if [ "$TOOL" = "claude" ]; then
  cat <<'EOF'
SDD installs natively in Claude Code — run inside a Claude Code session:

  /plugin marketplace add genkovich/sdd
  /plugin install sdd@sdd
EOF
  exit 0
fi

if [ -z "$PREFIX" ]; then
  if [ "$GLOBAL" = 1 ]; then PREFIX="$HOME"; else PREFIX="$PWD"; fi
fi

case "$TOOL" in
  codex)  SKILLS_ROOT="$PREFIX/.agents/skills"; AGENTS_DIR="$PREFIX/.codex/agents" ;;
  cursor) SKILLS_ROOT="$PREFIX/.cursor/skills"; AGENTS_DIR="$PREFIX/.cursor/agents" ;;
esac

# --- idempotent clean (also the uninstall path) ------------------------------------------
rm -rf "${SKILLS_ROOT:?}/sdd"
rm -f "$AGENTS_DIR"/sdd-*.toml "$AGENTS_DIR"/sdd-*.md

if [ "$UNINSTALL" = 1 ]; then
  log "uninstalled sdd from $PREFIX ($TOOL)"
  exit 0
fi

# --- resolve the source tree -------------------------------------------------------------
# This fork installs from a vetted LOCAL checkout only — there is no network download path.
# cleanup also rolls back a PARTIAL install: if the script dies after the copy started but
# before the summary (INSTALL_DONE=1), the half-copied tree + generated agents are removed —
# the prefix is left clean, not with a silently broken install.
INSTALL_DONE=0
cleanup() {
  if [ "$INSTALL_DONE" != 1 ]; then
    rm -rf "${SKILLS_ROOT:?}/sdd"
    rm -f "$AGENTS_DIR"/sdd-*.toml "$AGENTS_DIR"/sdd-*.md
  fi
}
trap cleanup EXIT

[ -n "$SRC" ] \
  || die "--src DIR is required — install from a local checkout, e.g. ./install.sh $TOOL --src ."
[ -f "$SRC/skills/specify/SKILL.md" ] \
  || die "source $SRC does not look like the sdd repo (skills/specify/SKILL.md missing)"

# --- collision check: a marketplace install would list every skill twice ------------------
# `codex plugin marketplace add` registers the ORIGINAL names ($specify); this script installs
# the sdd- prefixed copies. Both at once → a doubled skill list. Warn, don't block (README:
# "pick one of the two paths").
if [ "$TOOL" = "codex" ] && [ -f "$HOME/.codex/config.toml" ] \
   && grep -q 'plugins."sdd@' "$HOME/.codex/config.toml" 2>/dev/null; then
  warn "a marketplace install of sdd is already registered in ~/.codex/config.toml — adding the script install too will list each skill twice (\$specify AND \$sdd-specify); pick one path (see README), or remove the marketplace plugin"
fi

# --- copy the subtree verbatim: <skills-root>/sdd/{skills,agents} ------------------------
mkdir -p "$SKILLS_ROOT/sdd"
cp -R "$SRC/skills" "$SKILLS_ROOT/sdd/skills"
cp -R "$SRC/agents" "$SKILLS_ROOT/sdd/agents"

# --- rename pass: frontmatter `name: <base>` → `name: sdd-<base>` ------------------------
# The repo validator guarantees the exact line `name: <dirname>` AND that every skill dir name
# matches [a-z0-9-]+ (no BRE metacharacters), so interpolating $base into the sed pattern is
# safe on both GNU and BSD sed. A new skill with ./_+ etc. in its dir name would break this —
# the validator rejects it first.
n_skills=0
for skill_md in "$SKILLS_ROOT"/sdd/skills/*/SKILL.md; do
  base="$(basename "$(dirname "$skill_md")")"
  tmp="${skill_md}.tmp"
  sed "s/^name: ${base}\$/name: sdd-${base}/" "$skill_md" > "$tmp"
  grep -q "^name: sdd-${base}\$" "$tmp" \
    || die "rename failed for $skill_md (expected the exact line 'name: ${base}')"
  mv "$tmp" "$skill_md"
  n_skills=$((n_skills + 1))
done

# --- functional agents per tool -----------------------------------------------------------
# (the verbatim copies under sdd/agents/ stay as documentation the skills cross-link)
mkdir -p "$AGENTS_DIR"
n_agents=0

if [ "$TOOL" = "cursor" ]; then
  for agent_md in "$SRC"/agents/*.md; do
    n="$(basename "$agent_md" .md)"
    out="$AGENTS_DIR/sdd-${n}.md"
    # rewrite two frontmatter lines only: the name (prefix) and the model (host-agnostic)
    sed -e "1,/^---\$/ s/^name: ${n}\$/name: sdd-${n}/" \
        -e "1,/^---\$/ s/^model: .*/model: inherit/" \
        "$agent_md" > "$out"
    grep -q "^name: sdd-${n}\$" "$out" \
      || die "agent rewrite failed for $agent_md (expected the exact line 'name: ${n}')"
    n_agents=$((n_agents + 1))
  done
else # codex: generate .codex/agents/sdd-<name>.toml (needs python3 — folded YAML description)
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$SRC/agents" "$AGENTS_DIR" <<'PYEOF'
import functools
import json
import sys
from pathlib import Path

dumps = functools.partial(json.dumps, ensure_ascii=False)
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
for md in sorted(src.glob("*.md")):
    text = md.read_text()
    if not text.startswith("---"):
        sys.exit(f"{md}: no frontmatter")
    end = text.find("\n---", 3)
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")

    # parse the scalar keys + the folded `description: >` block (no yaml module in stdlib)
    fm, desc_lines, in_desc = {}, [], False
    for line in block.splitlines():
        if in_desc:
            if line.startswith((" ", "\t")):
                desc_lines.append(line.strip())
                continue
            in_desc = False
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if key == "description" and val in (">", "|", ">-", "|-"):
                in_desc = True
            else:
                fm[key] = val

    desc = fm.get("description") or " ".join(desc_lines)
    name = "sdd-" + fm["name"]
    tools = fm.get("tools", "")
    writes = any(t.strip() in ("Write", "Edit") for t in tools.split(","))
    sandbox = "workspace-write" if writes else "read-only"

    if not body.endswith("\n"):
        body += "\n"
    if "'''" in body:  # can't hold a TOML literal multi-line string — escape via JSON form
        instructions = "developer_instructions = " + dumps(body)
    else:
        instructions = "developer_instructions = '''\n" + body + "'''"

    toml = (
        f"name = {dumps(name)}\n"
        f"description = {dumps(desc)}\n"
        f"sandbox_mode = {dumps(sandbox)}\n"
        f"{instructions}\n"
    )
    (dst / f"{name}.toml").write_text(toml)
    print(f"  agent {name}.toml")
PYEOF
    n_agents="$(find "$AGENTS_DIR" -name 'sdd-*.toml' | wc -l | tr -dc '0-9')"
  else
    warn "python3 not found — skipping Codex custom agents; skills install anyway and agent dispatch degrades to inline (see sdd/skills/_shared/agent-roster.md)"
  fi
fi

# --- summary -------------------------------------------------------------------------------
INSTALL_DONE=1
log ""
log "installed sdd ($TOOL):"
log "  skills  → $SKILLS_ROOT/sdd  (${n_skills} skills)"
if [ "$n_agents" -gt 0 ]; then
  log "  agents  → $AGENTS_DIR  (${n_agents} agents, sdd-* prefixed)"
fi
case "$TOOL" in
  codex)  log "  invoke  → type \$sdd-… in codex, e.g. \$sdd-specify <slug>" ;;
  cursor) log "  invoke  → type / in the chat and pick sdd-…, e.g. sdd-specify" ;;
esac
log "  mapping → $SKILLS_ROOT/sdd/skills/_shared/tool-adapters.md"
log "  remove  → re-run with --uninstall (re-running install is also safe: it cleans first)"
