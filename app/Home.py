from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.ui import DISCLAIMER, HEADLINE, SIMULATED_BANNER, SUBTITLE, inject_css
from lab.copy import CURRENT_PRICING, NEW_MODEL, BUSINESS_RULES, RETURN_TO_CURRENT

st.set_page_config(page_title=HEADLINE, layout="wide")
inject_css()
st.title(HEADLINE)
st.caption(SUBTITLE)
st.markdown(f'<div class="disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="banner">{SIMULATED_BANNER}</div>', unsafe_allow_html=True)

st.markdown(
    f"""
Etihad already has an in-house ancillary dynamic-pricing capability. This lab shows how
to evaluate a **{NEW_MODEL}** against **{CURRENT_PRICING}**, keep **{BUSINESS_RULES}**
in final control, roll the model out in traffic steps, and **{RETURN_TO_CURRENT}**
if it is not healthy.

**v1 products:** extra baggage and preferred / extra-legroom seat.
Fare-brand upgrades are a future expansion.

Use the pages in this order:

1. Price Explanation  
2. Pricing Controls  
3. Pricing Test Results  
4. Production Monitor  
"""
)
