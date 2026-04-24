"""Gemini-powered summaries for fairness scan outputs.

This module is intentionally fail-safe: if Gemini is not configured or unavailable,
callers still get a structured result and the main scan flow continues.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional at import time
    load_dotenv = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_prompt(
    model_name: str,
    analysis_results: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> str:
    overall_risk = analysis_results.get("overall_risk_level", "unknown")
    results = analysis_results.get("results", {})

    compact_results: dict[str, dict[str, Any]] = {}
    for attr_name, attr_data in results.items():
        metric_map = attr_data.get("metrics", {})
        compact_results[attr_name] = {}
        for metric_name, metric_data in metric_map.items():
            compact_results[attr_name][metric_name] = {
                "value": metric_data.get("value"),
                "status": metric_data.get("status"),
                "threshold": metric_data.get("threshold"),
            }

    compact_recs = [
        {
            "algorithm": r.get("algorithm"),
            "confidence": r.get("confidence"),
            "category": r.get("category"),
            "rationale": r.get("rationale"),
            "addresses": r.get("addresses", []),
            "priority": r.get("priority"),
        }
        for r in recommendations
    ]

    return (
        "You are a fairness and compliance assistant. "
        "Given fairness scan outputs, produce concise, non-technical text for compliance stakeholders.\n\n"
        "Return strict JSON with keys: executive_summary, top_risks, recommended_actions.\n"
        "- executive_summary: 2-3 sentences.\n"
        "- top_risks: list of 3 short bullets.\n"
        "- recommended_actions: list of 3 short bullets.\n"
        "- Do not include markdown fences.\n"
        "- Keep total response under 180 words.\n\n"
        f"Model Name: {model_name}\n"
        f"Overall Risk: {overall_risk}\n"
        f"Metrics by attribute: {json.dumps(compact_results, default=str)}\n"
        f"Mitigation recommendations: {json.dumps(compact_recs, default=str)}\n"
    )


def _build_fallback(
    error: str,
    model: str,
    generated: bool = False,
) -> dict[str, Any]:
    return {
        "provider": "google-gemini",
        "model": model,
        "generated": generated,
        "generated_at": _utcnow_iso(),
        "executive_summary": None,
        "top_risks": [],
        "recommended_actions": [],
        "error": error,
    }


def generate_scan_summary(
    model_name: str,
    analysis_results: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate an optional Gemini summary for scan output.

    Configuration:
    - GEMINI_API_KEY: required to enable calls
    - GEMINI_MODEL: optional, defaults to gemini-2.5-flash-lite
    """
    # Load .env if available so local configuration works without manual export.
    if load_dotenv is not None:
        load_dotenv(override=False)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip() or "gemini-2.5-flash-lite"

    if not api_key:
        return _build_fallback(
            error="Gemini disabled: GEMINI_API_KEY not configured.",
            model=model,
        )

    prompt = _build_prompt(
        model_name=model_name,
        analysis_results=analysis_results,
        recommendations=recommendations,
    )

    try:
        from google import genai
    except ImportError:
        logger.warning("google-genai package not installed; skipping Gemini summary")
        return _build_fallback(
            error="Gemini disabled: google-genai package not installed.",
            model=model,
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        raw_text = getattr(response, "text", None)
        if not raw_text:
            return _build_fallback(
                error="Gemini returned empty response.",
                model=model,
            )

        parsed = json.loads(raw_text)
        return {
            "provider": "google-gemini",
            "model": model,
            "generated": True,
            "generated_at": _utcnow_iso(),
            "executive_summary": parsed.get("executive_summary"),
            "top_risks": parsed.get("top_risks", []),
            "recommended_actions": parsed.get("recommended_actions", []),
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        logger.warning("Gemini summary generation failed: %s", exc)
        return _build_fallback(
            error=f"Gemini request failed: {exc}",
            model=model,
        )
