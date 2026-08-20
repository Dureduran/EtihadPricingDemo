from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd

from business_rules import TemporaryCap
from lab.paths import DATA_DIR, OFFER_LOG, STATE_DIR
from new_model.recommend import recommend
from rollout import get_config
from rollout.assignment import serve_booking


def simulate_batch(n: int = 500, seed: int = 7) -> pd.DataFrame:
    if not OFFER_LOG.exists():
        raise FileNotFoundError("Run python -m data.build_offer_log first")
    offers = pd.read_parquet(OFFER_LOG)
    sample = offers.sample(n=min(n, len(offers)), random_state=seed).reset_index(drop=True)
    rows = []
    rng = np.random.default_rng(seed)
    for rec in sample.to_dict(orient="records"):
        cfg = get_config(rec["route"], rec["product_type"])
        # Demo: extra-legroom AUH-LHR at 20% live; others mostly current/shadow via defaults.
        served = serve_booking(rec, cfg)
        # Realised purchase from served price vs a noisy WTP proxy using current/new p_buy.
        p = served["p_buy_new"] if served["arm"] == "new_model" else served["p_buy_current"]
        purchased = int(rng.random() < p)
        # Inject drift: AUH-BOM within 7 days converts less than the New Model expects.
        drift = rec["route"] == "AUH-BOM" and int(rec["days_to_departure"]) <= 7
        if drift and served["arm"] == "new_model":
            purchased = int(rng.random() < p * 0.45)
        rows.append(
            {
                **{k: rec[k] for k in rec if k != "purchased"},
                **served,
                "realised_purchase": purchased,
                "drift_segment": drift,
            }
        )
    frame = pd.DataFrame(rows)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(STATE_DIR / "simulated_offers.parquet", index=False)
    return frame


def main() -> None:
    frame = simulate_batch()
    print(f"simulated {len(frame):,} offers -> lab_state/simulated_offers.parquet")


if __name__ == "__main__":
    main()
