from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.pricing_controls import (
    DEFAULT_PRODUCT,
    DEFAULT_ROUTE,
    STATUSES,
    TRAFFIC_STEPS,
    add_temporary_cap,
    load_controls,
    pause_controls,
    return_to_current_pricing,
    save_controls,
)
from app.ui import page_header
from lab.constants import PRODUCTS, ROUTES
from lab.copy import BUSINESS_RULES, CURRENT_PRICING, NEW_MODEL, RETURN_TO_CURRENT
from rollout import load_caps

page_header("Pricing Controls")

st.caption(
    f"Revenue Management sets traffic, price bands, and temporary caps. "
    f"This is not per-passenger approval. {NEW_MODEL} never bypasses {BUSINESS_RULES}."
)

route = st.selectbox("Route", ROUTES, index=list(ROUTES).index(DEFAULT_ROUTE))
product = st.selectbox("Product", PRODUCTS, index=list(PRODUCTS).index(DEFAULT_PRODUCT))
cfg = load_controls(route, product)

status = st.selectbox(
    "Status",
    list(STATUSES),
    index=list(STATUSES).index(cfg.status) if cfg.status in STATUSES else 0,
)
shadow = st.checkbox("Shadow mode (log New Model, customer still gets Current Pricing)", value=cfg.shadow)
traffic = st.select_slider(
    f"{NEW_MODEL} allowed on % of bookings",
    options=list(TRAFFIC_STEPS),
    value=cfg.traffic_percent if cfg.traffic_percent in TRAFFIC_STEPS else 20,
)
amin, amax = st.slider(
    "Allowed price band (AED)",
    40,
    280,
    (int(cfg.allowed_min), int(cfg.allowed_max)),
)

cols = st.columns(3)
if cols[0].button("Save controls"):
    save_controls(
        cfg,
        status=status,
        traffic_percent=int(traffic),
        allowed_min=float(amin),
        allowed_max=float(amax),
        shadow=bool(shadow),
    )
    st.success("Saved.")

if cols[1].button("Pause"):
    pause_controls(route, product)
    st.success(f"Paused. Customers receive {CURRENT_PRICING}.")

if cols[2].button(RETURN_TO_CURRENT):
    return_to_current_pricing(route, product)
    st.success(f"{RETURN_TO_CURRENT}.")

st.markdown("---")
st.markdown(f"**Temporary {CURRENT_PRICING} override / cap**")
st.caption("Example: maximum price AED 130 for AUH–LHR until a chosen date.")
cap_price = st.number_input("Maximum price (AED)", min_value=40, max_value=280, value=130)
cap_days = st.number_input("Days in force", min_value=1, max_value=90, value=11)
if st.button("Add temporary cap"):
    until = date.today() + timedelta(days=int(cap_days))
    add_temporary_cap(route, product, float(cap_price), until)
    st.success(f"Cap AED {cap_price:.0f} on {route} {product} until {until.isoformat()}.")

st.markdown("**Active caps**")
active = load_caps()
if not active:
    st.write("None.")
else:
    st.table([c.__dict__ for c in active])
