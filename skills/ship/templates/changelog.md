# Changelog — <slug>

<!-- instruction: what changed + why, not a file list. Link the spec and the load-bearing ADRs.
Include the operational note (migrations, feature flags) the deployer needs. Keep it readable by
someone who didn't write the feature. -->

## <slug> — <one-line summary>

**What:** <the user-facing capability that now exists, in plain language>.

**Why:** <the problem it solves — link [spec](../spec.md) §1/§2; cite the key decision(s) — [ADR-NNNN](../adr/NNNN-...md)>.

**How to use:** <the endpoint/flow + an example, from [openapi.yaml](../contracts/openapi.yaml)>.

**Operational notes:**
- Migration: <e.g. "adds 000023_create_notification_preferences — applied on deploy; reverts cleanly">, or `<!-- none -->`.
- Feature flag / config: <any>, or `<!-- none -->`.
- Rollback: <how to back out — usually `migrate down` + revert the deploy>.
- Mobile release <only for a `mobile-app` surface — pick the flavor; else `<!-- N/A: not a mobile ship -->`>:
  - **App:** version + build bump <e.g. 2.39.0 (1234)>; signing <who/how>; target track <internal / beta / store>; rollout <phased % or full>; dSYM / mapping upload <yes/no>.
  - **Library/SDK:** module version bump(s) <e.g. Messaging 2.39.0>; registries <SPM / CocoaPods / Maven / …>; channel <snapshot / release>; public-API breaking change <none, or what broke + the major bump>.

**Acceptance criteria delivered:** <AC-01 … AC-NN — the business outcomes now guaranteed>.
