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

    VALID_MODELS = {"haiku", "sonnet", "opus", "inherit"}
    VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
    agent_names = {p.stem for p in (ROOT / "agents").glob("*.md")}

    def parse_list(v: str) -> list[str]:
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = v[1:-1]
        return [x.strip() for x in v.split(",") if x.strip()]

    def check_profile(label: str, fm: dict, require: bool):
        """Validate model/effort/agents attributes if present (required on skills)."""
        m, e = fm.get("model"), fm.get("effort")
        if require:
            check(m is not None, f"{label} declares model", f"{label} is missing the model attribute")
            check(e is not None, f"{label} declares effort", f"{label} is missing the effort attribute")
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
        check_profile(f"skill '{base}'", fm, require=True)
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
    # legit /sdd- in the tree is the proof-run branch ref proof/sdd-notification-preferences. We scan
    # docs + the manifests (the v1.8.4 sweep missed plugin.json's description — that gap stays closed).
    print("== invocation form ==")
    SDD_HYPHEN = re.compile(r"(?<!proof)/sdd-")
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
    # Cheap, robust proxy: the SKILL.md's final step points at _shared/handoff.md.
    print("== handoff block ==")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check("handoff.md" in skill_md.read_text(),
              f"skill '{base}' points at the stage-handoff block (_shared/handoff.md)",
              f"skill '{base}' SKILL.md never references _shared/handoff.md — every stage must end with the handoff block")

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

    # --- no orphan in _shared/: every shared reference is pointed to by >=1 file ---
    print("== _shared no-orphan ==")
    for sf in sorted((ROOT / "skills" / "_shared").glob("*.md")):
        referrers = [p for p in doc_pool if p != sf and sf.name in p.read_text()]
        check(bool(referrers),
              f"_shared/{sf.name} is referenced by {len(referrers)} file(s)",
              f"_shared/{sf.name} is an orphan — nothing under skills/ or agents/ points to it")

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
