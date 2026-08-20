from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from app.ui import money, page_header, pct
from lab.caps import caps_for_rules
from lab.constants import FIXTURE_BOOKING, PRODUCTS
from lab.copy import BUSINESS_RULES, CURRENT_PRICING, NEW_MODEL
from new_model.explain import why_lines
from new_model.recommend import recommend


def fixture_booking() -> dict[str, Any]:
    return dict(FIXTURE_BOOKING)


def explanation_view(
    booking: Mapping[str, Any] | None = None,
    *,
    allowed_max: float | None = None,
) -> dict[str, Any]:
    row = dict(booking or fixture_booking())
    if row.get("product_type") not in PRODUCTS:
        raise ValueError("v1 products only: extra baggage and extra-legroom")
    result = recommend(
        row,
        allowed_max=allowed_max,
        temporary_caps=caps_for_rules(),
        persist=False,
    )
    return {
        "booking": row,
        "result": result,
        "why": why_lines(row, result),
        "show_cap": (
            result["customer_price"] is not None
            and abs(result["customer_price"] - result["new_model_recommended_price"]) > 0.01
        ),
    }


def render_price_explanation() -> None:
    page_header("Price Explanation")
    view = explanation_view()
    booking = view["booking"]
    result = view["result"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Route", booking["route"].replace("-", " → "))
    c2.metric("Fare", f"{booking['cabin']} {booking['fare_type']}")
    c3.metric("Departure", f"{booking['days_to_departure']} days")
    c4.metric("Extra-legroom left", str(booking["remaining_extra_legroom"]))

    left, right = st.columns(2)
    with left:
        st.markdown(f"**{CURRENT_PRICING}**")
        st.markdown(
            f'<div class="kpi">Price {money(result["current_price"])}<br/>'
            f'Purchase chance {pct(result["p_buy_current"])}<br/>'
            f'Expected revenue {money(result["expected_revenue_current"])}</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"**{NEW_MODEL}**")
        st.markdown(
            f'<div class="kpi">Price {money(result["new_model_recommended_price"])}<br/>'
            f'Purchase chance {pct(result["p_buy_new"])}<br/>'
            f'Expected revenue {money(result["expected_revenue_new"])}</div>',
            unsafe_allow_html=True,
        )

    if view["show_cap"]:
        st.info(
            f"{BUSINESS_RULES} set the customer price to {money(result['customer_price'])} "
            f"(recommendation {money(result['new_model_recommended_price'])}). "
            f"Reasons: {', '.join(result['rule_reason_codes'])}."
        )

    st.markdown(f"**Why the {NEW_MODEL} differs**")
    for line in view["why"]:
        st.write(f"- {line}")

    st.caption(f"Fallback layer: {result['fallback_layer']}")
