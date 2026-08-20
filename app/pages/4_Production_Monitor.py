from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app.ui import page_header
from lab.copy import RETURN_TO_CURRENT, ROLLOUT_DECISION
from lab.paths import STATE_DIR
from monitor.health import health
from monitor.simulate import simulate_batch
from monitor.test_results import summarise
from rollout import get_config, upsert_config

page_header("Production Monitor")

path = STATE_DIR / "simulated_offers.parquet"
if not path.exists():
    offers = simulate_batch()
else:
    offers = pd.read_parquet(path)

report = health(offers)
stats = report["stats"]


def state_html(label: str, text: str, state: str) -> str:
    return f'<div class="kpi">{label}<br/><span class="{state}">{text}</span></div>'


st.markdown(
    f'<div class="decision"><div class="decision-label">{ROLLOUT_DECISION}</div>'
    f"<h2 style='margin:0.3rem 0 0.6rem 0'>{report['decision']}</h2>"
    f"<p>{report['reason']}</p></div>",
    unsafe_allow_html=True,
)

st.markdown("**Commercial performance**")
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

st.markdown("**Model health**")
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

st.markdown("**System health**")
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

st.markdown("**Business rules**")
st.markdown(
    state_html(
        "Violations",
        str(report["business_rules"]["violations"]["value"]),
        report["business_rules"]["violations"]["state"],
    ),
    unsafe_allow_html=True,
)

left, right = st.columns(2)
if left.button("Pause expansion"):
    cfg = get_config("AUH-LHR", "extra_legroom")
    cfg.status = "PAUSED"
    cfg.traffic_percent = 0
    upsert_config(cfg)
    st.success("Paused extra-legroom AUH–LHR.")
if right.button(RETURN_TO_CURRENT):
    cfg = get_config("AUH-LHR", "extra_legroom")
    cfg.status = "CURRENT_PRICING"
    cfg.shadow = False
    cfg.traffic_percent = 0
    upsert_config(cfg)
    st.success(RETURN_TO_CURRENT)
