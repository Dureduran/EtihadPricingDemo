from pathlib import Path

from app.price_explanation import explanation_view, fixture_booking
from app.ui import DISCLAIMER, HEADLINE, SIMULATED_BANNER, SUBTITLE, money, pct
from lab.copy import FORBIDDEN_UI_WORDS
from new_model.explain import why_lines

APP = Path(__file__).resolve().parents[1] / "app"
REQUIRED_WHY = (
    "departure is close",
    "long-haul",
    "few extra-legroom seats remain",
    "fare does not already include the seat",
)


def test_fixture_is_auh_lhr_economy_basic_four_days_seven_seats():
    booking = fixture_booking()
    assert booking["route"] == "AUH-LHR"
    assert booking["cabin"] == "Economy"
    assert booking["fare_type"] == "Basic"
    assert booking["days_to_departure"] == 4
    assert booking["remaining_extra_legroom"] == 7
    assert booking["product_type"] == "extra_legroom"


def test_shell_copy_on_every_app_page():
    sources = [APP / "Home.py", APP / "ui.py"]
    sources.extend(p for p in (APP / "pages").glob("*.py") if p.name != "__init__.py")
    for path in sources:
        text = path.read_text(encoding="utf-8")
        uses_header = "page_header(" in text or "render_price_explanation(" in text
        inline_shell = HEADLINE in text and SUBTITLE in text and DISCLAIMER in text
        assert uses_header or inline_shell, path


def test_home_is_price_explanation_default():
    home = (APP / "Home.py").read_text(encoding="utf-8")
    assert "render_price_explanation" in home


def test_explanation_shows_both_systems_in_aed():
    view = explanation_view()
    result = view["result"]
    assert result["current_price"] > 0
    assert result["new_model_recommended_price"] > 0
    assert 0 <= result["p_buy_current"] <= 1
    assert 0 <= result["p_buy_new"] <= 1
    assert result["expected_revenue_current"] == result["current_price"] * result["p_buy_current"]
    assert "AED" in money(result["current_price"])
    assert "%" in pct(result["p_buy_new"])


def test_why_lines_from_fixture_features():
    view = explanation_view()
    joined = " ".join(view["why"]).lower()
    for needle in REQUIRED_WHY:
        assert needle in joined
    far = dict(fixture_booking(), days_to_departure=40, remaining_extra_legroom=40, route="AUH-BOM")
    far_why = " ".join(why_lines(far, view["result"])).lower()
    assert "departure is close" not in far_why


def test_capped_recommendation_shows_recommended_vs_customer(monkeypatch):
    monkeypatch.setattr(
        "new_model.recommend.new_model_recommended_price",
        lambda booking, allowed_min=None, allowed_max=None: (175.0, 0.4),
    )
    view = explanation_view(allowed_max=150)
    assert view["show_cap"] is True
    result = view["result"]
    assert result["new_model_recommended_price"] == 175
    assert result["customer_price"] == 150


def test_simulated_banner_constant():
    assert SIMULATED_BANNER == "Simulated result using synthetic/public data."


def test_no_champion_challenger_or_fare_upgrade_on_explanation():
    text = (APP / "price_explanation.py").read_text(encoding="utf-8")
    for word in FORBIDDEN_UI_WORDS:
        assert word not in text
    assert "fare_upgrade" not in text
    assert "fare-brand upgrade" not in text.lower()
    view = explanation_view()
    assert view["booking"]["product_type"] != "fare_upgrade"
