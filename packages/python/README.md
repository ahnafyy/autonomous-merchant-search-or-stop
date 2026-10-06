# agentic-shopping-search-or-stop

Runtime utilities for the paper's recalled-search rule: decide whether another seller
inspection earns its cost or an agent should stop with its best retained offer.

The host owns LLM calls, merchant tools, credentials, and purchase execution. This
package makes the decision and checks declared budget feasibility; it never contacts a
merchant.

```bash
pip install agentic-shopping-search-or-stop
```

## Recalled-search hook for LLM tool loops

Use `RecalledSearchHook` after each seller tool result when the agent can retain its
best observed offer. The hook implements the reported rule exactly:

```text
SEARCH iff the next inspection fits the remaining budget
     and E[max(best retained offer - next price, 0)] > inspection cost
```

Prices and API spend are integer USD minor units. Resource shadow prices may be exact
fractions: `time_ms` is a millisecond quantity whose shadow price is minor units per
second, and `tokens` is charged in minor units per thousand tokens. The host supplies
calibrated samples for the next seller, then owns tool dispatch, actual-usage charging,
credentials, and purchase execution.

```python
from agentic_shopping_search_or_stop import RecalledSearchHook

after_offer = RecalledSearchHook(
  price_samples_minor=[8_900, 9_400, 10_200, 11_100],
  shadow_prices={"time_ms": 8, "api_calls": 2},
)

decision = after_offer(
  current_best_minor=10_000,
  next_inspection_resources={"time_ms": 12_000, "api_calls": 1, "api_cost_minor": 18},
  remaining_budget={"time_ms": 45_000, "api_calls": 3, "api_cost_minor": 100},
)
if decision["action"] == "SEARCH":
  next_seller = call_seller_tool()  # Host responsibility.
else:
  buy_best_retained_offer()         # Host responsibility.
```

`decision` contains the `expected_saving_minor`, each cost component,
`inspection_cost_minor`, `net_value_minor`, feasibility, and reservation price for
logging or an LLM tool response. Do not use seller observations from one product as
the calibrated price sample for another product.

### OpenAI/ChatGPT and Claude tool registration

`recalled_search_tool_schema()` returns a vendor-neutral name, description, and JSON
input schema. `run_recalled_search_tool()` executes exactly that payload. Adapt only
the outer tool envelope at the SDK boundary; no provider SDK is required.

```python
from agentic_shopping_search_or_stop import (
  recalled_search_tool_schema,
  run_recalled_search_tool,
)

schema = recalled_search_tool_schema()

# OpenAI Chat Completions-style registration:
openai_tool = {
  "type": "function",
  "function": {
    "name": schema["name"],
    "description": schema["description"],
    "parameters": schema["input_schema"],
    "strict": True,
  },
}

# Anthropic Messages-style registration:
claude_tool = schema

# When either model emits decide_recalled_search arguments:
decision = run_recalled_search_tool(model_tool_arguments)
```

Treat the model as a caller, not as the decision implementation. Validate seller
identity and a calibrated same-product price sample before calling the tool, enforce
the actual tool permit separately, and never let model output authorize a purchase.

### Agent skill

For a cross-agent procedure that registers and calls this runtime safely, install
`agent-shopping-search-or-stop` from this repository with:

```bash
npx skills add ahnafyy/autonomous-merchant-search-under-constraints
```

The skill complements this package; this package remains the deterministic decision
implementation.

## Evidence boundary

The frozen Shopify seller-deck study has 40 product decks: 24 calibration decks and
16 held-out product clusters. It uses only the recovered complete 39-query prefix of
48 registered deep queries. Its title identity rule was revised after collection, so
it is a reproducible held-out study, not a deployment recommendation.
Direct-merchant UCP panels are separate catalog-observability evidence, not inputs to
the Shopify Pandora policy replay.

## Runtime API boundary

For production agent integrations, depend on `RecalledSearchHook`,
`pandora_decision`, `recalled_search_tool_schema`, and `run_recalled_search_tool`.
The runtime needs no study data: the host supplies same-product calibration samples,
declared inspection resources, and remaining budgets.
