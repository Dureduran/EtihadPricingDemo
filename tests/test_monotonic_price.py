from lab.constants import FIXTURE_BOOKING
from new_model.score import predict_buy_proba
from lab.paths import MODEL_PATH
import pytest


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="train first")
def test_higher_price_does_not_increase_p_buy():
    low = dict(FIXTURE_BOOKING, displayed_price=80)
    high = dict(FIXTURE_BOOKING, displayed_price=150)
    p_low = predict_buy_proba(low)
    p_high = predict_buy_proba(high)
    assert 0 <= p_high <= 1
    assert 0 <= p_low <= 1
    assert p_high <= p_low + 1e-6
