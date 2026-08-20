from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from lab.copy import DISCLAIMER, HEADLINE, SIMULATED_BANNER, SUBTITLE

NAVY = "#0B1F33"
GOLD = "#C4A35A"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {NAVY}; color: #E8EEF4; }}
        [data-testid="stSidebar"] {{ background: #081624; }}
        h1, h2, h3 {{ color: #F4F7FA !important; font-weight: 600; }}
        .banner {{
            border: 1px solid {GOLD};
            color: {GOLD};
            padding: 0.55rem 0.8rem;
            margin-bottom: 1rem;
            font-size: 0.92rem;
        }}
        .disclaimer {{
            color: #9BB0C3;
            font-size: 0.85rem;
            margin-bottom: 1.2rem;
        }}
        .decision {{
            border: 2px solid {GOLD};
            padding: 1.2rem 1.4rem;
            margin: 1rem 0 1.4rem 0;
        }}
        .decision-label {{
            letter-spacing: 0.12em;
            font-size: 0.75rem;
            color: {GOLD};
        }}
        .kpi {{
            background: #10283F;
            padding: 0.9rem 1rem;
            border: 1px solid #1E3D59;
        }}
        .pass {{ color: #7DCEA0; }}
        .warn {{ color: #F0C36A; }}
        .fail {{ color: #E07A7A; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str) -> None:
    inject_css()
    st.title(HEADLINE)
    st.caption(SUBTITLE)
    st.markdown(f'<div class="disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="banner">{SIMULATED_BANNER}</div>', unsafe_allow_html=True)
    st.subheader(title)


def money(value: float | None) -> str:
    if value is None:
        return "—"
    return f"AED {value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"
