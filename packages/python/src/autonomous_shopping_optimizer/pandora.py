from __future__ import annotations

from collections.abc import Iterable, Mapping
from fractions import Fraction

RESOURCE_FIELDS = ("time_ms", "tokens", "api_calls", "api_cost_minor")
CostNumber = int | Fraction


def scalarized_inspection_cost(
    resources: Mapping[str, CostNumber], shadow_prices: Mapping[str, CostNumber]
) -> Fraction:
    """Convert one inspection's resources to currency minor units."""
    parsed = _resource_vector(resources, "resources")
    prices = _resource_vector(shadow_prices, "shadow_prices")
    return (
        Fraction(parsed["api_cost_minor"])
        + Fraction(parsed["time_ms"] * prices["time_ms"], 1000)
        + Fraction(parsed["tokens"] * prices["tokens"], 1000)
        + Fraction(parsed["api_calls"] * prices["api_calls"])
    )


def expected_improvement(current_best_minor: int, price_samples: Iterable[int]) -> Fraction:
    """Expected item-price saving from one more seller under free recall."""
    current = _positive_integer(current_best_minor, "current_best_minor")
    samples = _price_samples(price_samples)
    return sum((max(0, current - price) for price in samples), 0) / Fraction(len(samples))


def empirical_reservation_price(
    price_samples: Iterable[int], inspection_cost_minor: Fraction | int
) -> Fraction:
    """Solve E[(z - P)+] = c exactly for an empirical price distribution."""
    samples = sorted(_price_samples(price_samples))
    cost = Fraction(inspection_cost_minor)
    if cost < 0:
        raise ValueError("inspection_cost_minor must be non-negative")
    prefix = 0
    count = len(samples)
    for opened, price in enumerate(samples, start=1):
        prefix += price
        candidate = (count * cost + prefix) / opened
        next_price = samples[opened] if opened < count else None
        if next_price is None or candidate <= next_price:
            return max(Fraction(price), candidate)
    raise AssertionError("empirical reservation price is undefined")


def pandora_decision(
    *,
    current_best_minor: int,
    price_samples: Iterable[int],
    resources: Mapping[str, CostNumber],
    shadow_prices: Mapping[str, CostNumber],
    remaining_budget: Mapping[str, CostNumber],
) -> dict[str, object]:
    """Return STOP or SEARCH from value of information and hard feasibility."""
    parsed_resources = _resource_vector(resources, "resources")
    budget = _resource_vector(remaining_budget, "remaining_budget")
    feasible = all(parsed_resources[field] <= budget[field] for field in RESOURCE_FIELDS)
    prices = _resource_vector(shadow_prices, "shadow_prices")
    components = {
        "time": Fraction(parsed_resources["time_ms"] * prices["time_ms"], 1000),
        "tokens": Fraction(parsed_resources["tokens"] * prices["tokens"], 1000),
        "api_calls": Fraction(parsed_resources["api_calls"] * prices["api_calls"]),
        "api_spend": Fraction(parsed_resources["api_cost_minor"]),
    }
    cost = sum(components.values(), Fraction())
    gross = expected_improvement(current_best_minor, price_samples)
    reservation = empirical_reservation_price(price_samples, cost)
    net = gross - cost
    action = "SEARCH" if feasible and net > 0 else "STOP"
    return {
        "action": action,
        "feasible": feasible,
        "current_best_minor": current_best_minor,
        "expected_saving_minor": float(gross),
        "cost_components_minor": {
            key: float(value) for key, value in components.items()
        },
        "inspection_cost_minor": float(cost),
        "net_value_minor": float(net),
        "reservation_price_minor": float(reservation),
        "resources": {key: float(value) for key, value in parsed_resources.items()},
        "shadow_prices": {key: float(value) for key, value in prices.items()},
        "remaining_budget": {key: float(value) for key, value in budget.items()},
    }


def pandora_cost_table() -> dict[str, object]:
    """Declared scenarios showing how resource valuations change the action."""
    current_best = 10_000
    samples = [8_500, 9_500, 10_000, 11_000]
    budget = {
        "time_ms": 300_000,
        "tokens": 30_000,
        "api_calls": 12,
        "api_cost_minor": 1_000,
    }
    scenarios = [
        (
            "catalog_expansion_openai_gpt_5_4_mini",
            {
                "time_ms": 30_000,
                "tokens": 0,
                "api_calls": 0,
                "api_cost_minor": Fraction(91, 40),
            },
            {"time_ms": Fraction(25, 3), "tokens": 0, "api_calls": 0, "api_cost_minor": 0},
            budget,
        ),
        (
            "agentic_review_2m_anthropic_claude_sonnet_5",
            {
                "time_ms": 120_000,
                "tokens": 0,
                "api_calls": 0,
                "api_cost_minor": 21,
            },
            {"time_ms": Fraction(25, 3), "tokens": 0, "api_calls": 0, "api_cost_minor": 0},
            budget,
        ),
        (
            "long_horizon_research_5m_xai_grok_4_7",
            {
                "time_ms": 300_000,
                "tokens": 0,
                "api_calls": 0,
                "api_cost_minor": Fraction(111, 2),
            },
            {"time_ms": Fraction(25, 3), "tokens": 0, "api_calls": 0, "api_cost_minor": 0},
            budget,
        ),
        (
            "hard_time_cap",
            {"time_ms": 120_000, "tokens": 0, "api_calls": 0, "api_cost_minor": 21},
            {"time_ms": Fraction(25, 3), "tokens": 0, "api_calls": 0, "api_cost_minor": 0},
            {**budget, "time_ms": 60_000},
        ),
    ]
    rows = []
    for scenario, resources, shadow_prices, remaining in scenarios:
        row = pandora_decision(
            current_best_minor=current_best,
            price_samples=samples,
            resources=resources,
            shadow_prices=shadow_prices,
            remaining_budget=remaining,
        )
        row["scenario"] = scenario
        rows.append(row)
    return {
        "model": "empirical_pandora_free_recall",
        "currency": "USD",
        "minor_units_per_currency_unit": 100,
        "current_best_minor": current_best,
        "candidate_price_samples_minor": samples,
        "reservation_equation": "E[max(z - P, 0)] = scalarized_inspection_cost",
        "decision_rule": "SEARCH iff feasible and E[max(b - P, 0)] > cost",
        "cost_rate_card": "research/cost-rate-card-2026-09.json",
        "time_value_minor_per_minute": 500,
        "scenario_assumptions": "Declared workload assumptions, not execution telemetry.",
        "rows": rows,
    }


def _resource_vector(
    values: Mapping[str, CostNumber], name: str
) -> dict[str, Fraction]:
    parsed: dict[str, Fraction] = {}
    for field in RESOURCE_FIELDS:
        value = values.get(field, 0)
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)) or value < 0:
            raise ValueError(f"{name}.{field} must be a non-negative integer")
        parsed[field] = Fraction(value)
    return parsed


def _price_samples(values: Iterable[int]) -> tuple[int, ...]:
    samples = tuple(_positive_integer(value, "price sample") for value in values)
    if not samples:
        raise ValueError("price_samples must not be empty")
    return samples


def _positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value