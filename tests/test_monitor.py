import pandas as pd

from monitor.health import health
from monitor.test_results import summarise


def _frame():
    return pd.DataFrame(
        {
            "route": ["AUH-LHR", "AUH-BOM", "AUH-BOM"],
            "days_to_departure": [4, 3, 2],
            "current_price": [120.0, 90.0, 95.0],
            "new_model_recommended_price": [145.0, 110.0, 120.0],
            "customer_price": [145.0, 110.0, 120.0],
            "p_buy_current": [0.27, 0.30, 0.28],
            "p_buy_new": [0.24, 0.40, 0.42],
            "p_buy_at_recommendation": [0.24, 0.40, 0.42],
            "arm": ["new_model", "new_model", "new_model"],
            "offered": [True, True, True],
            "rule_reason_codes": [["rules_passed"], ["rules_passed"], ["rules_passed"]],
            "fallback_layer": ["new_model", "new_model", "new_model"],
            "realised_purchase": [1, 0, 0],
            "served_price": [145.0, 110.0, 120.0],
        }
    )


def test_summarise_hand_calc():
    stats = summarise(_frame())
    assert stats["n"] == 3
    assert stats["business_rule_violations"] == 0
    assert stats["current_revpp"] > 0
    assert stats["new_revpp"] > 0


def test_health_hold_on_auh_bom_drift():
    report = health(_frame())
    assert report["decision"] == "HOLD"
    assert "AUH" in report["reason"] and "BOM" in report["reason"]
