# Mermaid check — validate every diagram after writing it

> **Reference-only.** Not a skill. Any skill that emits a Mermaid diagram (`design` C4 §3/§5,
> `sequences` §6, `data-model` ER, `survey` C4, `tasks` `_epic` flowchart) runs this **after
> writing** the diagram and **before committing** it. The rule: a diagram that doesn't parse must
> never be committed — broken Mermaid renders as a red error box for the reader.

## Procedure

1. **Write** the diagram into its file.
2. **Validate it parses** (render-check if a renderer is available, else the structural lint below).
3. **On failure:** cite the offending ```mermaid block + the parser's error line, **fix the syntax**, and **re-validate**. Loop up to 3 times.
4. If it still won't parse after 3 tries, do **not** commit it as-is — surface the block + the error to the user and ask, rather than shipping a diagram that renders as an error box.

## Detection cascade (first available wins)

1. **`mmdc` (mermaid-cli)** — the real parser. On PATH, or `npx -y @mermaid-js/mermaid-cli`. Run it over the file that contains the diagrams (it extracts and renders every ```mermaid block) to a throwaway output and check the exit code:
   ```bash
   mmdc -i docs/features/<slug>/sad.md -o /tmp/_mmd_check.md 2>&1   # exit != 0 → a block failed; stderr names it
   ```
   A non-zero exit means at least one block is invalid; the stderr names the diagram + the syntax error. Delete the throwaway output after.
2. **Project mermaid dep** — if `node_modules/mermaid` exists, a tiny `mermaid.parse(src)` per extracted block (parse-only, no render) is enough and fast.
3. **Obsidian vault** — if the docs live in an Obsidian vault, the obsidian-cli render/error-capture can confirm the block renders.
4. **No renderer → structural lint** (the fallback; what `design` did inline — now centralized here): for each ```mermaid block check
   - matched opening/closing ```mermaid fences;
   - a recognized first token: `graph`/`flowchart`/`sequenceDiagram`/`classDiagram`/`erDiagram`/`stateDiagram`/`C4Context`/`C4Container`/`C4Component`/`journey`/`gantt`;
   - **every node/participant referenced by an edge/`Rel` is declared first**;
   - no leftover template `<placeholder>` substrings;
   - balanced brackets/parens/quotes;
   - no known typos (see below).
   The lint catches the common breakages; recommend installing `mmdc` for a real parse when it's not present.

## Per-type gotchas (the usual render failures)

- **C4** (`C4Context` / `C4Container`): it's `Container_Boundary` / `System_Boundary` (NOT `Container_Bondary`); declare every `Person(...)` / `System(...)` / `Container(...)` / `ContainerDb(...)` **before** any `Rel(from, to, "label")` that uses its id; ids have no spaces; `Rel` needs the quoted label arg.
- **sequenceDiagram**: declare `participant X as Display Name`, then refer to `X`; keep `alt … else … end` / `loop … end` / `opt … end` balanced; `Note over X,Y: text`; actors with spaces need an alias. **No `;` in message/Note text** — Mermaid treats `;` as a statement separator, so `Note over R,DB: commit; any error rolls back` parses the part after `;` as a broken new message (a real bug this check caught). Avoid **Unicode arrows (`→`)** in text (use words or `-->`), and put **no trailing `%%` inline comment** on a message line (`%%` must start its own line).
- **erDiagram**: `ENTITY ||--o{ OTHER : "label"`; attribute lines are `type name` inside `ENTITY { … }`; cardinality glyphs must be valid (`||--o{`, `}o--||`, …). The key class is `PK` / `FK` / `UK` only — **`PK_FK` is invalid** (use `PK, FK`, or `PK "FK to users"` as a comment; another real bug this check caught).
- **flowchart**: `flowchart LR` (or `TD`) + `A[label] --> B{decision}`; match bracket shapes (`[]` `()` `{}`); a node label with special chars needs quotes `A["a: b"]`.

## Where each skill calls this

- `design` — at the per-section write (§3 C4Context, §5 C4Container) and again in the finalize backstop, over `sad.md`.
- `sequences` — after writing the §6 `sequenceDiagram` blocks.
- `data-model` — after the `erDiagram` in `data-model.md`.
- `survey` — after the C4 in `architecture-map.md`.
- `tasks` — after the `flowchart` in `_epic.md`.

Each keeps only a one-line "validate per [`mermaid-check.md`]" pointer; the procedure lives here.
