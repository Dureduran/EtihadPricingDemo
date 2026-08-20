import pandas as pd
import pytest

from monitor.health import health
from monitor.test_results import comparison_sentence, summarise


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
    current_rev = (120.0 * 0.27 + 90.0 * 0.30 + 95.0 * 0.28) / 3
    new_rev = (145.0 * 0.24 + 110.0 * 0.40 + 120.0 * 0.42) / 3
    current_conv = (0.27 + 0.30 + 0.28) / 3
    new_conv = (0.24 + 0.40 + 0.42) / 3
    assert stats["n"] == 3
    assert stats["business_rule_violations"] == 0
    assert stats["current_revpp"] == pytest.approx(current_rev)
    assert stats["new_revpp"] == pytest.approx(new_rev)
    assert stats["current_conversion"] == pytest.approx(current_conv)
    assert stats["new_conversion"] == pytest.approx(new_conv)
    assert stats["current_asp"] == pytest.approx((120.0 + 90.0 + 95.0) / 3)
    assert stats["new_asp"] == pytest.approx((145.0 + 110.0 + 120.0) / 3)
    assert stats["revenue_impact"] == pytest.approx(new_rev / current_rev - 1.0)
    assert stats["conversion_impact_pp"] == pytest.approx((new_conv - current_conv) * 100)


def test_health_hold_on_auh_bom_drift():
    report = health(_frame())
    assert report["model_health"]["drift_gap"] > 0.08
    assert report["decision"] == "HOLD"
    assert "AUH" in report["reason"] and "BOM" in report["reason"]
    assert "seven days" in report["reason"]
    assert report["model_health"]["customer_behaviour_changed"]["state"] == "warn"


def test_hold_reason_requires_computed_drift():
    frame = _frame()
    frame["realised_purchase"] = [1, 1, 1]
    report = health(frame)
    assert report["model_health"]["drift_gap"] <= 0.08
    assert "behaving differently" not in report["reason"]


def test_pricing_failure_and_fallback_thresholds():
    ok = health(_frame(), fallback_rate=0.0)
    assert ok["system_health"]["pricing_failures"]["state"] == "pass"
    assert ok["system_health"]["fallback_usage"]["state"] == "pass"
    bad = health(_frame(), fallback_rate=0.05)
    assert bad["system_health"]["pricing_failures"]["state"] == "fail"
    assert bad["system_health"]["fallback_usage"]["state"] == "fail"


def test_summarise_counts_business_rule_violations():
    frame = _frame()
    frame.loc[0, "rule_reason_codes"] = ["included_in_fare"]
    frame.loc[0, "customer_price"] = 80.0
    frame.loc[0, "offered"] = True
    stats = summarise(frame)
    assert stats["business_rule_violations"] == 1


def test_impact_sentence_uses_computed_stats():
    stats = summarise(_frame())
    sentence = comparison_sentence(stats)
    assert "in the simulation" in sentence
    assert "8.0%" not in sentence
    assert f"{abs(stats['revenue_impact']):.1%}" in sentence

