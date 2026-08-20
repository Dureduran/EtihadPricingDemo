from pathlib import Path

import pandas as pd

from app.pricing_test_results import METRIC_ROWS, results_view
from app.ui import SIMULATED_BANNER
from lab.copy import CURRENT_PRICING, FORBIDDEN_UI_WORDS, NEW_MODEL

PAGE = Path(__file__).resolve().parents[1] / "app" / "pages" / "3_Pricing_Test_Results.py"
MONITOR = Path(__file__).resolve().parents[1] / "app" / "pages" / "4_Production_Monitor.py"


def _offers():
    return pd.DataFrame(
        {
            "current_price": [120.0, 90.0, 95.0],
            "customer_price": [145.0, 110.0, 120.0],
            "p_buy_current": [0.27, 0.30, 0.28],
            "p_buy_new": [0.24, 0.40, 0.42],
            "arm": ["new_model", "new_model", "new_model"],
            "offered": [True, True, True],
            "rule_reason_codes": [["rules_passed"], ["rules_passed"], ["rules_passed"]],
            "realised_purchase": [1, 0, 0],
            "served_price": [145.0, 110.0, 120.0],
        }
    )


def test_results_view_table_from_logged_offers():
    view = results_view(_offers())
    table = view["table"]
    assert list(table.index) == list(METRIC_ROWS)
    assert CURRENT_PRICING in table.columns
    assert NEW_MODEL in table.columns
    assert view["stats"]["n"] == 3
    assert "8.0%" not in view["sentence"]
    assert "Revenue impact" in view["summary_lines"][0]
    assert "Conversion impact" in view["summary_lines"][1]
    assert "Business-rule violations" in view["summary_lines"][2]


def test_page_uses_pipeline_not_hardcoded_eight_percent():
    text = PAGE.read_text(encoding="utf-8")
    assert "results_view(" in text
    assert "page_header(" in text
    assert "pd.read_parquet" in text or "simulate_batch" in text
    assert "SIMULATED_BANNER" in text
    assert SIMULATED_BANNER == "Simulated result using synthetic/public data."
    assert "8.0%" not in text
    assert "live Etihad" not in text.lower()
    for word in FORBIDDEN_UI_WORDS:
        assert word not in text


def test_did_not_rebuild_production_monitor():
    text = MONITOR.read_text(encoding="utf-8")
    assert "Production Monitor" in text
    assert "page_header(" in text
