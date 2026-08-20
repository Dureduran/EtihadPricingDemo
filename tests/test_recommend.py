import pytest

from lab.constants import FIXTURE_BOOKING
from lab.paths import MODEL_PATH
from new_model.recommend import recommend


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="train first")
def test_recommend_fixture_has_both_systems():
    out = recommend(FIXTURE_BOOKING)
    assert out["current_price"] > 0
    assert out["new_model_recommended_price"] > 0
    assert "p_buy_current" in out
    assert "expected_revenue_current" in out
    assert out["fallback_layer"] in {"new_model", "current_pricing", "simple_rules", "safe_fixed"}


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="train first")
def test_recommend_respects_max():
    out = recommend(FIXTURE_BOOKING, allowed_max=150)
    assert out["customer_price"] <= 150


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="train first")
def test_recommend_fallback_on_error():
    out = recommend(FIXTURE_BOOKING, force_new_model_error=True)
    assert out["fallback_layer"] != "new_model"
    assert out["current_price"] > 0
