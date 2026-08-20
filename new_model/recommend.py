from __future__ import annotations

from typing import Any, Mapping

from lab.caps import caps_for_rules
from business_rules import TemporaryCap, apply_business_rules
from current_pricing import current_price
from fallback import run_fallback
from lab.constants import PRICE_GRIDS
from lab.paths import OFFERS_LOG, STATE_DIR
from new_model.score import predict_buy_proba
import pandas as pd
from pathlib import Path


def _context_with_price(booking: Mapping[str, Any], price: float) -> dict[str, Any]:
    row = dict(booking)
    row["displayed_price"] = float(price)
    return row


def expected_revenue(price: float, p_buy: float) -> float:
    return float(price) * float(p_buy)


def new_model_recommended_price(
    booking: Mapping[str, Any],
    allowed_min: float | None = None,
    allowed_max: float | None = None,
) -> tuple[float, float]:
    product = booking["product_type"]
    grid = list(PRICE_GRIDS[product])
    if allowed_min is not None:
        grid = [p for p in grid if p >= allowed_min]
    if allowed_max is not None:
        grid = [p for p in grid if p <= allowed_max]
    if not grid:
        grid = list(PRICE_GRIDS[product])

    best_price = grid[0]
    best_rev = -1.0
    best_p = 0.0
    for price in grid:
        p = predict_buy_proba(_context_with_price(booking, price))
        rev = expected_revenue(price, p)
        if rev > best_rev:
            best_rev = rev
            best_price = float(price)
            best_p = p
    return best_price, best_p


def recommend(
    booking: Mapping[str, Any],
    *,
    allowed_min: float | None = None,
    allowed_max: float | None = None,
    temporary_caps: list[TemporaryCap] | None = None,
    force_new_model_error: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    if temporary_caps is None:
        temporary_caps = caps_for_rules()
    product = booking["product_type"]
    current = current_price(
        route=booking["route"],
        days_to_departure=int(booking["days_to_departure"]),
        product_type=product,
        channel=booking["channel"],
        remaining_extra_legroom=int(booking["remaining_extra_legroom"]),
    )
    p_current = predict_buy_proba(_context_with_price(booking, current))

    def _new_model_raw() -> float:
        if force_new_model_error:
            raise RuntimeError("new_model_unavailable")
        rec, _ = new_model_recommended_price(booking, allowed_min, allowed_max)
        return rec

    fb = run_fallback(
        product_type=product,
        route=booking["route"],
        days_to_departure=int(booking["days_to_departure"]),
        channel=booking["channel"],
        remaining_extra_legroom=int(booking["remaining_extra_legroom"]),
        new_model_fn=_new_model_raw,
    )

    recommended = float(fb.customer_price) if fb.customer_price is not None else current
    if fb.fallback_layer == "new_model":
        recommended, p_new_at_rec = new_model_recommended_price(
            booking, allowed_min, allowed_max
        )
    else:
        p_new_at_rec = predict_buy_proba(_context_with_price(booking, recommended))

    rules = apply_business_rules(
        recommended_price=recommended,
        product_type=product,
        fare_type=booking["fare_type"],
        loyalty=booking["loyalty"],
        cabin=booking["cabin"],
        channel=booking["channel"],
        remaining_extra_legroom=int(booking["remaining_extra_legroom"]),
        allowed_min=allowed_min,
        allowed_max=allowed_max,
        temporary_caps=temporary_caps,
        route=booking["route"],
    )

    customer = rules.customer_price
    p_new = (
        predict_buy_proba(_context_with_price(booking, customer))
        if customer and customer > 0
        else 0.0
    )

    out = {
        "current_price": float(current),
        "new_model_recommended_price": float(recommended),
        "customer_price": None if customer is None else float(customer),
        "offered": rules.offered,
        "p_buy_current": float(p_current),
        "p_buy_new": float(p_new),
        "expected_revenue_current": expected_revenue(current, p_current),
        "expected_revenue_new": expected_revenue(customer or 0.0, p_new),
        "rule_reason_codes": rules.reason_codes,
        "fallback_layer": fb.fallback_layer,
        "fallback_error": fb.error,
        "p_buy_at_recommendation": float(p_new_at_rec),
    }
    if persist:
        _append_offer(booking, out)
    return out


def _append_offer(booking: Mapping[str, Any], result: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    row = {**{k: booking.get(k) for k in ("booking_id", "route", "product_type")}, **result}
    frame = pd.DataFrame([row])
    if OFFERS_LOG.exists():
        prev = pd.read_parquet(OFFERS_LOG)
        frame = pd.concat([prev, frame], ignore_index=True)
    frame.to_parquet(OFFERS_LOG, index=False)
