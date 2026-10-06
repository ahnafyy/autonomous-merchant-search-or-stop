---
name: agent-shopping-search-or-stop
description: "Use when an AI shopping agent must decide whether to inspect another merchant or stop with its best retained offer under explicit time, token, call, and money budgets."
---

# Agent Shopping: Search or Stop

Use this procedure after a host has revealed one or more offers for the same
product and can return to its best retained offer.

## Required Host Inputs

Before making a decision, obtain:

- The best currently retained price in USD minor units.
- A same-product calibrated sample of plausible next-seller prices in USD minor
  units. Do not mix products, currencies, or unvalidated seller variants.
- The next inspection's declared resource use: `time_ms`, `tokens`, `api_calls`,
  and `api_cost_minor`.
- The remaining hard budget for those same resources and, when applicable,
  their shadow prices in USD minor units.

## Decision Procedure

1. Register the public `decide_recalled_search` tool schema from the Python or
   JavaScript runtime package.
2. Invoke the runtime with the required values. It returns `SEARCH` only when
   the inspection fits the hard budget and its expected retained-offer saving
   exceeds its declared inspection cost.
3. On `SEARCH`, reserve and enforce the actual tool permit before dispatching
   the next merchant tool. Reconcile recorded usage afterward.
4. On `STOP`, present the retained offer for a separate, user-authorized
   purchase decision.
5. Log the input, returned decision, and actual resource use so the host can
   audit the decision without treating it as a purchase authorization.

## Non-Negotiable Boundaries

- The model may request the decision tool but does not decide the formula,
  dispatch merchant tools, own credentials, or authorize a purchase.
- The host validates seller identity, same-product equivalence, currency,
  freshness, shipping, tax, and return terms.
- The frozen study evaluates replayed seller cards, not universal merchant
  coverage, checkout success, or deployment performance. Do not describe a
  runtime decision as a replicated empirical finding.