from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.pricing_test_results import results_view
from app.ui import page_header
from lab.copy import CURRENT_PRICING, PRICING_TEST_RESULTS, SIMULATED_BANNER
from lab.paths import STATE_DIR
from monitor.simulate import simulate_batch

page_header(PRICING_TEST_RESULTS)

path = STATE_DIR / "simulated_offers.parquet"
if st.button("Run simulated comparison") or not path.exists():
    with st.spinner("Scoring a simulated booking batch…"):
        offers = simulate_batch()
else:
    offers = pd.read_parquet(path)

view = results_view(offers)
st.table(view["table"])

for line in view["summary_lines"]:
    st.markdown(line)

st.write(view["sentence"])
st.caption(
    f"{SIMULATED_BANNER} n={view['stats']['n']:,} simulated bookings compared with {CURRENT_PRICING}. "
    f"Live New Model arm n={view['stats']['n_new_model_live']:,}. Not a live airline A/B test."
)
