# Greenfield foundation — calibrate, pick, fix, scaffold

When `survey` detects an empty repo, it doesn't write «greenfield — nothing here». It runs a short
session to **establish the foundation** so the per-feature flow has something real to build into,
then hands a skeleton to `implement`. The session is **adaptive to the person** — gauge their level
once, then meet them there.

## G2 — Calibrate (one question, sets everything after)

Open with a single `AskUserQuestion` that gauges how the user wants to engage (and implicitly their level). Phrase it warmly, per [`../../_shared/ask-style.md`](../../_shared/ask-style.md):

- **«Pick good defaults, I'll confirm»** → *guided-default* depth: propose a complete coherent foundation, ask **one** confirm, explain each piece in plain language. Best for a first-timer / non-engineer / "just get me going".
- **«Walk me through each choice with explanations»** → *guided-explained* depth: one question per major choice, each option glossed (no jargon without a plain-words explanation). Best for a junior who wants to learn the why.
- **«Let me choose each piece, keep it terse»** → *expert* depth: offer the choices without the long explanations, accept overrides freely. Best for a senior.

Calibration governs **depth + phrasing**, not the set of decisions — the same foundation gets fixed either way. Default to *guided-default* if the answer is ambiguous (over-explaining is cheaper than overwhelming).

## G3 — Intent (short, not a brief)

1–3 questions, at the calibrated depth: **what is this** (one line) and **what kind of capabilities** (e.g. HTTP API / CLI / web app / library / worker), plus the one or two hard constraints if any (must use language X / must deploy to Y). Stop there — feature-level scope is `specify`'s job, per feature. The goal is only «enough to choose an architecture».

## G4 — The foundation choices (recommend a coherent default set)

Pick these together. In *guided-default* mode, present the whole set as one recommended bundle + a confirm; in *guided-explained* / *expert*, walk the ones that matter. Always recommend a **coherent** default (the pieces fit each other), and gloss each per ask-style.

| Decision | What to pick | Default heuristic |
|---|---|---|
| **Stack** | language + framework + datastore | match the intent (HTTP API → a mainstream web framework + a relational DB; CLI → the language's standard CLI lib, no DB) |
| **Architectural style** | how code is organized | hexagonal modules (`domain → app → infra → ports`) with self-wiring — the pattern the rest of SDD assumes |
| **Folder / module structure** | the top-level layout | `cmd|src/`, `internal/modules/<m>/{domain,app,infra,ports}`, `migrations/`, `docs/` — adapt names to the stack |
| **Data / persistence** | migration tool + ID strategy | the stack's standard migration tool; app-generated time-sortable IDs; «DB as dumb storage» (see `data-model`'s baseline) |
| **Conventions** | errors, tests, CI | a unified error envelope; unit + integration (ephemeral real dependency) test layout; one CI workflow running build+test+lint |

Each irreversible pick (stack, module style, persistence) becomes a **foundational ADR** in `docs/adr/` — the «why» of the project's bones, so a later contributor doesn't silently re-litigate them. These ADRs are real blast-radius decisions (changing the stack/style later is a rewrite).

## G5 — Fix the foundation (the map as target baseline)

Write `docs/architecture-map.md` from the template with `mode: greenfield-bootstrap`. The C4 + module inventory describe the **target baseline** (what we're about to scaffold), the conventions catalog is the rule set the scaffold + every future feature follows. This is the same file brownfield mode produces, so downstream skills don't care which mode created it.

## G6 — Scaffold `tasks.json` contract (handed to `implement`)

Emit `docs/features/_scaffold/tasks.json` (a repo-level, not per-feature, task set) so `implement` can materialize the skeleton. Same shape as the `tasks` contract, with `layer: scaffold`:

```json
{
  "slug": "_scaffold",
  "tasks": [
    { "id": "S1", "title": "Create the module/folder structure + entry point", "layer": "scaffold", "deps": [],
      "acs": [], "dod": "project builds (empty)", "files_hint": ["cmd/", "internal/modules/"] },
    { "id": "S2", "title": "Wire the test harness + a smoke test", "layer": "scaffold", "deps": ["S1"],
      "acs": [], "dod": "empty test suite runs green; `app boots` smoke test passes", "files_hint": ["..."] },
    { "id": "S3", "title": "Set up the migration tool + an initial empty migration", "layer": "scaffold", "deps": ["S1"],
      "acs": [], "dod": "the migration tool applies + reverts cleanly", "files_hint": ["migrations/"] },
    { "id": "S4", "title": "Add the CI workflow (build + test + lint)", "layer": "scaffold", "deps": ["S2"],
      "acs": [], "dod": "CI config is valid; the commands match the detected toolchain", "files_hint": [".github/" ] },
    { "id": "S5", "title": "Write CLAUDE.md / .claude/rules from the chosen conventions", "layer": "scaffold", "deps": ["S1"],
      "acs": [], "dod": "conventions doc reflects the foundation map", "files_hint": ["CLAUDE.md", ".claude/rules/"] }
  ]
}
```

**The skeleton smoke test is the TDD anchor.** Scaffold tasks have no feature AC, so `implement` anchors the red→green on the structural smoke test: RED = «the project does not build / boot / the tooling doesn't run», GREEN = «build + boot + empty test suite + migration tool all succeed». That keeps the engine's discipline meaningful for structural work (no per-folder TDD theatre). `implement` reads the foundation map for the exact conventions to scaffold to.

After scaffold: the repo is real, `docs/architecture-map.md` describes it, and the normal per-feature flow (`specify → … → implement`) builds features into it — `implement`'s feature tests are real TDD against a project that now boots.
