from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui import page_header
from lab.constants import PRODUCTS, ROUTES
from lab.copy import CURRENT_PRICING, NEW_MODEL, RETURN_TO_CURRENT
from rollout import (
    TemporaryCapRecord,
    get_config,
    load_caps,
    save_caps,
    upsert_config,
)

page_header("Pricing Controls")

st.caption(
    f"Revenue Management sets traffic, price bands, and temporary caps. "
    f"This is not per-passenger approval. {NEW_MODEL} never bypasses Business Rules."
)

route = st.selectbox("Route", ROUTES, index=list(ROUTES).index("AUH-LHR"))
product = st.selectbox("Product", PRODUCTS, index=1)
cfg = get_config(route, product)

status = st.selectbox(
    "Status",
    ["TESTING", "PAUSED", "CURRENT_PRICING"],
    index=["TESTING", "PAUSED", "CURRENT_PRICING"].index(cfg.status),
)
shadow = st.checkbox("Shadow mode (log New Model, customer still gets Current Pricing)", value=cfg.shadow)
traffic = st.select_slider(
    f"{NEW_MODEL} traffic %",
    options=[0, 5, 20, 50, 100],
    value=cfg.traffic_percent if cfg.traffic_percent in {0, 5, 20, 50, 100} else 20,
)
amin, amax = st.slider("Allowed price (AED)", 40, 280, (int(cfg.allowed_min), int(cfg.allowed_max)))

cols = st.columns(3)
if cols[0].button("Save controls"):
    cfg.status = status
    cfg.shadow = bool(shadow)
    cfg.traffic_percent = 0 if status != "TESTING" else int(traffic)
    cfg.allowed_min = float(amin)
    cfg.allowed_max = float(amax)
    upsert_config(cfg)
    st.success("Saved.")

if cols[1].button("Pause"):
    cfg.status = "PAUSED"
    cfg.traffic_percent = 0
    upsert_config(cfg)
    st.success("Paused. Customers receive Current Pricing.")

if cols[2].button(RETURN_TO_CURRENT):
    cfg.status = "CURRENT_PRICING"
    cfg.shadow = False
    cfg.traffic_percent = 0
    upsert_config(cfg)
    st.success(f"{RETURN_TO_CURRENT}.")

st.markdown("---")
st.markdown(f"**Temporary {CURRENT_PRICING} override / cap**")
st.caption("Example: maximum price AED 130 for AUH–LHR until a chosen date.")
cap_price = st.number_input("Maximum price (AED)", min_value=40, max_value=280, value=130)
cap_days = st.number_input("Days in force", min_value=1, max_value=90, value=11)
if st.button("Add temporary cap"):
    until = date.today() + timedelta(days=int(cap_days))
    caps = load_caps()
    caps.append(
        TemporaryCapRecord(
            route=route,
            product_type=product,
            max_price=float(cap_price),
            until=until.isoformat(),
        )
    )
    save_caps(caps)
    st.success(f"Cap AED {cap_price:.0f} on {route} {product} until {until.isoformat()}.")

st.markdown("**Active caps**")
active = load_caps()
if not active:
    st.write("None.")
else:
    st.table([c.__dict__ for c in active])
