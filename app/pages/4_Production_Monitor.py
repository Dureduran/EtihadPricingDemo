from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.production_monitor import (
    SECTIONS,
    monitor_report,
    pause_from_monitor,
    return_to_current_from_monitor,
)
from app.ui import page_header
from lab.copy import RETURN_TO_CURRENT, ROLLOUT_DECISION, SIMULATED_BANNER
from lab.paths import STATE_DIR
from monitor.simulate import simulate_batch

page_header("Production Monitor")

path = STATE_DIR / "simulated_offers.parquet"
if not path.exists():
    offers = simulate_batch()
else:
    offers = pd.read_parquet(path)

report = monitor_report(offers)
stats = report["stats"]


def state_html(label: str, text: str, state: str) -> str:
    return f'<div class="kpi">{label}<br/><span class="{state}">{text}</span></div>'


st.markdown(
    f'<div class="decision"><div class="decision-label">{ROLLOUT_DECISION}</div>'
    f"<h2 style='margin:0.3rem 0 0.6rem 0'>{report['decision']}</h2>"
    f"<p>{report['reason']}</p></div>",
    unsafe_allow_html=True,
)

st.markdown(f"**{SECTIONS[0]}**")
a, b = st.columns(2)
a.markdown(
    state_html("Revenue", f"{stats['revenue_impact']:+.1%}", report["commercial"]["revenue"]["state"]),
    unsafe_allow_html=True,
)
b.markdown(
    state_html(
        "Conversion",
        f"{stats['conversion_impact_pp']:+.1f} pp",
        report["commercial"]["conversion"]["state"],
    ),
    unsafe_allow_html=True,
)

st.markdown(f"**{SECTIONS[1]}**")
c, d = st.columns(2)
c.markdown(
    state_html(
        "Predictions accurate",
        report["model_health"]["predictions_accurate"]["state"].upper(),
        report["model_health"]["predictions_accurate"]["state"],
    ),
    unsafe_allow_html=True,
)
d.markdown(
    state_html(
        "Customer behaviour changed",
        report["model_health"]["customer_behaviour_changed"]["state"].upper(),
        report["model_health"]["customer_behaviour_changed"]["state"],
    ),
    unsafe_allow_html=True,
)

st.markdown(f"**{SECTIONS[2]}**")
e, f = st.columns(2)
e.markdown(
    state_html(
        "Pricing failures",
        f"{report['system_health']['pricing_failures']['value']:.1%}",
        report["system_health"]["pricing_failures"]["state"],
    ),
    unsafe_allow_html=True,
)
f.markdown(
    state_html(
        "Fallback usage",
        f"{report['system_health']['fallback_usage']['value']:.1%}",
        report["system_health"]["fallback_usage"]["state"],
    ),
    unsafe_allow_html=True,
)

st.markdown(f"**{SECTIONS[3]}**")
st.markdown(
    state_html(
        "Violations",
        str(report["business_rules"]["violations"]["value"]),
        report["business_rules"]["violations"]["state"],
    ),
    unsafe_allow_html=True,
)

st.caption(
    f"{SIMULATED_BANNER} Pause and {RETURN_TO_CURRENT} reuse Pricing Controls state. "
    "This screen does not auto-expand traffic to 100%."
)

left, right = st.columns(2)
if left.button("Pause expansion"):
    pause_from_monitor()
    st.success("Paused extra-legroom AUH–LHR.")
if right.button(RETURN_TO_CURRENT):
    return_to_current_from_monitor()
    st.success(RETURN_TO_CURRENT)
