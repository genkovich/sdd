# Stage handoff — what every skill prints when it finishes (the output contract)

> **Reference-only.** Not a skill. **Every** skill ends by emitting the handoff block defined here —
> as its **last output**, after it has proposed its commit. The format lives only in this file; each
> skill keeps a one-line pointer and supplies its own *What I did* / *Review* / *next command*. This
> exists because a bare «Next: …» line is hard to act on — the user can't tell what changed, which
> files to open, or what to run next without scrolling back.

Running under Codex CLI or Cursor? The `/clear` and `/sdd:<next>` forms map to the host tool's
equivalents per [`tool-adapters.md`](./tool-adapters.md).

## TL;DR (короткий вступ українською)

Кожен крок (skill) наприкінці **завжди** друкує однаковий хендоф-блок із трьох секцій:

1. **What I did** — що стадія зробила + який коміт запропонувала (не змушуй гортати вгору).
2. **Review before continuing** — посилання на файли, які стадія створила/змінила і які треба
   глянути на цьому геті (реальні `docs/features/<slug>/…` шляхи — клікабельні/копіювані).
3. **Run next** — спершу `/clear` (обов'язково для forward-переходу — наступна стадія перечитує
   все з диска), потім наступна команда `/sdd:<next> <slug>` у **fenced-блоці** (копіюється в один
   клік) + альтернатива-пропуск, якщо вона є.

Це прибирає головний біль: «погано виводить, незручно копіювати і перевіряти».

---

## The block (sectioned format)

```md
## ✅ <skill> — <slug>

**What I did**
- <1–3 bullets: the artifact(s) produced/changed + the commit proposed>

**Review before continuing**
- `docs/features/<slug>/<file>` — <what to check here>
- `docs/features/<slug>/<file2>` — <…>

**Run next**
1. `/clear` — mandatory (fresh context; the next stage re-reads its inputs from disk)
2. then run:
   ```
   /sdd:<next> <slug>
   ```
   ↳ or `/sdd:<alt> <slug>` to <skip condition>   ← only when a real skip exists
```

Rules for filling it:

- **Always emit it** as the final output, once per run, after the commit is proposed. Never end a
  skill on a bare «Next: X».
- **What I did** — concrete and self-contained: name the files written and the proposed commit
  message, so the user doesn't scroll up to reconstruct it.
- **State the size + route used.** *What I did* names the `feature_size` AND the route the stage
  worked at — «size M + route standard (from `.size`/`.route`)»; if the stage had to **default**
  because a file was missing, say so loudly — «size M (default — no `.size`; run
  `/sdd:classify-size <slug>`)», «route standard (default — no `.route`)» — so a missing size/route
  surfaces at this gate, not three stages later. A missing `.route` always means `standard` (the
  pre-route behaviour — fully back-compatible). (`specify` establishes both at the start, so this
  should be rare.)
- **Review before continuing** — list **every artifact this stage wrote or changed**, each as a real
  `docs/features/<slug>/…` path (or repo-root path like `docs/architecture-map.md`) plus a one-liner
  on what to eyeball. This *is* the per-gate review checklist.
- **Run next** — the next command in **`/sdd:<name> <slug>`** form inside a fenced code block (so the
  user copies it in one click). `/clear` is step 1 and **mandatory** for a forward backbone handoff.
  Add a `↳ or …` skip-alternative **only** when one genuinely exists (see the table). The
  skip-alternatives come from the **fast-lane N/A conditions** in [`size-matrix.md`](./size-matrix.md);
  **how each resolves is route-dependent** — auto-skip on `quick`, offered on `standard`,
  suppressed on `full` (see the *Route-resolved forward handoff* variant below).
- Keep the `<slug>` substituted with the real slug — never leave the literal `<slug>` in the printed
  block.

## Variants

- **Backbone forward handoff** (`survey → … → review → ship`): `/clear` mandatory + the next stage.
- **Route-resolved forward handoff** (a backbone stage whose successor is an *optional* stage —
  `specify`, `clarify`, `design`, `sequences`, `data-model`, `api`, `tasks`): before printing *Run next*,
  resolve the next stage per `docs/features/<slug>/.route` and the Routes table in
  [`size-matrix.md`](./size-matrix.md):
  - **`quick`** — evaluate the next optional stage's N/A condition yourself. Holds → *Run next*
    names the post-skip stage, *What I did* states «auto-skipped `<stage>`: <reason>», and the
    `↳ or` line **inverts** — it offers the skipped stage («run the full path»). Doesn't hold →
    normal forward handoff (the stage is not skipped).
  - **`standard`** — normal forward handoff; add the `↳ or` skip-alternative when the N/A
    condition holds (the user picks).
  - **`full`** — normal forward handoff; **never** print an `↳ or` skip line.
  Missing `.route` → `standard`. The route steers handoffs only — a stage invoked directly always
  runs.
- **Loop-back** (`review → implement` on `CHANGES REQUESTED`): **no `/clear`** — you stay in context
  to iterate; *Run next* = `/sdd:implement <slug>` (fix), then re-review the changed surface.
- **Terminal** (`ship`): there is no `/sdd` successor. *Run next* becomes **Done** — the PR command/URL
  + «merging to main is your call»; still print *What I did* + *Review* (the changelog + PR).
- **Utility** (`classify-size`, `glossary`, `decide-adr`, `roadmap`, `design-system`, `fix`): called ad-hoc, not a
  gate. `/clear` is **optional** (recommend it only if the context is large); *Run next* = «resume
  your backbone stage», naming the likely one (e.g. `/sdd:design <slug>`). Print *What I did* +
  *Review* (the one file it wrote). One exception: `fix` alone adds a **conditional** recommendation —
  when the fix touched >5 files or crossed a module boundary, *Run next* also offers
  `/sdd:review <slug>` (a recommendation, never a gate).

## Canonical sequence (stage → review-files → next)

| Stage | Review before continuing (files written) | Run next |
|---|---|---|
| `survey` | `docs/architecture-map.md` (+ scaffold `tasks.json` on greenfield) | brownfield → `/sdd:specify <slug>`; greenfield → `/sdd:scaffold` |
| `scaffold` | the materialized skeleton (committed diff) + green smoke test | `/sdd:specify <slug>` |
| `specify` | `docs/features/<slug>/spec.md` | `/sdd:clarify <slug>` ↳ or `/sdd:ux-flows <slug>` (zero §8 OQ — fast lane; no human-facing UI → `/sdd:design <slug>`) |
| `clarify` | `docs/features/<slug>/spec.md` (tightened) | `/sdd:glossary <slug>` ↳ or `/sdd:ux-flows <slug>` (no human-facing UI → `/sdd:design <slug>`) |
| `ux-flows` | `docs/features/<slug>/ux-flows.md` (flows + SCR inventory) | `/sdd:design <slug>` |
| `design` | `sad.md` (C4 §3/§5 + `target_surfaces`) + `adr/` | `/sdd:sequences <slug>` ↳ or `/sdd:data-model <slug>` (XS/S, no multi-step flow — fast lane) |
| `sequences` | `sad.md` §6 (flows) | `/sdd:data-model <slug>` ↳ or `/sdd:api <slug>` (XS/S, no schema change — fast lane) |
| `data-model` | `data-model.md` + staged `migrations/` | `/sdd:api <slug>` ↳ or `/sdd:screens <slug>` (XS/S, no contract change — fast lane; no UI surface → `/sdd:tasks <slug>`) |
| `api` | `contracts/openapi.yaml` (+ `events.md`, `api-sync-report.md`) | `/sdd:screens <slug>` ↳ or `/sdd:tasks <slug>` (no UI surface in `target_surfaces` — fast lane) |
| `screens` | `docs/features/<slug>/screens.md` (+ `screens.pen` / Figma node-refs per tool) | `/sdd:tasks <slug>` |
| `tasks` | `tasks/` + `tasks.json` | `/sdd:plan-tests <slug>` ↳ then `/sdd:implement <slug>` |
| `plan-tests` | `test-plan.md` (or `spec.md` `## Test plan` for XS/S) | `/sdd:implement <slug>` |
| `implement` | the committed diff (code + tests) + `tasks/tracker.md` | `/sdd:review <slug>` |
| `review` | `_review/review-<date>.md` | `/sdd:ship <slug>` (PASS) · `/sdd:implement <slug>` (CHANGES, no `/clear`) |
| `ship` | `CHANGELOG` + the PR | **Done** — PR command/URL; merge is your call |
| `classify-size` | `.size` + `.route` | resume — e.g. `/sdd:specify <slug>` |
| `design-system` | `docs/design-system.md` | resume — e.g. `/sdd:ux-flows <slug>` |
| `glossary` | `CONTEXT.md` | resume — e.g. `/sdd:design <slug>` |
| `decide-adr` | `adr/NNNN-<title>.md` | resume — `/sdd:tasks <slug>` or `/sdd:plan-tests <slug>` |
| `roadmap` | `docs/roadmap.md` | resume your backbone stage |
| `fix` | `_fixes/<date>-<short>.md` + the diff (+ the spec patch if any) | resume — or `/sdd:review <slug>` when the fix was wide (>5 files / cross-module) |

The `↳ or` cells above show the `standard`-route rendering; on `quick` the stage auto-skips (and
the `↳ or` inverts), on `full` the `↳ or` line is dropped — per the *Route-resolved* variant.

## Discipline

- **The block is the last thing printed — every run, no exceptions.** A skill that ends on prose
  without it has regressed.
- **Real paths, not descriptions.** «the SAD» is not reviewable; `docs/features/<slug>/sad.md` is.
- **The next command is copy-ready** — `/sdd:<name> <slug>` in a fenced block, slug substituted.
- **`/clear` only where it's correct** — mandatory on a forward backbone handoff, omitted on a
  loop-back (you're iterating), optional after a utility.
- **Format canonical here** — a skill that hand-rolls its own block shape has duplicated the contract.

## Where each skill calls this

Every skill's final protocol step ends with: «emit the **stage-handoff block** per
[`handoff.md`](./handoff.md)» + its own next command from the table above. The format + variants live
here; the skill supplies only the run-specific content.
