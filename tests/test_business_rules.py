from datetime import date

from business_rules import apply_business_rules, TemporaryCap
from current_pricing import current_price
from fallback import run_fallback
from lab.constants import FIXTURE_BOOKING, SAFE_FIXED


def test_current_pricing_not_constant():
    a = current_price(
        route="AUH-LHR",
        days_to_departure=4,
        product_type="extra_legroom",
        channel="web",
        remaining_extra_legroom=7,
    )
    b = current_price(
        route="AUH-BOM",
        days_to_departure=40,
        product_type="extra_baggage",
        channel="web",
        remaining_extra_legroom=20,
    )
    assert a != b
    assert a > 0 and b > 0


def test_cap_175_to_150():
    result = apply_business_rules(
        recommended_price=175,
        product_type="extra_legroom",
        fare_type="Basic",
        loyalty="None",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=7,
        allowed_max=150,
        route="AUH-LHR",
    )
    assert result.customer_price == 150
    assert result.offered
    assert "max_price" in result.reason_codes


def test_zero_inventory_not_sold():
    result = apply_business_rules(
        recommended_price=120,
        product_type="extra_legroom",
        fare_type="Basic",
        loyalty="None",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=0,
        route="AUH-LHR",
    )
    assert result.offered is False
    assert result.customer_price is None


def test_included_in_fare_no_positive_price():
    result = apply_business_rules(
        recommended_price=120,
        product_type="extra_legroom",
        fare_type="Deluxe",
        loyalty="None",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=7,
        route="AUH-LHR",
    )
    assert result.customer_price == 0.0
    assert "included_in_fare" in result.reason_codes


def test_loyalty_complimentary_seat_is_free():
    result = apply_business_rules(
        recommended_price=120,
        product_type="extra_legroom",
        fare_type="Basic",
        loyalty="Gold",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=7,
        route="AUH-LHR",
    )
    assert result.customer_price == 0.0
    assert result.offered is False
    assert "loyalty_complimentary" in result.reason_codes


def test_baggage_online_cheaper_than_airport():
    web = current_price(
        route="AUH-LHR",
        days_to_departure=21,
        product_type="extra_baggage",
        channel="web",
        remaining_extra_legroom=10,
    )
    airport = current_price(
        route="AUH-LHR",
        days_to_departure=21,
        product_type="extra_baggage",
        channel="airport",
        remaining_extra_legroom=10,
    )
    assert web < airport


def test_complimentary_seat_both_current_and_new_model_paths():
    shared = dict(
        product_type="extra_legroom",
        fare_type="Basic",
        loyalty="Platinum",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=7,
        route="AUH-LHR",
    )
    current = apply_business_rules(
        recommended_price=current_price(
            route="AUH-LHR",
            days_to_departure=4,
            product_type="extra_legroom",
            channel="web",
            remaining_extra_legroom=7,
        ),
        **shared,
    )
    new_model = apply_business_rules(recommended_price=175, **shared)
    assert current.customer_price == 0.0
    assert new_model.customer_price == 0.0


def test_fare_brand_inclusion_is_documented_stand_in():
    from pathlib import Path

    readme = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
    assert "portfolio stand-in" in readme.lower() or "portfolio stand-ins" in readme.lower()
    assert "not Etihad production logic" in readme
    result = apply_business_rules(
        recommended_price=175,
        product_type="extra_legroom",
        fare_type="Basic",
        loyalty="None",
        cabin="Economy",
        channel="web",
        remaining_extra_legroom=7,
        route="AUH-LHR",
        temporary_caps=[
            TemporaryCap(route="AUH-LHR", product_type="extra_legroom", max_price=130, until=date(2099, 8, 31))
        ],
    )
    assert result.customer_price == 130


def test_fallback_new_model_then_current():
    ok = run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=lambda: 145.0,
    )
    assert ok.fallback_layer == "new_model"
    assert ok.customer_price == 145.0

    down = run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=lambda: (_ for _ in ()).throw(RuntimeError("down")),
    )
    assert down.fallback_layer == "current_pricing"
    assert down.customer_price > 0


def test_fallback_to_safe_fixed(monkeypatch):
    import fallback as fb

    def boom(**kwargs):
        raise RuntimeError("current down")

    monkeypatch.setattr("fallback.current_price", boom)
    monkeypatch.setattr("fallback.simple_rules_price", boom)
    result = fb.run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=None,
    )
    assert result.fallback_layer == "safe_fixed"
    assert result.customer_price == SAFE_FIXED["extra_legroom"]
