from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.ui import money, page_header, pct
from lab.copy import CURRENT_PRICING, NEW_MODEL
from lab.paths import STATE_DIR
from monitor.simulate import simulate_batch
from monitor.test_results import summarise

page_header("Pricing Test Results")

path = STATE_DIR / "simulated_offers.parquet"
if st.button("Run simulated comparison") or not path.exists():
    with st.spinner("Scoring a simulated booking batch…"):
        offers = simulate_batch()
else:
    offers = pd.read_parquet(path)

stats = summarise(offers)

table = pd.DataFrame(
    {
        CURRENT_PRICING: [
            money(stats["current_revpp"]),
            pct(stats["current_conversion"]),
            money(stats["current_asp"]),
        ],
        NEW_MODEL: [
            money(stats["new_revpp"]),
            pct(stats["new_conversion"]),
            money(stats["new_asp"]),
        ],
    },
    index=["Revenue per passenger", "Purchase rate", "Average selling price"],
)
st.table(table)

st.markdown(f"**Revenue impact:** {stats['revenue_impact']:+.1%}")
st.markdown(f"**Conversion impact:** {stats['conversion_impact_pp']:+.1f} percentage points")
st.markdown(f"**Business-rule violations:** {stats['business_rule_violations']}")

st.write(
    f'The model changes expected revenue by {stats["revenue_impact"]:+.1%} in the simulation '
    f"while conversion moves {stats['conversion_impact_pp']:+.1f} percentage points "
    "relative to Current Pricing."
)
st.caption(f"n={stats['n']:,} simulated bookings. Live New Model arm n={stats['n_new_model_live']:,}.")
