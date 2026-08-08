#!/usr/bin/env python3
"""Validate the SDD Claude Code plugin.

Checks the plugin manifest + marketplace manifest agree on name / version / description,
that the version is semver, and that every triggering skill and agent carries the required
frontmatter. Run from the repo root:

    python3 scripts/validate_plugin.py

Exits non-zero on the first category of failures (CI gate). Prints one line per check.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

errors: list[str] = []
checks = 0


def check(ok: bool, ok_msg: str, fail_msg: str) -> bool:
    global checks
    checks += 1
    if ok:
        print(f"  ok   {ok_msg}")
    else:
        print(f"  FAIL {fail_msg}")
        errors.append(fail_msg)
    return ok


def load_json(rel: str):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"{rel} is missing")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{rel} is not valid JSON: {exc}")
        return None


def read_frontmatter(path: Path) -> dict[str, str]:
    """Return the top-level scalar keys of a leading --- YAML frontmatter block."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fm: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def main() -> int:
    print("== manifests ==")
    plugin = load_json(".claude-plugin/plugin.json")
    market = load_json(".claude-plugin/marketplace.json")
    if plugin is None or market is None:
        for e in errors:
            print(f"  FAIL {e}")
        print(f"\nFAILED: {len(errors)} error(s)")
        return 1

    # --- plugin.json: name / version / description ---
    name = plugin.get("name", "")
    version = plugin.get("version", "")
    desc = plugin.get("description", "")
    check(name == "sdd", "plugin name is 'sdd'", f"plugin name is {name!r}, expected 'sdd'")
    check(bool(SEMVER.match(version)), f"plugin version {version!r} is semver", f"plugin version {version!r} is not semver X.Y.Z")
    check(len(desc) >= 50, f"plugin description present ({len(desc)} chars)", f"plugin description too short ({len(desc)} chars)")
    check(bool(plugin.get("license")), "plugin declares a license", "plugin.json has no license")
    auth = plugin.get("author")
    auth_name = auth if isinstance(auth, str) else (auth.get("name") if isinstance(auth, dict) else None)
    check(bool(auth_name), "plugin declares an author", "plugin.json has no author")

    # --- manifest schema FIELD TYPES (Claude Code's loader rejects wrong types) ---
    repo = plugin.get("repository")
    check(repo is None or isinstance(repo, str),
          "plugin repository is a string (or absent)",
          "plugin.json `repository` must be a STRING URL, not an object {type,url} — Claude Code's manifest schema rejects the object form")
    check(plugin.get("homepage") is None or isinstance(plugin.get("homepage"), str),
          "plugin homepage is a string (or absent)", "plugin.json `homepage` must be a string")
    check(auth is None or isinstance(auth, (str, dict)),
          "plugin author is a string or object (or absent)", "plugin.json `author` must be a string or object")

    # --- marketplace.json: agrees with plugin.json on name / version / description ---
    print("== marketplace ==")
    plugins = market.get("plugins", [])
    entry = next((p for p in plugins if p.get("name") == "sdd"), None)
    if check(entry is not None, "marketplace lists the 'sdd' plugin", "marketplace.json has no plugin named 'sdd'"):
        check(entry.get("version") == version,
              f"marketplace version matches plugin.json ({version})",
              f"marketplace version {entry.get('version')!r} != plugin.json {version!r}")
        check(bool(entry.get("description")), "marketplace entry has a description", "marketplace 'sdd' entry has no description")
        check(bool(entry.get("source")), "marketplace entry has a source", "marketplace 'sdd' entry has no source")

    # --- cross-tool manifests: the Codex + Cursor mirrors carry the same name + version ---
    # v1.9.0 ships .codex-plugin/ + .agents/plugins/ (Codex CLI) and .cursor-plugin/ (Cursor);
    # a version bump that misses one of them would silently publish a stale manifest.
    print("== cross-tool manifests ==")

    def load_tool_manifest(rel: str):
        path = ROOT / rel
        if not check(path.exists(), f"{rel} exists", f"{rel} is missing"):
            return None
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            check(False, "", f"{rel} is not valid JSON: {exc}")
            return None

    for rel in (".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        data = load_tool_manifest(rel)
        if data is None:
            continue
        check(data.get("name") == "sdd", f"{rel} name is 'sdd'",
              f"{rel} name is {data.get('name')!r}, expected 'sdd'")
        check(data.get("version") == version,
              f"{rel} version matches plugin.json ({version})",
              f"{rel} version {data.get('version')!r} != plugin.json {version!r}")

    codex_market = load_tool_manifest(".agents/plugins/marketplace.json")
    if codex_market is not None:
        check(codex_market.get("name") == "sdd",
              ".agents marketplace name is 'sdd'",
              f".agents marketplace name is {codex_market.get('name')!r}, expected 'sdd'")
        cm_entry = next((p for p in codex_market.get("plugins", []) if p.get("name") == "sdd"), None)
        check(cm_entry is not None and bool(cm_entry.get("source")),
              ".agents marketplace lists the 'sdd' plugin with a source",
              ".agents/plugins/marketplace.json has no 'sdd' plugin entry with a source")
        # Codex CANNOT install a plugin whose local path is the marketplace root: it strips `./`
        # and rejects the empty remainder (codex-rs marketplace.rs, resolve_local_plugin_source_path)
        # — the entry is silently skipped and the marketplace lists zero plugins. The self-marketplace
        # therefore must use the git `url` object form pointing back at this repo.
        cm_src = (cm_entry or {}).get("source")
        check(isinstance(cm_src, dict) and cm_src.get("source") == "url"
              and str(cm_src.get("url", "")).startswith("https://github.com/"),
              ".agents marketplace 'sdd' source is the git url form (root-local './' is uninstallable in codex)",
              f".agents marketplace 'sdd' source must be {{'source': 'url', 'url': 'https://github.com/…'}} — "
              f"codex silently skips a root-local './' plugin; got {cm_src!r}")

    installer = ROOT / "install.sh"
    check(installer.exists() and installer.read_text().startswith("#!/usr/bin/env bash"),
          "install.sh exists and is a bash script (#!/usr/bin/env bash)",
          "install.sh is missing or lacks the #!/usr/bin/env bash shebang")

    VALID_MODELS = {"haiku", "sonnet", "opus", "fable", "inherit"}
    VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
    agent_names = {p.stem for p in (ROOT / "agents").glob("*.md")}

    def parse_list(v: str) -> list[str]:
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = v[1:-1]
        return [x.strip() for x in v.split(",") if x.strip()]

    def check_profile(label: str, fm: dict, require: bool, require_agents: bool = False):
        """Validate model/effort/agents attributes if present (required on skills)."""
        m, e = fm.get("model"), fm.get("effort")
        if require:
            check(m is not None, f"{label} declares model", f"{label} is missing the model attribute")
            check(e is not None, f"{label} declares effort", f"{label} is missing the effort attribute")
        if require_agents:
            check(fm.get("agents") is not None,
                  f"{label} declares agents",
                  f"{label} is missing the agents attribute (use `agents: []` when it spawns none)")
        if m is not None:
            check(m in VALID_MODELS or "-" in m or "." in m,
                  f"{label} model {m!r} is valid", f"{label} model {m!r} not in {sorted(VALID_MODELS)} or a full id")
        if e is not None:
            check(e in VALID_EFFORTS or e.isdigit(),
                  f"{label} effort {e!r} is valid", f"{label} effort {e!r} not in {sorted(VALID_EFFORTS)} or a number")
        ag = fm.get("agents")
        if ag is not None:
            for a in parse_list(ag):
                check(a in agent_names, f"{label} → agent '{a}' exists",
                      f"{label} references agent '{a}' with no agents/{a}.md")

    # --- skills: every trigger skill has name + description + model/effort/agents profile ---
    print("== skills ==")
    skills_dir = ROOT / "skills"
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        base = skill_md.parent.name
        if base == "_shared":
            check(False, "", "skills/_shared must not contain SKILL.md (it would register as a skill)")
            continue
        fm = read_frontmatter(skill_md)
        check(fm.get("name") == base,
              f"skill '{base}' has matching name frontmatter",
              f"skill '{base}': frontmatter name is {fm.get('name')!r}, expected {base!r}")
        check(len(fm.get("description", "")) >= 30 or "description" in _block_keys(skill_md),
              f"skill '{base}' has a description",
              f"skill '{base}' has no/short description")
        check_profile(f"skill '{base}'", fm, require=True, require_agents=True)
        # Skill frontmatter executes BEFORE any settings are read — a skill that pins an
        # entitlement-gated tier hard-fails at skill start for every account without that tier
        # (proven by the 1140b0c-era hard-fail). Judgment tier lives on the AGENTS + judgment_model.
        check(fm.get("model") not in ("opus", "fable"),
              f"skill '{base}' does not pin an entitlement-gated model tier",
              f"skill '{base}' frontmatter pins model: {fm.get('model')} — skill frontmatter runs "
              f"before settings, so accounts without that tier hard-fail; use `model: inherit` "
              f"(judgment quality belongs to the agents / judgment_model)")
    check((skills_dir / "_shared").is_dir() and not (skills_dir / "_shared" / "SKILL.md").exists(),
          "_shared is reference-only (no SKILL.md)",
          "_shared is missing or contains a SKILL.md")

    # --- agents: name + description ---
    print("== agents ==")
    for agent_md in sorted((ROOT / "agents").glob("*.md")):
        fm = read_frontmatter(agent_md)
        check(bool(fm.get("name")), f"agent '{agent_md.stem}' has a name", f"agent '{agent_md.name}' has no name frontmatter")
        check("description" in _block_keys(agent_md), f"agent '{agent_md.stem}' has a description", f"agent '{agent_md.name}' has no description")
        check_profile(f"agent '{agent_md.stem}'", fm, require=True)

    # === semantic + consistency invariants (the checks a human ran by hand each change) ===
    # The groups above check structure (manifests agree, frontmatter valid). These check the
    # conventions the plugin actually relies on: doc links resolve, the invocation form is right,
    # every stage ends with its handoff block, the surface taxonomy is single-source, and no
    # _shared/ file lost all its referrers. Structure passing != the conventions holding.
    skill_glob = sorted((ROOT / "skills").rglob("*.md"))
    skill_specs = sorted((ROOT / "skills").glob("*/SKILL.md"))
    doc_pool = skill_glob + sorted((ROOT / "agents").glob("*.md"))

    # --- skill count in prose: README + the 4 manifests state the REAL skill count ---
    # The "N atomic" phrase is marketing prose that silently rots when a skill is added;
    # every file that carries it must agree with the actual number of skills/*/SKILL.md.
    print("== skill count in prose ==")
    n_skills = len(skill_specs)
    ATOMIC_RE = re.compile(r"\b(\d+) atomic")
    for rel in ("README.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        counts = ATOMIC_RE.findall((ROOT / rel).read_text())
        check(bool(counts) and all(int(c) == n_skills for c in counts),
              f"{rel} states the real skill count ({n_skills} atomic)",
              f"{rel} must say '{n_skills} atomic …' to match the {n_skills} skills/*/SKILL.md "
              f"(found: {counts if counts else 'no `N atomic` phrase'})")

    # --- markdown relative links resolve (replaces the per-change manual link sweep) ---
    # Only *.md / dir targets are resolved (the doc cross-references). Skipped: http(s), #anchors,
    # any <placeholder> target, and the template-runtime paths that resolve ONLY inside a generated
    # docs/features/<slug>/ folder (the skills/*/templates/ scaffolds link to those).
    print("== links ==")
    LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    LINK_ALLOW = {"./CONTEXT.md", "../spec.md", "../sad.md", "../data-model.md", "../tasks.json"}
    LINK_ALLOW_PREFIX = ("../contracts/", "../adr/", "./features/")
    link_files = sorted(set(skill_glob + sorted((ROOT / "agents").glob("*.md")) + [ROOT / "README.md"]))
    n_links = 0
    broken: list[str] = []
    for f in link_files:
        for m in LINK_RE.finditer(f.read_text()):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://")) or target.startswith("#"):
                continue
            if "<" in target:                        # placeholder, e.g. docs/features/<slug>/…
                continue
            path_part = target.split("#", 1)[0]
            if not path_part or not (path_part.endswith(".md") or path_part.endswith("/")):
                continue                             # only doc (*.md) + dir links are resolvable here
            if path_part in LINK_ALLOW or path_part.startswith(LINK_ALLOW_PREFIX):
                continue                             # template-runtime: resolves only in a feature folder
            n_links += 1
            if not (f.parent / path_part).exists():
                broken.append(f"{f.relative_to(ROOT)} → {target}")
    check(not broken,
          f"all {n_links} relative doc links resolve (template-runtime paths allowlisted)",
          "broken relative links (real *.md/dir target missing, not template-runtime):\n        "
          + "\n        ".join(broken))

    # --- invocation form: the namespaced /sdd:<name>, never the hyphenated /sdd-<name> ---
    # The plugin ships skills (no commands/ dir), so Claude Code invokes them /sdd:<name>. The only
    # legit /sdd- in the tree is the proof-run branch ref proof/sdd-notification-preferences and the
    # `sdd-dashboard` MCP server / `~/.claude/sdd-dashboard/` state dir (a server name, not an
    # invocation). We scan docs + the manifests (the v1.8.4 sweep missed plugin.json's description —
    # that gap stays closed).
    print("== invocation form ==")
    SDD_HYPHEN = re.compile(r"(?<!proof)/sdd-(?!dashboard)")
    form_files = link_files + [ROOT / ".claude-plugin" / "plugin.json", ROOT / ".claude-plugin" / "marketplace.json"]
    offenders: list[str] = []
    for f in sorted(set(form_files)):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if SDD_HYPHEN.search(line):
                offenders.append(f"{f.relative_to(ROOT)}:{i}")
    check(not offenders,
          "invocation form is namespaced /sdd:<name> everywhere (no hyphenated /sdd-)",
          "found the stale hyphenated /sdd- form (use /sdd:<name>) at: " + ", ".join(offenders))

    # --- every stage ends with the handoff block (the v1.8.1 output contract) ---
    # The phrase «stage-handoff block» is the contract wording every spine's final step uses;
    # a bare `handoff.md` substring (e.g. in a passing mention) is not enough to prove the
    # skill actually ends with the block.
    print("== handoff block ==")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check("stage-handoff block" in skill_md.read_text(),
              f"skill '{base}' emits the stage-handoff block (the literal phrase is present)",
              f"skill '{base}' SKILL.md never says 'stage-handoff block' — every stage must end with «emit the stage-handoff block per _shared/handoff.md»")

    # --- every skill verifies its own output (the structural self-check contract) ---
    # _shared/self-check.md defines the contract; every SKILL.md either runs a named checklist
    # or maps its heavy verifier (critic/reviewer/drift/mermaid/GATE) onto it — the literal
    # phrase «structural self-check» is the greppable evidence, same mechanism as the
    # stage-handoff check above.
    print("== structural self-check ==")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check("structural self-check" in skill_md.read_text().lower(),
              f"skill '{base}' names its structural self-check",
              f"skill '{base}' SKILL.md never says 'structural self-check' — every skill must run "
              f"the checklist (or map its heavy verifier) per _shared/self-check.md")

    # --- skill dir names are BRE-safe (install.sh interpolates them into a sed pattern) ---
    print("== skill dir names ==")
    DIRNAME_RE = re.compile(r"^[a-z0-9-]+$")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check(bool(DIRNAME_RE.match(base)),
              f"skill dir '{base}' matches ^[a-z0-9-]+$",
              f"skill dir '{base}' must match ^[a-z0-9-]+$ — install.sh interpolates the dir name into a sed (BRE) pattern, so a dot/underscore/+ would break the rename pass")

    # --- cross-tool mechanism coverage: every Claude mechanism a spine uses is mapped ---
    # tool-adapters.md is the single Codex/Cursor mapping table; a spine that starts using a
    # new Claude-specific mechanism without a row there strands non-Claude users.
    print("== cross-tool mechanism coverage ==")
    adapters_text = (ROOT / "skills" / "_shared" / "tool-adapters.md").read_text()
    MECHANISMS = ["AskUserQuestion", "TeamCreate", "Workflow", "subagent_type", "/clear"]
    for mech in MECHANISMS:
        used_in = [s.parent.name for s in skill_specs if mech in s.read_text()]
        if not used_in:
            continue  # no spine uses it — nothing to map
        check(mech in adapters_text,
              f"mechanism '{mech}' (used by {len(used_in)} skill(s)) is mapped in tool-adapters.md",
              f"mechanism '{mech}' is used by {', '.join(sorted(used_in))} but has no row in _shared/tool-adapters.md — Codex/Cursor users get no mapping for it")

    # --- the surface taxonomy is single-source in _shared/surfaces.md (DRY) ---
    # The two canonical tables (the taxonomy + the per-skill gating table) live ONLY here; a SKILL.md
    # that copies a header row has duplicated the source of truth (surfaces.md's own discipline rule).
    print("== taxonomy single-source ==")
    surfaces_text = (ROOT / "skills" / "_shared" / "surfaces.md").read_text()
    TAXONOMY_ROWS = [
        "| Surface | `api` contract form |",             # the per-skill gating table
        "| Surface | What it is (the C4 container) |",    # the surface taxonomy table
    ]
    for row in TAXONOMY_ROWS:
        dups = [str(s.relative_to(ROOT)) for s in skill_specs if row in s.read_text()]
        check(row in surfaces_text and not dups,
              f"taxonomy row `{row} …` is single-source in _shared/surfaces.md",
              (f"taxonomy row `{row} …` is duplicated in a SKILL.md (must live only in _shared/surfaces.md): "
               + ", ".join(dups)) if dups
              else f"taxonomy row `{row} …` is missing from _shared/surfaces.md (did it move/rename?)")

    # --- architecture-map template shape: the machine-readable keys survey fills ---
    # implement's command-detection cascade reads test_cmd/lint_cmd from the map frontmatter and
    # design/others key freshness off reflects_commit — the template must keep declaring them.
    print("== architecture-map template ==")
    amap = ROOT / "skills" / "survey" / "templates" / "architecture-map.md"
    amap_fm = _block_keys(amap)
    for key in ("test_cmd", "reflects_commit"):
        check(key in amap_fm,
              f"architecture-map template frontmatter declares `{key}`",
              f"skills/survey/templates/architecture-map.md frontmatter lost the `{key}` key — "
              f"command-detection / staleness checks read it")

    # --- model policy consistency: judgment_model is documented everywhere it matters ---
    # The judgment_model settings key (open value-set switch for the judgment agents) is defined in
    # the settings doc, consumed per agent-roster's precedence, and surfaced to users in the README —
    # if any file drops the mention, the policy silently forks. Both policy files must also carry
    # the "floor" rule (default-is-a-floor: never silently downgrade judgment below the session),
    # so the rule can't vanish from one of them.
    print("== model policy ==")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/agent-roster.md",
                "README.md"):
        check("judgment_model" in (ROOT / rel).read_text(),
              f"{rel} documents judgment_model",
              f"{rel} never mentions 'judgment_model' — the settings doc, the roster policy and the README must all carry it")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/agent-roster.md"):
        check("floor" in (ROOT / rel).read_text().lower(),
              f"{rel} carries the judgment_model floor rule",
              f"{rel} never says 'floor' — the default-is-a-floor rule (no silent judgment downgrade below the session) must stay in both policy files")

    # --- artifact language: the key is defined + the rule is threaded through every writer ---
    # The artifact_language settings key (en|uk prose switch for pipeline documents) is defined in
    # the settings doc and its rule lives in _shared/artifact-language.md — if either drops the
    # mention, the policy silently forks. And every artifact-writing skill must point at the shared
    # rule; a dropped pointer means that skill's documents silently revert to always-English.
    print("== artifact language ==")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/artifact-language.md"):
        check("artifact_language" in (ROOT / rel).read_text(),
              f"{rel} documents artifact_language",
              f"{rel} never mentions 'artifact_language' — the settings doc and the shared rule must both carry it")
    ARTIFACT_WRITERS = ("specify", "clarify", "glossary", "design", "decide-adr", "sequences",
                        "data-model", "api", "tasks", "plan-tests", "review", "ship", "fix",
                        "roadmap", "survey")
    for name in ARTIFACT_WRITERS:
        check("artifact-language.md" in (ROOT / "skills" / name / "SKILL.md").read_text(),
              f"skills/{name}/SKILL.md points at _shared/artifact-language.md",
              f"skills/{name}/SKILL.md never mentions 'artifact-language.md' — every artifact-writing "
              f"skill must carry the language pointer")

    # --- the route table is single-source in _shared/size-matrix.md + `.route` is threaded ---
    # The Routes table (quick/standard/full handoff behaviour) lives ONLY in size-matrix.md;
    # and the `.route` artifact must be named by the files that write/consume it — a rename or
    # a dropped mention silently reverts the pipeline to always-standard.
    print("== routes ==")
    size_matrix_text = (ROOT / "skills" / "_shared" / "size-matrix.md").read_text()
    ROUTE_HEADER = "| Route | Handoff behaviour at an optional stage |"
    route_dups = [str(s.relative_to(ROOT)) for s in skill_specs if ROUTE_HEADER in s.read_text()]
    check(ROUTE_HEADER in size_matrix_text and not route_dups,
          "route table is single-source in _shared/size-matrix.md",
          (f"route table header is duplicated in a SKILL.md (must live only in _shared/size-matrix.md): "
           + ", ".join(route_dups)) if route_dups
          else "route table header is missing from _shared/size-matrix.md (did it move/rename?)")
    for rel in ("skills/_shared/size-matrix.md", "skills/_shared/handoff.md",
                "skills/classify-size/SKILL.md", "skills/specify/SKILL.md"):
        check('.route' in (ROOT / rel).read_text(),
              f"{rel} mentions the .route artifact",
              f"{rel} never mentions '.route' — it writes or resolves the route and must name the artifact")

    # --- no orphan in _shared/: every shared reference is pointed to by >=1 file ---
    print("== _shared no-orphan ==")
    for sf in sorted((ROOT / "skills" / "_shared").glob("*.md")):
        referrers = [p for p in doc_pool if p != sf and sf.name in p.read_text()]
        check(bool(referrers),
              f"_shared/{sf.name} is referenced by {len(referrers)} file(s)",
              f"_shared/{sf.name} is an orphan — nothing under skills/ or agents/ points to it")

    # === dashboard: .mcp.json + server/ + dashboard/ + the `start` handshake skill ===
    # The visual dashboard (the shipped "MCP exposure" feature) is opt-in but its files must
    # stay structurally sound: the MCP server is declared correctly, the server/dashboard
    # sources exist, the render libs are vendored (offline), and the `start` skill is the
    # documented handshake. A missing piece silently breaks `/sdd:start` for everyone who opts in.
    print("== dashboard (mcp server + ui) ==")
    mcp_path = ROOT / ".mcp.json"
    if check(mcp_path.exists(), ".mcp.json exists", ".mcp.json is missing (the dashboard MCP server is undeclared)"):
        try:
            mcp = json.loads(mcp_path.read_text())
        except json.JSONDecodeError as exc:
            mcp = None
            check(False, "", f".mcp.json is not valid JSON: {exc}")
        if mcp is not None:
            srv = (mcp.get("mcpServers") or {}).get("sdd-dashboard")
            check(isinstance(srv, dict),
                  ".mcp.json declares the 'sdd-dashboard' server",
                  ".mcp.json has no mcpServers.sdd-dashboard entry")
            if isinstance(srv, dict):
                check(srv.get("command") == "bun",
                      ".mcp.json sdd-dashboard launches with `bun`",
                      f".mcp.json sdd-dashboard command is {srv.get('command')!r}, expected 'bun'")
                args = srv.get("args") or []
                joined = " ".join(args) if isinstance(args, list) else str(args)
                check("${CLAUDE_PLUGIN_ROOT}/server" in joined,
                      ".mcp.json sdd-dashboard runs in ${CLAUDE_PLUGIN_ROOT}/server (not the plugin root)",
                      ".mcp.json sdd-dashboard args must `--cwd ${CLAUDE_PLUGIN_ROOT}/server` — cwd is the plugin dir, never the project")
                check("start" in args if isinstance(args, list) else False,
                      ".mcp.json sdd-dashboard invokes the `start` package script",
                      ".mcp.json sdd-dashboard args must end in the `start` script (bun run … start)")

    # server/ sources — the seven modules + the Bun package manifest.
    for rel in ("server/package.json", "server/server.ts", "server/state.ts",
                "server/channel.ts", "server/paths.ts", "server/http.ts",
                "server/frontmatter.ts", "server/watch.ts"):
        check((ROOT / rel).exists(), f"{rel} exists", f"{rel} is missing")
    # The server package must declare the MCP SDK dependency + a `start` script.
    spkg = ROOT / "server" / "package.json"
    if spkg.exists():
        try:
            pkg = json.loads(spkg.read_text())
            check("@modelcontextprotocol/sdk" in (pkg.get("dependencies") or {}),
                  "server/package.json depends on @modelcontextprotocol/sdk",
                  "server/package.json is missing the @modelcontextprotocol/sdk dependency")
            check(bool((pkg.get("scripts") or {}).get("start")),
                  "server/package.json defines a `start` script",
                  "server/package.json has no `start` script (the .mcp.json launch target)")
        except json.JSONDecodeError as exc:
            check(False, "", f"server/package.json is not valid JSON: {exc}")

    # dashboard/ UI + vendored render libs (vendored, not CDN — offline reliability).
    # mermaid stays vendored but is lazy-loaded by app.js (only when a ```mermaid
    # block is actually rendered); redoc was dropped with the read-only dashboard.
    for rel in ("dashboard/index.html", "dashboard/app.js", "dashboard/style.css",
                "dashboard/vendor/marked.min.js", "dashboard/vendor/mermaid.min.js"):
        check((ROOT / rel).exists(), f"{rel} exists", f"{rel} is missing")

    # The `start` skill — the documented handshake (auto-discovered as a skill above, but
    # its dashboard-specific contract must hold: it calls the handshake tool + gates on opt-in).
    start_md = ROOT / "skills" / "start" / "SKILL.md"
    if check(start_md.exists(), "skills/start/SKILL.md exists", "skills/start/SKILL.md is missing (the /sdd:start handshake)"):
        start_text = start_md.read_text()
        check("dashboard_handshake" in start_text,
              "skills/start references the dashboard_handshake tool",
              "skills/start/SKILL.md never mentions dashboard_handshake — the project-dir handover point")
        check("dashboard_enabled" in start_text,
              "skills/start gates on dashboard_enabled (opt-in)",
              "skills/start/SKILL.md never mentions dashboard_enabled — it must gate on the opt-in flag")

    print()
    if errors:
        print(f"FAILED: {len(errors)} error(s) out of {checks} checks")
        return 1
    print(f"PASSED: {checks} checks")
    return 0


def _block_keys(path: Path) -> set[str]:
    """Keys present in the frontmatter, including multi-line (folded) ones like `description: >`."""
    text = path.read_text()
    if not text.startswith("---"):
        return set()
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else ""
    return {m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", block, re.M)}


if __name__ == "__main__":
    sys.exit(main())
