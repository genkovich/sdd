<!-- PR body scaffold. Forge-agnostic — same body for `gh pr create --body-file` or `glab mr create --description`. -->

## Summary

<1–3 sentences: what this PR ships and why. Link [spec](docs/features/<slug>/spec.md).>

## Acceptance criteria

<the AC this PR satisfies, each one line — the reviewer checks these against the diff>

- AC-01 — <business outcome> ✓
- AC-0N — <business outcome> ✓

## Design

- Spec: `docs/features/<slug>/spec.md`
- Architecture: `docs/features/<slug>/sad.md`
- Decisions: `docs/features/<slug>/adr/`
- Data model + migration: `docs/features/<slug>/data-model.md` (migration `<NNNN>`)
- API: `docs/features/<slug>/contracts/openapi.yaml`

## Tasks (SDD-Task trailers)

<the per-task commits — `git log --grep SDD-Task`>

## Verification

- Unit: <result>
- Integration: <result, or "CI — Docker-backed">
- Lint + vet: <result>
- Ran the feature: <what was exercised against the AC, or what was deferred and why>

## Operational notes

- Migration: <run-on-deploy + rollback>, or none.
- Feature flag / config: <any>, or none.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
