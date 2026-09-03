---
status: Draft
owner: "Commerce lead"
updated_at: "2026-08-20"
depth: "medium"
---

# Idea brief — checkout-incentives

## 1. Raw idea

Sales keeps promising customers discounts and gift cards that our checkout cannot honour, so
finance applies them by hand afterwards. I want the checkout itself to price both.

## 2. Problem

Roughly 90 orders a month get a manual price adjustment after the fact. Each one is a support
ticket plus a finance correction, and two of them last quarter shipped at the wrong price.

## 3. Users

Customers at checkout; the support team that currently patches orders; finance, who reconciles the
corrections monthly.

## 4. Why now

The autumn campaign is built on discount codes and starts in eight weeks. Doing it by hand at that
volume is not survivable.

## 5. Out of scope

- Loyalty points and tiered pricing — a different pricing model entirely, not this quarter.
- Refunds against a gift card — the finance flow for that is not designed yet.

## 6. Risks

- Discount codes and gift cards both change the same price computation. Two people editing that
  path at once is the obvious way to lose a rule silently.
- Assumes the order confirmation email can show an adjusted total; nobody has checked what the
  template currently renders.

## 7. Recommendation

Ship the price computation once and put both incentives through it. Discount codes go first
because the campaign depends on them; gift cards follow on the same path. The confirmation email
is independent of both and can move in parallel.

## 8. Open questions

- Can two discount codes stack on one order? — owner: commerce lead
- What does the confirmation-email template render for the total today? — owner: agent
