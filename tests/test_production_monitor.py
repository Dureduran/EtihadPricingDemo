from pathlib import Path

import pandas as pd

from app.pricing_controls import DEFAULT_PRODUCT, DEFAULT_ROUTE, load_controls
from app.production_monitor import (
    SECTIONS,
    monitor_report,
    pause_from_monitor,
    return_to_current_from_monitor,
)
from app.ui import DISCLAIMER, SIMULATED_BANNER
from lab.copy import FORBIDDEN_UI_WORDS, RETURN_TO_CURRENT, ROLLOUT_DECISION
from monitor.health import (
    DRIFT_GAP_THRESHOLD,
    FALLBACK_RATE_THRESHOLD,
    FAILURE_RATE_THRESHOLD,
    HOLD_DRIFT_REASON,
    behaviour_changed,
    drift_gap,
    failure_rate,
    health,
)

PAGE = Path(__file__).resolve().parents[1] / "app" / "pages" / "4_Production_Monitor.py"
CONTROLS = Path(__file__).resolve().parents[1] / "app" / "pages" / "2_Pricing_Controls.py"


def _base(**overrides) -> pd.DataFrame:
    rows = {
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
    rows.update(overrides)
    return pd.DataFrame(rows)


def test_sections_have_pass_warn_fail_states():
    report = monitor_report(_base())
    assert report["commercial"]["revenue"]["state"] in {"pass", "warn", "fail"}
    assert report["commercial"]["conversion"]["state"] in {"pass", "warn", "fail"}
    assert report["model_health"]["predictions_accurate"]["state"] in {"pass", "warn", "fail"}
    assert report["model_health"]["customer_behaviour_changed"]["state"] in {"pass", "warn", "fail"}
    assert report["system_health"]["pricing_failures"]["state"] in {"pass", "warn", "fail"}
    assert report["system_health"]["fallback_usage"]["state"] in {"pass", "warn", "fail"}
    assert report["business_rules"]["violations"]["state"] in {"pass", "warn", "fail"}
    assert SECTIONS == (
        "Commercial performance",
        "Model health",
        "System health",
        "Business rules",
    )


def test_auh_bom_short_dtd_drift_sets_hold():
    frame = _base()
    assert drift_gap(frame) > DRIFT_GAP_THRESHOLD
    assert behaviour_changed(frame) is True
    report = health(frame)
    assert report["decision"] == "HOLD"
    assert report["reason"] == HOLD_DRIFT_REASON
    assert "seven days" in report["reason"]
    matched = _base(realised_purchase=[1, 1, 1], p_buy_new=[0.24, 0.40, 0.42])
    assert behaviour_changed(matched) is False
    matched_report = health(matched)
    assert matched_report["reason"] != HOLD_DRIFT_REASON


def test_failure_and_fallback_thresholds():
    clean = _base(route=["AUH-LHR", "AUH-LHR", "AUH-LHR"], realised_purchase=[1, 1, 1])
    assert failure_rate(clean) == 0.0
    ok = health(clean, fallback_rate=0.0)
    assert ok["system_health"]["pricing_failures"]["state"] == "pass"
    assert ok["system_health"]["fallback_usage"]["state"] == "pass"
    failed = health(clean, fallback_rate=FAILURE_RATE_THRESHOLD)
    assert failed["system_health"]["pricing_failures"]["state"] == "fail"
    high_fallback = health(clean, fallback_rate=FALLBACK_RATE_THRESHOLD)
    assert high_fallback["system_health"]["fallback_usage"]["state"] == "fail"


def test_pause_and_return_reuse_pricing_controls(tmp_path, monkeypatch):
    monkeypatch.setattr("rollout.ROLLOUT_STATE", tmp_path / "rollout.json")
    monkeypatch.setattr("rollout.STATE_DIR", tmp_path)
    paused = pause_from_monitor()
    assert paused.status == "PAUSED"
    assert load_controls(DEFAULT_ROUTE, DEFAULT_PRODUCT).status == "PAUSED"
    returned = return_to_current_from_monitor()
    assert returned.status == "CURRENT_PRICING"
    assert load_controls(DEFAULT_ROUTE, DEFAULT_PRODUCT).status == "CURRENT_PRICING"


def test_page_leads_with_rollout_decision_not_accuracy():
    text = PAGE.read_text(encoding="utf-8")
    assert "page_header(" in text
    assert ROLLOUT_DECISION in text
    assert "pause_from_monitor" in text
    assert "return_to_current_from_monitor" in text
    assert SIMULATED_BANNER in text or "SIMULATED_BANNER" in text
    assert DISCLAIMER == DISCLAIMER
    assert text.index("ROLLOUT_DECISION") < text.index("Predictions accurate")
    assert "89%" not in text
    assert "st.button(\"Expand to 100" not in text
    assert "increase_testing" not in text
    assert "100%" in text
    assert "does not auto-expand traffic to 100%" in text
    assert "etihad.com" not in text.lower()
    for word in FORBIDDEN_UI_WORDS:
        assert word not in text


def test_did_not_rebuild_pricing_controls_page():
    controls = CONTROLS.read_text(encoding="utf-8")
    assert "Pricing Controls" in controls or "page_header(" in controls
    monitor = PAGE.read_text(encoding="utf-8")
    assert "save_controls(" not in monitor
    assert "TRAFFIC_STEPS" not in monitor
    assert RETURN_TO_CURRENT in monitor or "RETURN_TO_CURRENT" in monitor
