"""Chart generation for reports (D-02: Matplotlib static images).

Generates per-group performance bar charts and metric comparison charts
as base64-encoded PNG strings for embedding in HTML/PDF reports.
"""

from __future__ import annotations

import base64
import io
from typing import Any

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for server-side rendering

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def generate_charts(analysis_results: dict[str, Any]) -> dict[str, str]:
    """Generate all report charts as base64 PNG strings.

    Parameters
    ----------
    analysis_results : dict
        From ``AnalysisResult.to_dict()``.

    Returns
    -------
    dict[str, str]
        Mapping of chart name → base64-encoded PNG string.
    """
    charts: dict[str, str] = {}
    results = analysis_results.get("results", {})

    for attr_name, attr_data in results.items():
        breakdown = attr_data.get("performance_breakdown", {})
        if breakdown:
            charts[f"performance_{attr_name}"] = _performance_bar_chart(
                attr_name, breakdown
            )

        metrics = attr_data.get("metrics", {})
        if metrics:
            charts[f"metrics_{attr_name}"] = _metrics_comparison_chart(
                attr_name, metrics
            )

    return charts


def _performance_bar_chart(attr_name: str, breakdown: dict) -> str:
    """Grouped bar chart: accuracy/precision/recall/F1 per group."""
    groups = list(breakdown.keys())
    metric_names = ["accuracy", "precision", "recall", "f1"]

    x = np.arange(len(groups))
    width = 0.18
    colors = ["#3b82f6", "#8b5cf6", "#f59e0b", "#10b981"]

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (metric, color) in enumerate(zip(metric_names, colors)):
        values = [breakdown[g].get(metric, 0) for g in groups]
        ax.bar(x + i * width, values, width, label=metric.capitalize(), color=color)

    ax.set_xlabel("Group", fontsize=11)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(
        f"Performance by {attr_name.replace('_', ' ').title()}", fontsize=13
    )
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    return _fig_to_base64(fig)


def _metrics_comparison_chart(attr_name: str, metrics: dict) -> str:
    """Horizontal bar chart: metric value vs threshold."""
    metric_names: list[str] = []
    values: list[float] = []
    thresholds: list[float] = []
    colors: list[str] = []

    status_colors = {
        "pass": "#22c55e",
        "warning": "#eab308",
        "fail": "#ef4444",
        "skipped": "#94a3b8",
    }

    for name, data in metrics.items():
        if data.get("value") is None:
            continue
        metric_names.append(name.replace("_", " ").title())
        values.append(data["value"])
        thresholds.append(data.get("threshold", 0))
        colors.append(status_colors.get(data.get("status", ""), "#94a3b8"))

    if not metric_names:
        fig, ax = plt.subplots(figsize=(8, 2))
        ax.text(0.5, 0.5, "No metrics to display", ha="center", va="center")
        ax.axis("off")
        return _fig_to_base64(fig)

    y = np.arange(len(metric_names))
    fig, ax = plt.subplots(figsize=(8, max(3, len(metric_names) * 0.8)))

    ax.barh(y, values, color=colors, alpha=0.85, label="Value")

    # Threshold markers
    for i, t in enumerate(thresholds):
        ax.plot(
            [t, t], [i - 0.4, i + 0.4], color="#1f2937", linewidth=2, linestyle="--"
        )

    ax.set_yticks(y)
    ax.set_yticklabels(metric_names, fontsize=10)
    ax.set_xlabel("Value", fontsize=11)
    ax.set_title(
        f"Fairness Metrics — {attr_name.replace('_', ' ').title()}", fontsize=13
    )
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    return _fig_to_base64(fig)


def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
