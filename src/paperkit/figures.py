from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_study_figures(results: dict[str, Any], destination: Path) -> None:
    """Render deterministic figures from canonical study results."""
    destination.mkdir(parents=True, exist_ok=True)
    _render_shopify_funnel(results["shopify_global_catalog"], destination)
    _render_cost_sensitivity(results["ucp_cost_sensitivity"], destination)


def _render_shopify_funnel(shopify: dict[str, Any], destination: Path) -> None:
    deck_build = shopify["report"]["deck_build"]
    labels = ("Captured\noffers", "Eligible\noffers", "Matched\nseller cards", "Seller\ndecks")
    values = (
        deck_build["input_rows"],
        deck_build["eligible_rows"],
        deck_build["seller_card_count"],
        deck_build["product_deck_count"],
    )
    figure, axis = plt.subplots(figsize=(6.6, 3.25))
    bars = axis.bar(range(len(values)), values, color=("#245b76", "#2f7f72", "#d48336", "#9b3d2e"))
    axis.set_yscale("log")
    axis.set_ylabel("Count (log scale)")
    axis.set_xticks(range(len(labels)), labels)
    axis.set_title("Recovered deep Shopify snapshot: offer-to-deck funnel")
    axis.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values, strict=True):
        axis.annotate(
            f"{value:,}",
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    _save(figure, destination / "shopify_deck_funnel")


def _render_cost_sensitivity(sensitivity: dict[str, Any], destination: Path) -> None:
    rows = sensitivity["cost_results"]
    labels = [str(row["cost_scenario"]).rsplit("_x", maxsplit=1)[-1] + "x" for row in rows]
    means = [row["adaptive_vs_search_all"]["mean_difference"] for row in rows]
    lower = [row["adaptive_vs_search_all"]["ci_lower"] for row in rows]
    upper = [row["adaptive_vs_search_all"]["ci_upper"] for row in rows]
    colors = [
        "#2f7f72" if row["adaptive_vs_search_all"]["favors_treatment"] else "#9b3d2e"
        if row["adaptive_vs_search_all"]["ci_lower"] > 0
        else "#667085"
        for row in rows
    ]
    positions = list(range(len(rows)))
    figure, axis = plt.subplots(figsize=(6.6, 3.25))
    axis.axhline(0, color="#1f2937", linewidth=0.9)
    for position, mean, low, high, color in zip(
        positions, means, lower, upper, colors, strict=True
    ):
        axis.errorbar(
            position, mean, yerr=[[mean - low], [high - mean]], fmt="o", color=color,
            capsize=4, markersize=6,
        )
    axis.set_xticks(positions, labels)
    axis.set_xlabel("Complete declared catalog-expansion cost multiple")
    axis.set_ylabel("Adaptive minus search-all total cost")
    axis.set_title("UCP held-out cost sensitivity (95% SKU-clustered intervals)")
    axis.grid(axis="y", alpha=0.25)
    _save(figure, destination / "ucp_cost_sensitivity")


def _save(figure: Any, path: Path) -> None:
    figure.tight_layout()
    metadata = {"Creator": "paperkit", "CreationDate": None, "ModDate": None}
    figure.savefig(path.with_suffix(".pdf"), metadata=metadata)
    figure.savefig(path.with_suffix(".png"), dpi=180, metadata={"Software": "paperkit"})
    plt.close(figure)