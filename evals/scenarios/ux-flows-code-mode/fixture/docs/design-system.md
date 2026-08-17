---
status: Living
tool: code
figma_file: ""
pen_file: ""
updated_at: 2026-08-10
---

# Design system — storefront

> The project's design canon — tool, posture, tokens, component inventory. Produced by
> `design-system`; read by `ux-flows` (posture) and `screens` (tool + inventory).

## Platform posture

- **Posture:** mobile-first — most shoppers arrive from phones; desktop is the enhancement.
- **Breakpoints / device classes:** sm 360px / md 768px / lg 1024px

## Design tool

- **Tool:** code — screens are specified as inline markdown wireframes in each feature's screens.md
- **Library location:** the in-repo components are the library

## Token source

- **Colors:** CSS variables — `web/src/styles/tokens.css`
- **Spacing / sizing:** the 4px scale in the same file — `web/src/styles/tokens.css`
- **Typography:** `web/src/styles/typography.css`

## Component inventory

| Component | Source (`file:line` / node / URL) | States it supports | Notes |
|---|---|---|---|
| Button | `web/src/components/Button.tsx:1` | default / disabled / loading | primary + ghost variants |
| Input | `web/src/components/Input.tsx:1` | default / error / disabled | inline validation message |
| ListItem | `web/src/components/ListItem.tsx:1` | default / pressed | swipe actions on mobile |
| EmptyState | `web/src/components/EmptyState.tsx:1` | default | illustration + one CTA |
| Toast | `web/src/components/Toast.tsx:1` | info / error | auto-dismiss 4s |

## Interaction & writing conventions

- **Errors:** inline under the field for validation; Toast for request failures
- **Empty states:** EmptyState with one CTA
- **Loading:** skeleton rows in lists; Button loading state on submit
- **Validation:** on-submit; errors attach under the field
- **Microcopy tone:** short, verb-first
