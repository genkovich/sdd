---
status: approved
updated_at: 2026-08-12
feature_size: S
---

# Saved searches — save, re-run and manage product searches

## 1. Context

Shoppers refine product searches with several filters, then lose them between visits. The
storefront web app (mobile-first) should let a signed-in shopper save a search under a name,
see the saved list, re-run one, and delete one.

## 2. Goals

- A shopper can keep a refined search and get back to its results in one tap.

## 3. Non-goals

- Sharing saved searches between accounts.
- Notifications when saved-search results change.

## 4. User stories

- US-1: As a signed-in shopper, I want to save my current search under a name so I can re-run it later.
- US-2: As a signed-in shopper, I want to see my saved searches and re-run one to its results.
- US-3: As a signed-in shopper, I want to delete a saved search I no longer need.

## 5. Acceptance criteria

- AC-1 (happy): Given a current search and a non-empty name, when the shopper saves it, then it
  appears in their saved-searches list under that name.
- AC-2 (error): Given an empty name, when the shopper tries to save, then the save is rejected
  with a message naming the problem and nothing is stored.
- AC-3 (authorization): Given a guest (not signed in), when they try to save a search, then they
  are asked to sign in first and the search is not stored.
- AC-4 (domain invariant): Saved-search names are unique per shopper — saving a duplicate name is
  rejected with a message and the existing entry is unchanged.
- AC-5 (cross-context): Given a shopper with no saved searches, when they open the saved-searches
  list, then an empty state explains how to save the first one.
- AC-6 (happy): Given a saved search, when the shopper deletes it and confirms, then it is removed
  from the list.

## 6. Non-functional requirements

- Opening the saved-searches list shows content in ≤ 1 second on a mid-range phone (p95, measured
  in the web app's performance monitoring).

## 7. KPIs

- ≥ 15% of signed-in shoppers who refine a search save at least one within 30 days of launch.

## 8. Open questions

_None._
