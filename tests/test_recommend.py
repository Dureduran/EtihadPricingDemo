import pandas as pd

from lab.constants import FIXTURE_BOOKING, PRICE_GRIDS, PRODUCTS
from lab.paths import MODEL_PATH
from new_model.recommend import expected_revenue, new_model_recommended_price, recommend
from new_model.score import predict_buy_proba

REQUIRED_KEYS = {
    "current_price",
    "new_model_recommended_price",
    "customer_price",
    "p_buy_current",
    "p_buy_new",
    "expected_revenue_current",
    "expected_revenue_new",
    "rule_reason_codes",
    "fallback_layer",
}


def test_model_artifact_present():
    assert MODEL_PATH.exists()


def test_recommend_fixture_has_both_systems():
    out = recommend(FIXTURE_BOOKING, persist=False)
    assert REQUIRED_KEYS <= set(out)
    assert out["current_price"] > 0
    assert out["new_model_recommended_price"] > 0
    assert out["expected_revenue_current"] == expected_revenue(
        out["current_price"], out["p_buy_current"]
    )
    assert out["expected_revenue_new"] == expected_revenue(
        out["customer_price"] or 0.0, out["p_buy_new"]
    )
    assert out["fallback_layer"] in {
        "new_model",
        "current_pricing",
        "simple_rules",
        "safe_fixed",
    }


def test_grid_search_picks_argmax_expected_revenue():
    rec, p = new_model_recommended_price(FIXTURE_BOOKING)
    best_price = None
    best_rev = -1.0
    for price in PRICE_GRIDS["extra_legroom"]:
        p_at = predict_buy_proba({**FIXTURE_BOOKING, "displayed_price": float(price)})
        rev = expected_revenue(price, p_at)
        if rev > best_rev:
            best_rev = rev
            best_price = float(price)
    assert rec == best_price
    assert abs(expected_revenue(rec, p) - best_rev) < 1e-9


def test_recommend_cap_lowers_175_to_150(monkeypatch):
    monkeypatch.setattr(
        "new_model.recommend.new_model_recommended_price",
        lambda booking, allowed_min=None, allowed_max=None: (175.0, 0.4),
    )
    out = recommend(FIXTURE_BOOKING, allowed_max=150, persist=False)
    assert out["new_model_recommended_price"] == 175
    assert out["customer_price"] == 150
    assert out["customer_price"] <= 150
    assert "max_price" in out["rule_reason_codes"]


def test_recommend_fallback_on_error():
    out = recommend(FIXTURE_BOOKING, force_new_model_error=True, persist=False)
    assert out["fallback_layer"] != "new_model"
    assert out["customer_price"] is not None


def test_extra_baggage_and_extra_legroom_supported_not_fare_upgrade():
    assert PRODUCTS == ("extra_baggage", "extra_legroom")
    assert "fare_upgrade" not in PRODUCTS
    bag = dict(FIXTURE_BOOKING, product_type="extra_baggage")
    out = recommend(bag, persist=False)
    assert out["current_price"] > 0
    assert out["new_model_recommended_price"] > 0
    seat = recommend(FIXTURE_BOOKING, persist=False)
    assert seat["current_price"] > 0


def test_result_persisted_to_offers_table(tmp_path, monkeypatch):
    log = tmp_path / "offers.parquet"
    monkeypatch.setattr("new_model.recommend.OFFERS_LOG", log)
    monkeypatch.setattr("new_model.recommend.STATE_DIR", tmp_path)
    recommend(FIXTURE_BOOKING, persist=True)
    assert log.exists()
    frame = pd.read_parquet(log)
    assert len(frame) >= 1
    assert "customer_price" in frame.columns
    assert "fallback_layer" in frame.columns
    assert "rule_reason_codes" in frame.columns
