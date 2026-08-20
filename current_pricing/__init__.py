from __future__ import annotations

from lab.constants import CURRENT_BASE_AED, MIN_PRICE


def current_price(
    *,
    route: str,
    days_to_departure: int,
    product_type: str,
    channel: str,
    remaining_extra_legroom: int,
) -> float:
    """Simulated Current Pricing: route, DTD, product, channel, remaining inventory."""
    base = CURRENT_BASE_AED[route][product_type]
    dtd = max(0, int(days_to_departure))
    # Closer to departure → higher price.
    dtd_mult = 1.0 + 0.018 * max(0, 21 - dtd)
    price = base * dtd_mult

    if product_type == "extra_legroom":
        remaining = int(remaining_extra_legroom)
        if remaining <= 3:
            price += 35
        elif remaining <= 8:
            price += 18
        elif remaining <= 14:
            price += 8

    if product_type == "extra_baggage" and channel == "airport":
        price *= 1.35

    if product_type == "extra_baggage" and channel in {"web", "app"} and dtd >= 2:
        price *= 0.92  # earlier digital purchase cheaper than airport

    price = round(price / 5) * 5
    return float(max(MIN_PRICE[product_type], price))


def simple_rules_price(*, days_to_departure: int, product_type: str) -> float:
    dtd = int(days_to_departure)
    if product_type == "extra_baggage":
        if dtd <= 2:
            return 140.0
        if dtd <= 10:
            return 100.0
        return 70.0
    if dtd <= 2:
        return 160.0
    if dtd <= 10:
        return 120.0
    return 80.0
