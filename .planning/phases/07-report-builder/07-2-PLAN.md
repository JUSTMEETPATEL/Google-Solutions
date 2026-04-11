---
phase: 07
plan: 2
title: "Chart Generation Module"
wave: 1
depends_on: []
files_modified:
  - src/faircheck/reports/charts.py
requirements: [RPT-05]
autonomous: true
---

# Plan 07-2: Chart Generation Module

<objective>
Build the Matplotlib chart generator that produces per-group performance bar charts from analysis results. Charts are rendered as base64 PNG strings for embedding in HTML/PDF reports (D-02).
</objective>

<must_haves>
- Generate grouped bar charts for per-group metrics (accuracy, precision, recall, F1)
- Generate metric comparison charts (threshold vs actual value with color coding)
- Output as base64-encoded PNG strings (for HTML data URI embedding)
- Support multiple protected attributes (one chart per attribute)
- Non-interactive backend (Agg) for server-side rendering
</must_haves>

## Tasks

<task id="07-2-1" title="Create chart generation module">
<action>
Create `src/faircheck/reports/charts.py`:

```python
from __future__ import annotations
import base64
import io
from typing import Any
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def generate_charts(analysis_results: dict[str, Any]) -> dict[str, str]:
    """Generate all report charts as base64 PNG strings.
    
    Returns dict mapping chart name to base64 string.
    """
    charts = {}
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
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, metric in enumerate(metric_names):
        values = [breakdown[g].get(metric, 0) for g in groups]
        ax.bar(x + i * width, values, width, label=metric.capitalize())
    
    ax.set_xlabel("Group")
    ax.set_ylabel("Score")
    ax.set_title(f"Performance by {attr_name.replace('_', ' ').title()}")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(groups)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    return _fig_to_base64(fig)

def _metrics_comparison_chart(attr_name: str, metrics: dict) -> str:
    """Horizontal bar chart: metric value vs threshold."""
    metric_names = []
    values = []
    thresholds = []
    colors = []
    
    status_colors = {"pass": "#22c55e", "warning": "#eab308", "fail": "#ef4444", "skipped": "#94a3b8"}
    
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
    
    ax.barh(y, values, color=colors, alpha=0.8, label="Value")
    for i, t in enumerate(thresholds):
        ax.plot([t, t], [i - 0.4, i + 0.4], color="black", linewidth=2, linestyle="--")
    
    ax.set_yticks(y)
    ax.set_yticklabels(metric_names)
    ax.set_xlabel("Value")
    ax.set_title(f"Fairness Metrics — {attr_name.replace('_', ' ').title()}")
    ax.invert_yaxis()
    
    return _fig_to_base64(fig)

def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
```
</action>

<acceptance_criteria>
- `charts.py` contains `generate_charts` function returning dict of base64 strings
- `_performance_bar_chart` creates grouped bar chart with 4 metrics
- `_metrics_comparison_chart` creates horizontal bar with threshold lines  
- matplotlib uses "Agg" backend (non-interactive)
- Charts close figures after rendering (no memory leak)
</acceptance_criteria>
</task>

<verification>
1. `python -c "from faircheck.reports.charts import generate_charts; print('OK')"` exits 0
</verification>
