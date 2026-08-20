from __future__ import annotations

from typing import Any

import pandas as pd

SHOULD_BE_FREE = frozenset({"included_in_fare", "loyalty_complimentary"})


def _codes(val: Any) -> list[str]:
    if val is None:
        return []
    try:
        if pd.isna(val):
            return []
    except (TypeError, ValueError):
        pass
    if isinstance(val, str):
        text = val.strip()
        if text.startswith("[") and text.endswith("]"):
            inner = text[1:-1].replace("'", "").replace('"', "")
            return [part.strip() for part in inner.split(",") if part.strip()]
        return [text] if text else []
    if isinstance(val, (list, tuple, set)):
        return [str(item) for item in val]
    if hasattr(val, "tolist"):
        return [str(item) for item in val.tolist()]
    try:
        return [str(item) for item in list(val)]
    except TypeError:
        return [str(val)]


def count_business_rule_violations(offers: pd.DataFrame) -> int:
    if offers.empty or "rule_reason_codes" not in offers.columns:
        return 0
    count = 0
    for _, row in offers.iterrows():
        codes = _codes(row.get("rule_reason_codes"))
        offered = bool(row.get("offered", False))
        try:
            price = row.get("customer_price")
            price_f = float(price) if price is not None and not pd.isna(price) else 0.0
        except (TypeError, ValueError):
            price_f = 0.0
        if offered and price_f > 0 and any(code in SHOULD_BE_FREE for code in codes):
            count += 1
    return count


def comparison_sentence(stats: dict[str, Any]) -> str:
    rev = float(stats["revenue_impact"])
    conv = float(stats["conversion_impact_pp"])
    direction = "increases" if rev >= 0 else "decreases"
    return (
        f"The model {direction} revenue by {abs(rev):.1%} in the simulation "
        f"while conversion moves {conv:+.1f} percentage points versus Current Pricing."
    )


impact_sentence = comparison_sentence


def summary_lines(stats: dict[str, Any]) -> list[str]:
    return [
        f"Revenue impact: {stats['revenue_impact']:+.1%}",
        f"Conversion impact: {stats['conversion_impact_pp']:+.1f} percentage points",
        f"Business-rule violations: {stats['business_rule_violations']}",
    ]


def summarise(offers: pd.DataFrame) -> dict:
    current_rev = float((offers["current_price"] * offers["p_buy_current"]).mean())
    current_conv = float(offers["p_buy_current"].mean())
    current_asp = float(offers["current_price"].mean())

    new_exp_rev = float((offers["customer_price"].fillna(0) * offers["p_buy_new"]).mean())
    new_exp_conv = float(offers["p_buy_new"].mean())
    priced = offers["customer_price"].dropna()
    new_asp = float(priced.mean()) if len(priced) else 0.0

    if "arm" in offers.columns:
        live = offers[offers["arm"] == "new_model"]
        n_live = int((offers["arm"] == "new_model").sum())
    else:
        live = offers.iloc[0:0]
        n_live = 0

    if len(live) and "served_price" in live.columns and "realised_purchase" in live.columns:
        live_rev = float((live["served_price"].fillna(0) * live["realised_purchase"]).mean())
        live_conv = float(live["realised_purchase"].mean())
        live_asp = float(live["served_price"].mean())
    else:
        live_rev = new_exp_rev
        live_conv = new_exp_conv
        live_asp = new_asp

    rev_impact = (new_exp_rev / current_rev - 1.0) if current_rev else 0.0
    conv_impact_pp = (new_exp_conv - current_conv) * 100

    return {
        "current_revpp": current_rev,
        "new_revpp": new_exp_rev,
        "current_conversion": current_conv,
        "new_conversion": new_exp_conv,
        "current_asp": current_asp,
        "new_asp": new_asp,
        "revenue_impact": float(rev_impact),
        "conversion_impact_pp": float(conv_impact_pp),
        "business_rule_violations": count_business_rule_violations(offers),
        "n": int(len(offers)),
        "n_new_model_live": n_live,
        "live_revpp": live_rev,
        "live_conversion": live_conv,
        "live_asp": live_asp,
    }


__all__ = [
    "SHOULD_BE_FREE",
    "comparison_sentence",
    "count_business_rule_violations",
    "impact_sentence",
    "summarise",
    "summary_lines",
]
