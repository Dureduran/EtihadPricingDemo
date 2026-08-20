from datetime import date
from pathlib import Path

from app.pricing_controls import (
    DEFAULT_PRODUCT,
    DEFAULT_ROUTE,
    STATUSES,
    TRAFFIC_STEPS,
    add_temporary_cap,
    increase_testing,
    load_controls,
    pause_controls,
    return_to_current_pricing,
    save_controls,
)
from app.ui import SIMULATED_BANNER
from lab.caps import caps_for_rules
from lab.constants import FIXTURE_BOOKING
from lab.copy import BUSINESS_RULES, CURRENT_PRICING, FORBIDDEN_UI_WORDS, NEW_MODEL, RETURN_TO_CURRENT
from new_model.recommend import recommend
from rollout import assign_new_model

PAGE = Path(__file__).resolve().parents[1] / "app" / "pages" / "2_Pricing_Controls.py"


def _patch_state(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("rollout.ROLLOUT_STATE", tmp_path / "rollout.json")
    monkeypatch.setattr("rollout.STATE_DIR", tmp_path)
    monkeypatch.setattr("rollout.TEMP_CAPS", tmp_path / "temporary_caps.json")


def test_default_is_extra_legroom_auh_lhr():
    assert DEFAULT_ROUTE == "AUH-LHR"
    assert DEFAULT_PRODUCT == "extra_legroom"
    assert STATUSES == ("TESTING", "PAUSED", "CURRENT_PRICING")
    assert TRAFFIC_STEPS == (0, 5, 20, 50, 100)


def test_controls_show_traffic_band_and_status(tmp_path, monkeypatch):
    _patch_state(monkeypatch, tmp_path)
    cfg = load_controls()
    saved = save_controls(
        cfg,
        status="TESTING",
        traffic_percent=20,
        allowed_min=80,
        allowed_max=150,
    )
    loaded = load_controls(DEFAULT_ROUTE, DEFAULT_PRODUCT)
    assert saved.traffic_percent == 20
    assert loaded.allowed_min == 80
    assert loaded.allowed_max == 150
    assert loaded.status == "TESTING"


def test_increase_pause_and_return_persist_and_drive_assignment(tmp_path, monkeypatch):
    _patch_state(monkeypatch, tmp_path)
    live = increase_testing(DEFAULT_ROUTE, DEFAULT_PRODUCT, "20")
    assert live.traffic_percent == 20
    assert live.status == "TESTING"
    hits = sum(assign_new_model(f"id-{i}", live) for i in range(500))
    assert 0.10 < hits / 500 < 0.30

    paused = pause_controls(DEFAULT_ROUTE, DEFAULT_PRODUCT)
    assert paused.status == "PAUSED"
    assert assign_new_model("B1", paused) is False

    returned = return_to_current_pricing(DEFAULT_ROUTE, DEFAULT_PRODUCT)
    reloaded = load_controls()
    assert returned.status == "CURRENT_PRICING"
    assert reloaded.status == "CURRENT_PRICING"
    assert assign_new_model("B1", reloaded) is False
    hits_after = sum(assign_new_model(f"id-{i}", reloaded) for i in range(200))
    assert hits_after == 0


def test_temporary_cap_limits_customer_price(tmp_path, monkeypatch):
    _patch_state(monkeypatch, tmp_path)
    add_temporary_cap(DEFAULT_ROUTE, DEFAULT_PRODUCT, 130, date(2026, 8, 31))
    monkeypatch.setattr(
        "new_model.recommend.new_model_recommended_price",
        lambda booking, allowed_min=None, allowed_max=None: (175.0, 0.4),
    )
    out = recommend(FIXTURE_BOOKING, temporary_caps=caps_for_rules(), persist=False)
    assert out["customer_price"] <= 130
    assert "temporary_rm_cap" in out["rule_reason_codes"]


def test_no_per_booking_approve_on_controls_screen():
    text = PAGE.read_text(encoding="utf-8")
    assert "per-passenger approval" in text
    assert "st.button(\"Approve\")" not in text
    assert "st.button(\"Accept\")" not in text
    assert "st.button(\"Reject\")" not in text
    from app import pricing_controls as module

    names = [name for name in dir(module) if "approve" in name.lower() or name.lower() in {"accept", "reject"}]
    assert names == []


def test_disclaimer_banner_and_required_labels():
    text = PAGE.read_text(encoding="utf-8")
    assert "page_header(" in text
    assert SIMULATED_BANNER == "Simulated result using synthetic/public data."
    for name in ("CURRENT_PRICING", "NEW_MODEL", "BUSINESS_RULES", "RETURN_TO_CURRENT"):
        assert name in text
    for word in FORBIDDEN_UI_WORDS:
        assert word not in text
    assert "fare_upgrade" not in text
