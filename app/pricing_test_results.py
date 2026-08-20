from __future__ import annotations

from typing import Any

import pandas as pd

from app.ui import money, pct
from lab.copy import CURRENT_PRICING, NEW_MODEL
from monitor.test_results import comparison_sentence, summarise

METRIC_ROWS = (
    "Revenue per passenger (AED)",
    "Purchase rate (%)",
    "Average selling price (AED)",
)


def results_table(stats: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            CURRENT_PRICING: [
                money(stats["current_revpp"]),
                pct(stats["current_conversion"]),
                money(stats["current_asp"]),
            ],
            NEW_MODEL: [
                money(stats["new_revpp"]),
                pct(stats["new_conversion"]),
                money(stats["new_asp"]),
            ],
        },
        index=list(METRIC_ROWS),
    )


def formatted_summary_lines(stats: dict[str, Any]) -> list[str]:
    return [
        f"**Revenue impact:** {stats['revenue_impact']:+.1%}",
        f"**Conversion impact:** {stats['conversion_impact_pp']:+.1f} percentage points",
        f"**Business-rule violations:** {stats['business_rule_violations']}",
    ]


def results_view(offers: pd.DataFrame) -> dict[str, Any]:
    stats = summarise(offers)
    return {
        "stats": stats,
        "table": results_table(stats),
        "sentence": comparison_sentence(stats),
        "summary_lines": formatted_summary_lines(stats),
    }
