# Agentic Shopping: Search or Stop

**Make "one more seller?" a deterministic, auditable decision.**

`agentic-shopping-search-or-stop` helps shopping agents decide whether another
merchant inspection is worth its time, tokens, API calls, and money. It returns
`SEARCH` only when the next inspection fits the remaining budget and its expected
saving exceeds its declared cost. Otherwise, it returns `STOP` with a complete
decision breakdown.

The runtimes are local decision utilities. They make no network calls, hold no
credentials, and never authorize a purchase.

## Install

Choose the integration that fits your agent host:

### Python

```bash
pip install agentic-shopping-search-or-stop
```

See the [Python package guide](packages/python/README.md).

### JavaScript

```bash
npm install agentic-shopping-search-or-stop
```

See the [JavaScript package guide](packages/javascript/README.md).

### Agent Skill

```bash
npx skills add ahnafyy/autonomous-merchant-search-or-stop
```

The Skill gives compatible agents a safe procedure for calling either runtime.

## What it provides

- **Hard budget gate:** time, token, call, and API-spend limits are checked before
	another merchant inspection.
- **Economic comparison:** expected retained-offer savings are compared with the full
	declared inspection cost, including resource shadow prices.
- **Decision breakdown:** every result includes feasibility, expected saving, cost
	components, net value, and reservation price.
- **Tool-ready contract:** both runtimes expose the same narrow JSON decision schema;
	the host adapts the provider-specific outer envelope.
- **Host control:** merchant access, credentials, validation, and purchase approval
	remain outside the model and outside this package.

## Decision rule

```text
SEARCH iff the next inspection fits the remaining budget
			 and expected retained-offer saving > inspection cost
```

The host supplies same-product price samples, the best retained price, expected
resource use for the next inspection, and remaining budgets. The runtime returns the
decision; the host remains responsible for dispatching tools and reconciling actual
usage.

## Public integrations

- Python: `RecalledSearchHook`, `pandora_decision`,
	`recalled_search_tool_schema`, and `run_recalled_search_tool`
- JavaScript: `createRecalledSearchHook`, `decideRecalledSearch`,
	`recalledSearchToolSchema`, and `runRecalledSearchTool`
- Agent Skill: `agent-shopping-search-or-stop`

## Development

```bash
make install
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
npm test --prefix packages/javascript
npm run pack:check --prefix packages/javascript
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full validation workflow.

## Evidence

The useful result is narrow: **inspection cost changes which policy wins**.

- In the held-out UCP replay, adaptive stopping beats costed search-all across all
	three declared real-dollar scenarios over 1,381 SKU clusters
	(`UCP-PANDORA-REPLAY-001`).
- At zero inspection cost, search-all wins. At one-hundredth and one-tenth of the
	registered workload, the comparison is inconclusive. At the registered workload
	and ten times it, adaptive stopping wins (`UCP-MARKET-RATE-SENSITIVITY-001`).
- The smaller Shopify replay is exploratory because identity matching changed after
	collection. Only its highest-cost scenario favors adaptive stopping
	(`PANDORA-ADVANTAGE-001`).

Read the [paper source](paper/) and [executable claim ledger](research/claims.yml)
for intervals, methods, and scope. The package itself is tested against shared
conformance vectors.

## License

Code is available under the [MIT License](LICENSE).