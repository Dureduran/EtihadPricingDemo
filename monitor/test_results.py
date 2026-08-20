from __future__ import annotations

import pandas as pd


def summarise(offers: pd.DataFrame) -> dict:
    current = offers.copy()
    # Counterfactual Current Pricing outcomes: use p_buy_current as expected purchase.
    current_rev = (current["current_price"] * current["p_buy_current"]).mean()
    current_conv = current["p_buy_current"].mean()
    current_asp = current["current_price"].mean()

    new = offers.copy()
    new_rev = (new["new_model_recommended_price"].clip(lower=0) * new["p_buy_at_recommendation"]).mean()
    # Live arm metrics where New Model actually served
    live = offers[offers["arm"] == "new_model"]
    if len(live):
        live_rev = (live["served_price"].fillna(0) * live["realised_purchase"]).mean()
        live_conv = live["realised_purchase"].mean()
        live_asp = live["served_price"].mean()
    else:
        live_rev = new_rev
        live_conv = float(new["p_buy_new"].mean())
        live_asp = float(new["customer_price"].dropna().mean()) if new["customer_price"].notna().any() else 0.0

    # Expected New Model vs Current on the full sample (fair comparison)
    new_exp_rev = (offers["customer_price"].fillna(0) * offers["p_buy_new"]).mean()
    new_exp_conv = offers["p_buy_new"].mean()
    new_asp = offers["customer_price"].dropna().mean() if offers["customer_price"].notna().any() else 0.0

    violations = 0
    if "rule_reason_codes" in offers.columns:
        def _bad(val) -> bool:
            if isinstance(val, list):
                return False
            return False

        violations = int(offers["offered"].eq(True).sum() and 0)
    # Count explicit inventory/inclusion mistakes: offered included products with positive price
    if "rule_reason_codes" in offers.columns:
        violations = int(
            offers.apply(
                lambda r: bool(r.get("offered") and r.get("customer_price") and r.get("customer_price") > 0 and "included_in_fare" in (r.get("rule_reason_codes") or [])),
                axis=1,
            ).sum()
        )

    rev_impact = (new_exp_rev / current_rev - 1.0) if current_rev else 0.0
    conv_impact_pp = (new_exp_conv - current_conv) * 100

    return {
        "current_revpp": float(current_rev),
        "new_revpp": float(new_exp_rev),
        "current_conversion": float(current_conv),
        "new_conversion": float(new_exp_conv),
        "current_asp": float(current_asp),
        "new_asp": float(new_asp),
        "revenue_impact": float(rev_impact),
        "conversion_impact_pp": float(conv_impact_pp),
        "business_rule_violations": int(violations),
        "n": int(len(offers)),
        "n_new_model_live": int((offers["arm"] == "new_model").sum()),
        "live_revpp": float(live_rev),
        "live_conversion": float(live_conv),
        "live_asp": float(live_asp),
    }
