---
status: Draft
owner: "Platform lead"
updated_at: "2026-08-20"
depth: "medium"
---

# Idea brief — deploy-digest

## 1. Raw idea

We ship 40-60 times a week across five services and nobody can answer «what went out yesterday»
without opening five CI dashboards. I want one page that lists what shipped, per service, per day,
built from what the CI already emits.

## 2. Problem

Post-incident, the first twenty minutes go to reconstructing what changed. Last quarter three
incidents had that reconstruction on the critical path; the shortest took 18 minutes.

## 3. Users

On-call engineers (six people, rotating weekly) during an incident, and the platform lead on the
Monday review. Roughly 12 lookups a week.

## 4. Why now

The fifth service landed in July and pushed manual reconstruction past the point where anyone does
it correctly under pressure.

## 5. Out of scope

- Deploy approval or rollback controls — this is a read-only view, not a deployment tool.
- Anything upstream of CI: no code-review or ticket data.

## 6. Risks

- Assumes every service's CI emits a machine-readable record of what it deployed. False for the
  legacy billing runner, which writes only to its own log file in a format nobody has documented
  or read.
- Assumes on-call will open a page during an incident rather than ask in chat.

## 7. Recommendation

Build the digest against the four services whose CI already emits structured deploy events, and
treat the legacy billing runner as a separate problem: its log format has never been looked at, so
we do not know whether it can be parsed at all or has to be changed at the source.

## 8. Open questions

- What exactly does the legacy billing runner write on a deploy, and is it parseable? — owner: platform lead
- Does the digest need per-commit detail, or is per-deploy enough? — owner: on-call reps
