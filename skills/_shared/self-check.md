# Structural self-check — the final-step verification contract every skill runs

> **Reference-only.** Not a skill. Every skill verifies its own output before handing off —
> this file is the one contract for how. A skill either runs a **named structural checklist**
> (defined in its own SKILL.md, penultimate protocol step) or maps an existing heavy verifier
> onto this contract (see «Heavy verifiers count» below). Either way, the SKILL.md names the
> phrase **structural self-check** at the place where the contract is satisfied — that is the
> greppable evidence the validator enforces.

## TL;DR (короткий вступ українською)

Кожен скіл перед хендофом перевіряє власний артефакт **з диска** за іменованим чеклістом.
Знайшов проблему → виправив і перевірив ще раз (максимум 2 цикли). Не зміг виправити →
чесно каже користувачу, ніколи мовчки. Результат — один рядок у хендофі: «self-check: 6/6 pass».
Скіли з важкими верифікаторами (critic, reviewer, drift-check, mermaid-check, GATE) не дублюють
роботу — їхній верифікатор і **є** self-check; вони додають лише структурні пункти, які він не покриває.

## The contract (five steps)

1. **Re-read the artifact from disk.** Never check the in-memory draft — the file as written is
   what downstream stages read. (A skill that writes nothing — e.g. `interview` — checks
   its emitted output against its DoD instead.)
2. **Run the named checklist.** Each item is **structural and cheap to verify** — a grep, a count,
   a file-exists test, an enum membership — not a judgment call. The checklist lives in the skill's
   own SKILL.md (penultimate protocol step) and has a fixed item count, so the result is reportable
   as `N/N`.
3. **Fix + re-check, ≤2 cycles.** A failing item is fixed and the checklist re-run. Two fix cycles
   maximum — an item still failing after that is *unresolved*, not retried forever.
4. **Surface the unresolved — never silently.** Anything still failing is reported to the user with
   the item name and what was tried. Silently committing a failing artifact is the one forbidden
   move; a stated failure is acceptable, a hidden one is not.
5. **Report in the handoff.** *What I did* carries one line: «self-check: 6/6 pass» (or
   «self-check: 5/6 — <failing item> unresolved, see above»).

## Heavy verifiers count (no double work)

A skill that already runs a heavy verifier — the clean-context **critic** (`specify`, `design`),
the **reviewer** agent (`review`), the **devil's-advocate** sweep (`clarify`), the bidirectional
**drift check** (`api`), the **mermaid re-validation** + coverage table (`sequences`), the
4-mandatory **self-check** (`data-model`, `tasks`), the per-task **GATE** (`implement`, `fix`) —
counts that verifier **as** its structural self-check. It does not bolt a second checklist on top;
it adds **only the structural items the verifier doesn't cover** (e.g. «frontmatter stamped»,
«file at the size-correct target») and still reports per step 5. The SKILL.md states the mapping
in one literal sentence («<verifier> = this skill's structural self-check»).

## Anti-patterns

- **Judgment items in the checklist.** «The spec is clear» is not checkable; «every §5 AC id
  appears in the coverage table» is. Judgment belongs to the heavy verifiers.
- **Checking the draft, not the disk.** The bug this contract exists to catch is the write that
  didn't land the way the conversation assumed.
- **Endless fix loops.** Two cycles, then surface. A checklist that can't converge in two fixes is
  flagging a real problem the user must see.
- **A silent pass.** The handoff line is mandatory even when everything passes — «self-check: 6/6
  pass» is one line of proof, not noise.
- **Duplicating the heavy verifier.** If the critic already checked cross-section drift, the
  checklist doesn't re-check it — only the structural leftovers.
