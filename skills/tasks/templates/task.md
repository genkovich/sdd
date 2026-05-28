---
id: T1
title: "<imperative, specific title>"
layer: "migration|domain|infra|app|ports|tests|wiring|docs"
deps: []                # task ids that must finish first
acs: ["AC-01"]          # spec §5 acceptance criteria this task satisfies
files_hint: ["path/or/dir/the/task/touches"]
owner: "<owner / TBD lead>"
estimate: "S"           # S/M/L or hours
status: "todo"
---

# T1 — <title>

## Why

<!-- instruction: 1–2 sentences. Link the upstream source, don't paste it:
derives from [spec §AC-01](../spec.md), [sad §6](../sad.md), [ADR-0001](../adr/0001-....md). -->

## What

<!-- instruction: the concrete change, scoped to ≤1 day / one reviewable PR. Name the files/dirs
(same as files_hint). For a migration task: the up + down files. For a ports task: the handler +
its dto + errors. Keep it within one layer where possible. -->

## Definition of Done

<!-- instruction: testable bullets. e.g.: -->
- [ ] <unit/integration test for this task passes>
- [ ] <migration applies and reverts cleanly> (migration tasks)
- [ ] <handler returns the spec'd outcome for AC-01> (ports tasks)
- [ ] lint + vet clean

## Notes

<!-- instruction: gotchas, the lane this shares with another task (overlapping files_hint), any
Hard Rule it must respect. -->
