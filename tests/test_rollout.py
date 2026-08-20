from rollout import RolloutConfig, assign_new_model, is_shadow


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
