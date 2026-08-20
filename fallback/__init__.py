from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from lab.constants import SAFE_FIXED
from current_pricing import current_price, simple_rules_price


@dataclass
class FallbackResult:
    customer_price: float | None
    fallback_layer: str
    error: str | None = None


def run_fallback(
    *,
    product_type: str,
    route: str,
    days_to_departure: int,
    channel: str,
    remaining_extra_legroom: int,
    new_model_fn: Callable[[], float] | None,
) -> FallbackResult:
    """New Model → Current Pricing → simple pricing rules → safe fixed price."""
    if new_model_fn is not None:
        try:
            price = new_model_fn()
            if price is None:
                raise ValueError("new_model_returned_null")
            return FallbackResult(customer_price=float(price), fallback_layer="new_model")
        except Exception as exc:  # noqa: BLE001 — checkout must never fail open
            new_model_error = str(exc)
    else:
        new_model_error = "new_model_unavailable"

    try:
        price = current_price(
            route=route,
            days_to_departure=days_to_departure,
            product_type=product_type,
            channel=channel,
            remaining_extra_legroom=remaining_extra_legroom,
        )
        return FallbackResult(
            customer_price=float(price),
            fallback_layer="current_pricing",
            error=new_model_error,
        )
    except Exception as exc:  # noqa: BLE001
        current_error = str(exc)

    try:
        price = simple_rules_price(
            days_to_departure=days_to_departure, product_type=product_type
        )
        return FallbackResult(
            customer_price=float(price),
            fallback_layer="simple_rules",
            error=current_error,
        )
    except Exception as exc:  # noqa: BLE001
        simple_error = str(exc)

    return FallbackResult(
        customer_price=float(SAFE_FIXED[product_type]),
        fallback_layer="safe_fixed",
        error=simple_error,
    )
