from __future__ import annotations

import pandas as pd

from monitor.test_results import summarise


def _flag(ok: bool, warn: bool = False) -> str:
    if ok and not warn:
        return "pass"
    if warn:
        return "warn"
    return "fail"


def health(offers: pd.DataFrame, fallback_rate: float | None = None) -> dict:
    stats = summarise(offers)
    n = max(len(offers), 1)
    fail_rate = float((offers.get("fallback_layer", pd.Series(["new_model"] * n)) != "new_model").mean())
    if fallback_rate is not None:
        fail_rate = fallback_rate

    drift = offers[(offers["route"] == "AUH-BOM") & (offers["days_to_departure"] <= 7)]
    drift_gap = 0.0
    if len(drift):
        predicted = drift["p_buy_new"].mean()
        realised = drift["realised_purchase"].mean() if "realised_purchase" in drift else predicted
        drift_gap = float(predicted - realised)

    behaviour_changed = drift_gap > 0.08
    calibration_ok = abs(stats["new_conversion"] - stats["live_conversion"]) < 0.12 if stats["n_new_model_live"] else True
    rev_ok = stats["revenue_impact"] > -0.02
    conv_ok = stats["conversion_impact_pp"] > -3.0
    fail_ok = fail_rate < 0.02
    fallback_ok = fail_rate < 0.03
    rules_ok = stats["business_rule_violations"] == 0

    if behaviour_changed:
        decision = "HOLD"
        reason = (
            "AUH–BOM bookings within seven days of departure are behaving differently "
            "from the training data. Keep the New Model at 20% of traffic while investigating."
        )
    elif not rev_ok or not conv_ok:
        decision = "Return to Current Pricing"
        reason = "Commercial performance is outside the agreed tolerance."
    elif stats["revenue_impact"] > 0.04 and conv_ok and not behaviour_changed:
        decision = "Expand"
        reason = "Revenue is up and conversion is within tolerance. Consider moving from 20% to 50%."
    else:
        decision = "HOLD"
        reason = "Keep the current traffic split and continue monitoring."

    return {
        "commercial": {
            "revenue": {"value": stats["revenue_impact"], "state": _flag(rev_ok)},
            "conversion": {"value": stats["conversion_impact_pp"], "state": _flag(conv_ok)},
        },
        "model_health": {
            "predictions_accurate": {"state": _flag(calibration_ok)},
            "customer_behaviour_changed": {"state": _flag(not behaviour_changed, warn=behaviour_changed)},
            "drift_gap": drift_gap,
        },
        "system_health": {
            "pricing_failures": {"value": fail_rate, "state": _flag(fail_ok)},
            "fallback_usage": {"value": fail_rate, "state": _flag(fallback_ok)},
        },
        "business_rules": {
            "violations": {"value": stats["business_rule_violations"], "state": _flag(rules_ok)},
        },
        "decision": decision,
        "reason": reason,
        "stats": stats,
    }
