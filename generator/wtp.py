"""Hidden willingness-to-pay generator. Training code must not import this package."""

from __future__ import annotations

import numpy as np

from lab.constants import LONG_HAUL, ROUTE_HAUL_HOURS


def latent_wtp(
    *,
    rng: np.random.Generator,
    route: str,
    days_to_departure: int,
    product_type: str,
    channel: str,
    remaining_extra_legroom: int,
    loyalty: str,
    cabin: str,
    party_size: int,
) -> tuple[float, str, float]:
    """Return (wtp, generator_rule_id, true_elasticity). Not a training feature."""
    hours = ROUTE_HAUL_HOURS[route]
    dtd = int(days_to_departure)
    remaining = int(remaining_extra_legroom)

    if product_type == "extra_legroom":
        base = 70 + 8 * hours
        if dtd <= 5:
            base += 40
        elif dtd <= 14:
            base += 18
        if remaining <= 5:
            base += 28
        elif remaining <= 10:
            base += 12
        if route in LONG_HAUL:
            base += 15
        if cabin == "Business":
            base += 25
        if loyalty in {"Gold", "Platinum"}:
            base += 10
        elasticity = -1.15 if dtd > 14 else -0.7
        rule = "seat_scarcity_dtd_haul"
    else:
        base = 55 + 5 * hours
        if dtd <= 3:
            base += 35
        if channel == "airport":
            base += 20
        if party_size >= 3:
            base += 25
        if cabin == "Business":
            base += 15
        elasticity = -1.3 if channel != "airport" else -0.85
        rule = "bag_party_channel_dtd"

    noise = float(rng.normal(0, 18))
    wtp = max(20.0, base + noise)
    return wtp, rule, elasticity
