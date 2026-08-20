from __future__ import annotations

from typing import Any, Mapping

from lab.constants import LONG_HAUL
from lab.copy import BUSINESS_RULES


def why_lines(booking: Mapping[str, Any], result: Mapping[str, Any]) -> list[str]:
    """Plain-language reasons a Revenue Management analyst can use."""
    lines: list[str] = []
    dtd = int(booking["days_to_departure"])
    remaining = int(booking["remaining_extra_legroom"])
    product = booking["product_type"]

    if dtd <= 7:
        lines.append("departure is close")
    if booking["route"] in LONG_HAUL:
        lines.append("long-haul flight")
    if product == "extra_legroom" and remaining <= 8:
        lines.append("few extra-legroom seats remain")
    if booking["fare_type"] in {"Basic", "Value"} and product == "extra_legroom":
        lines.append("fare does not already include the seat")
    if booking["fare_type"] == "Basic" and product == "extra_baggage":
        lines.append("fare does not already include extra baggage")
    if "max_price" in result.get("rule_reason_codes", []) or "temporary_rm_cap" in result.get(
        "rule_reason_codes", []
    ):
        rec = result.get("new_model_recommended_price")
        cust = result.get("customer_price")
        if rec is not None and cust is not None and rec > cust:
            lines.append(
                f"{BUSINESS_RULES} capped the recommendation from AED {rec:.0f} to AED {cust:.0f}"
            )
    if not lines:
        lines.append("booking context and remaining inventory relative to Current Pricing")
    return lines
