from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from lab.constants import (
    COMPLIMENTARY_SEAT_TIERS,
    FARE_INCLUDES,
    MAX_PRICE,
    MIN_PRICE,
)


@dataclass
class TemporaryCap:
    route: str
    product_type: str
    max_price: float
    until: date


@dataclass
class RuleResult:
    customer_price: float | None
    offered: bool
    reason_codes: list[str] = field(default_factory=list)
    recommended_price: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "customer_price": self.customer_price,
            "offered": self.offered,
            "reason_codes": list(self.reason_codes),
            "recommended_price": self.recommended_price,
        }


def fare_includes_product(fare_type: str, product_type: str) -> bool:
    return product_type in FARE_INCLUDES.get(fare_type, set())


def loyalty_comp_seat(loyalty: str, product_type: str, cabin: str) -> bool:
    return (
        product_type == "extra_legroom"
        and cabin == "Economy"
        and loyalty in COMPLIMENTARY_SEAT_TIERS
    )


def apply_business_rules(
    *,
    recommended_price: float,
    product_type: str,
    fare_type: str,
    loyalty: str,
    cabin: str,
    channel: str,
    remaining_extra_legroom: int,
    allowed_min: float | None = None,
    allowed_max: float | None = None,
    temporary_caps: list[TemporaryCap] | None = None,
    route: str = "",
    today: date | None = None,
) -> RuleResult:
    """Business Rules have final control. The model recommends; this function decides."""
    reasons: list[str] = []
    today = today or date.today()

    if product_type == "extra_legroom" and remaining_extra_legroom <= 0:
        return RuleResult(
            customer_price=None,
            offered=False,
            reason_codes=["no_inventory"],
            recommended_price=recommended_price,
        )

    if fare_includes_product(fare_type, product_type):
        return RuleResult(
            customer_price=0.0,
            offered=False,
            reason_codes=["included_in_fare"],
            recommended_price=recommended_price,
        )

    if loyalty_comp_seat(loyalty, product_type, cabin):
        return RuleResult(
            customer_price=0.0,
            offered=False,
            reason_codes=["loyalty_complimentary"],
            recommended_price=recommended_price,
        )

    floor = MIN_PRICE[product_type]
    ceiling = MAX_PRICE[product_type]
    if allowed_min is not None:
        floor = max(floor, allowed_min)
    if allowed_max is not None:
        ceiling = min(ceiling, allowed_max)

    if temporary_caps:
        for cap in temporary_caps:
            if cap.route == route and cap.product_type == product_type and today <= cap.until:
                ceiling = min(ceiling, cap.max_price)
                reasons.append("temporary_rm_cap")

    # Airport bags are never cheaper than the digital price after rules.
    price = float(recommended_price)
    if product_type == "extra_baggage" and channel == "airport":
        digital_like = price / 1.35
        if price < digital_like * 1.2:
            price = max(price, round(digital_like * 1.25 / 5) * 5)
            reasons.append("airport_vs_online_bag")

    if price < floor:
        price = floor
        reasons.append("min_price")
    if price > ceiling:
        price = ceiling
        reasons.append("max_price")

    if abs(price - recommended_price) > 0.01 and "max_price" not in reasons and "min_price" not in reasons:
        if price < recommended_price:
            reasons.append("capped_below_recommendation")

    if price != recommended_price and recommended_price > ceiling:
        if "max_price" not in reasons:
            reasons.append("max_price")

    return RuleResult(
        customer_price=float(price),
        offered=True,
        reason_codes=reasons or ["rules_passed"],
        recommended_price=float(recommended_price),
    )
