from current_pricing import current_price, simple_rules_price
from fallback import run_fallback
from lab.constants import SAFE_FIXED


def test_fallback_order_new_model_then_current():
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
        new_model_fn=lambda: (_ for _ in ()).throw(NotImplementedError("stub")),
    )
    assert down.fallback_layer == "current_pricing"
    assert down.customer_price == current_price(
        route="AUH-LHR",
        days_to_departure=4,
        product_type="extra_legroom",
        channel="web",
        remaining_extra_legroom=7,
    )


def test_fallback_current_null_uses_next_layer():
    down = run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=lambda: None,
    )
    assert down.fallback_layer == "current_pricing"
    assert down.customer_price is not None


def test_fallback_simple_rules_then_safe_fixed(monkeypatch):
    import fallback as fb

    monkeypatch.setattr(
        "fallback.current_price",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("current down")),
    )
    simple = fb.run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=None,
    )
    assert simple.fallback_layer == "simple_rules"
    assert simple.customer_price == simple_rules_price(
        days_to_departure=4, product_type="extra_legroom"
    )

    monkeypatch.setattr(
        "fallback.simple_rules_price",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("simple down")),
    )
    fixed = fb.run_fallback(
        product_type="extra_legroom",
        route="AUH-LHR",
        days_to_departure=4,
        channel="web",
        remaining_extra_legroom=7,
        new_model_fn=None,
    )
    assert fixed.fallback_layer == "safe_fixed"
    assert fixed.customer_price == SAFE_FIXED["extra_legroom"]
