from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui import money, page_header, pct
from lab.caps import caps_for_rules
from lab.constants import FIXTURE_BOOKING
from lab.copy import BUSINESS_RULES, CURRENT_PRICING, NEW_MODEL
from new_model.explain import why_lines
from new_model.recommend import recommend

page_header("Price Explanation")

booking = dict(FIXTURE_BOOKING)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Route", booking["route"].replace("-", " → "))
c2.metric("Fare", f"{booking['cabin']} {booking['fare_type']}")
c3.metric("Departure", f"{booking['days_to_departure']} days")
c4.metric("Extra-legroom left", str(booking["remaining_extra_legroom"]))

try:
    result = recommend(booking, temporary_caps=caps_for_rules())
except FileNotFoundError:
    st.error("Train the New Model first: `python -m data.build_offer_log` then `python -m new_model.train`.")
    st.stop()

left, right = st.columns(2)
with left:
    st.markdown(f"**{CURRENT_PRICING}**")
    st.markdown(f'<div class="kpi">Price {money(result["current_price"])}<br/>Purchase chance {pct(result["p_buy_current"])}<br/>Expected revenue {money(result["expected_revenue_current"])}</div>', unsafe_allow_html=True)
with right:
    st.markdown(f"**{NEW_MODEL}**")
    st.markdown(f'<div class="kpi">Price {money(result["new_model_recommended_price"])}<br/>Purchase chance {pct(result["p_buy_new"])}<br/>Expected revenue {money(result["expected_revenue_new"])}</div>', unsafe_allow_html=True)

if result["customer_price"] is not None and abs(result["customer_price"] - result["new_model_recommended_price"]) > 0.01:
    st.info(
        f"{BUSINESS_RULES} set the customer price to {money(result['customer_price'])} "
        f"(recommendation {money(result['new_model_recommended_price'])}). "
        f"Reasons: {', '.join(result['rule_reason_codes'])}."
    )

st.markdown("**Why the New Model differs**")
for line in why_lines(booking, result):
    st.write(f"- {line}")

st.caption(f"Fallback layer: {result['fallback_layer']}")
