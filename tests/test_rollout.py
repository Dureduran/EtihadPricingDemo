from pathlib import Path

from lab.constants import FIXTURE_BOOKING, ROLLOUT_STEPS
from rollout import RolloutConfig, assign_new_model, get_config, is_shadow, upsert_config
from rollout.assignment import serve_booking
from rollout.ladder import (
    DISPLAY_STATES,
    LADDER_STATES,
    STATUSES,
    apply_step,
    current_step,
    set_step,
)

FAKE_RECOMMEND = {
    "current_price": 120.0,
    "new_model_recommended_price": 140.0,
    "customer_price": 140.0,
    "offered": True,
    "p_buy_current": 0.5,
    "p_buy_new": 0.4,
    "expected_revenue_current": 60.0,
    "expected_revenue_new": 56.0,
    "rule_reason_codes": ["ok"],
    "fallback_layer": "new_model",
}


def _patch_state(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("rollout.ROLLOUT_STATE", tmp_path / "rollout.json")
    monkeypatch.setattr("rollout.STATE_DIR", tmp_path)


def _patch_recommend(monkeypatch) -> None:
    monkeypatch.setattr(
        "rollout.assignment.recommend",
        lambda *args, **kwargs: dict(FAKE_RECOMMEND),
    )


def test_ladder_states_exist():
    assert LADDER_STATES == ROLLOUT_STEPS
    assert LADDER_STATES == (
        "offline",
        "shadow",
        "5",
        "20",
        "50",
        "100",
        "return_to_current",
    )
    assert DISPLAY_STATES == (
        "Offline testing",
        "Shadow mode",
        "5%",
        "20%",
        "50%",
        "100%",
        "Return to Current Pricing",
    )
    for step in LADDER_STATES:
        cfg = RolloutConfig(
            route="AUH-LHR",
            product_type="extra_legroom",
            status="TESTING",
            traffic_percent=20,
            shadow=False,
            allowed_min=80,
            allowed_max=150,
        )
        assert current_step(apply_step(cfg, step)) == step


def test_shadow_never_assigns_live_new_model():
    cfg = RolloutConfig(
        route="AUH-LHR",
        product_type="extra_legroom",
        status="TESTING",
        traffic_percent=20,
        shadow=True,
        allowed_min=80,
        allowed_max=150,
    )
    assert is_shadow(cfg)
    assert assign_new_model("B1", cfg) is False
    assert current_step(cfg) == "shadow"


def test_shadow_serve_logs_new_model_but_customer_gets_current(monkeypatch):
    _patch_recommend(monkeypatch)
    cfg = apply_step(
        RolloutConfig(
            route="AUH-LHR",
            product_type="extra_legroom",
            status="TESTING",
            traffic_percent=20,
            shadow=False,
            allowed_min=80,
            allowed_max=150,
        ),
        "shadow",
    )
    for i in range(50):
        booking = dict(FIXTURE_BOOKING, booking_id=f"SH-{i}")
        out = serve_booking(booking, cfg)
        assert out["served_price"] == out["current_price"]
        assert out["new_model_recommended_price"] == 140.0
        assert out["arm"] == "current_shadow"
        assert out["shadow"] is True


def test_return_to_current_is_zero():
    cfg = RolloutConfig(
        route="AUH-LHR",
        product_type="extra_legroom",
        status="CURRENT_PRICING",
        traffic_percent=100,
        shadow=False,
        allowed_min=80,
        allowed_max=150,
    )
    assert assign_new_model("B1", cfg) is False
    assert current_step(cfg) == "return_to_current"


def test_return_to_current_persists(tmp_path, monkeypatch):
    _patch_state(monkeypatch, tmp_path)
    set_step("AUH-LHR", "extra_legroom", "20")
    saved = set_step("AUH-LHR", "extra_legroom", "return_to_current")
    loaded = get_config("AUH-LHR", "extra_legroom")
    assert saved.status == "CURRENT_PRICING"
    assert loaded.status == "CURRENT_PRICING"
    assert assign_new_model("B1", loaded) is False
    assert current_step(loaded) == "return_to_current"


def test_twenty_percent_is_stable():
    cfg = RolloutConfig(
        route="AUH-LHR",
        product_type="extra_legroom",
        status="TESTING",
        traffic_percent=20,
        shadow=False,
        allowed_min=80,
        allowed_max=150,
    )
    a = assign_new_model("booking-99", cfg)
    b = assign_new_model("booking-99", cfg)
    assert a is b
    hits = sum(assign_new_model(f"id-{i}", cfg) for i in range(2000))
    share = hits / 2000
    assert 0.14 < share < 0.26


def test_twenty_percent_serve_split(monkeypatch):
    _patch_recommend(monkeypatch)
    cfg = RolloutConfig(
        route="AUH-LHR",
        product_type="extra_legroom",
        status="TESTING",
        traffic_percent=20,
        shadow=False,
        allowed_min=80,
        allowed_max=150,
    )
    new_hits = 0
    for i in range(200):
        booking = dict(FIXTURE_BOOKING, booking_id=f"SP-{i}")
        out = serve_booking(booking, cfg)
        if out["arm"] == "new_model":
            new_hits += 1
            assert out["served_price"] == out["customer_price"]
        else:
            assert out["served_price"] == out["current_price"]
    assert 0.10 < new_hits / 200 < 0.30


def test_config_is_per_route_product_with_band_and_status(tmp_path, monkeypatch):
    _patch_state(monkeypatch, tmp_path)
    cfg = RolloutConfig(
        route="AUH-LHR",
        product_type="extra_legroom",
        status="TESTING",
        traffic_percent=20,
        shadow=False,
        allowed_min=80,
        allowed_max=150,
    )
    upsert_config(cfg)
    loaded = get_config("AUH-LHR", "extra_legroom")
    other = get_config("AUH-JFK", "extra_baggage")
    assert loaded.allowed_min == 80
    assert loaded.allowed_max == 150
    assert loaded.status in STATUSES
    assert other.route == "AUH-JFK"
    assert other.product_type == "extra_baggage"
    assert (loaded.route, loaded.product_type) != (other.route, other.product_type)


def test_no_per_passenger_approve_api():
    import rollout
    import rollout.assignment as assignment
    import rollout.ladder as ladder

    for module in (rollout, assignment, ladder):
        names = [name for name in dir(module) if "approve" in name.lower()]
        assert names == []
