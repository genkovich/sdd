---
status: approved
updated_at: 2026-08-01
---

# Session timeout — auto-revoke inactive admin sessions

## 1. Context

Admin sessions currently live until explicit logout. Compliance asked for automatic revocation
of inactive admin sessions in the existing auth module — no new module, no new API surface.

## 2. Goals

- An inactive admin session is revoked automatically, without operator action.

## 3. Non-goals

- Changing the login flow or the session store technology.
- Timeout policies for non-admin users.

## 4. User stories

- US-1: As a security officer, I want inactive admin sessions revoked automatically so a
  forgotten open session cannot be reused.

## 5. Acceptance criteria

- AC-1 (happy): Given an admin session with no activity for the configured inactivity window,
  when the window elapses, then the session is revoked and the next action requires login.
- AC-2 (error): Given a revoked session, when the admin performs any action, then the action is
  rejected and the admin is redirected to login with a clear message.
- AC-3 (authorization): Given a non-admin session, when the inactivity window elapses, then the
  session is unaffected by this feature.
- AC-4 (domain invariant): A revoked session can never be reactivated — a new login creates a
  new session.
- AC-5 (cross-context): Given a session revoked by timeout, when the audit log is read, then it
  contains a revocation entry with the session id and the reason «inactivity».

## 6. Non-functional requirements

| Requirement | Target | Measurement |
|---|---|---|
| Revocation must feel fast | fast | — |

## 7. KPIs

- 0 reused stale admin sessions in the quarterly access review.

## 8. Open questions

*(none)*
