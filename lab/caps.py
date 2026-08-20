from __future__ import annotations

from datetime import date

from business_rules import TemporaryCap
from rollout import active_caps


def caps_for_rules() -> list[TemporaryCap]:
    out = []
    for rec in active_caps():
        out.append(
            TemporaryCap(
                route=rec.route,
                product_type=rec.product_type,
                max_price=float(rec.max_price),
                until=date.fromisoformat(rec.until),
            )
        )
    return out
