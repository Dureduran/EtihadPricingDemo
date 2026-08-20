"""Build a synthetic offer log from a BA-shaped seed. Hidden WTP is written separately."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from current_pricing import current_price
from lab.constants import (
    CABINS,
    CHANNELS,
    FARE_TYPES,
    GENERATOR_ONLY,
    LOYALTY,
    PRODUCTS,
    ROUTES,
    TARGET,
    TRAINING_FEATURES,
)
from lab.paths import DATA_DIR, GENERATOR_DIR, HIDDEN_WTP, OFFER_LOG, TRAIN_LOG

N_ROWS = 12_000
SEED = 42

BA_COLUMNS = (
    "num_passengers",
    "sales_channel",
    "trip_type",
    "purchase_lead",
    "length_of_stay",
    "flight_hour",
    "flight_day",
    "route",
    "booking_origin",
    "wants_extra_baggage",
    "wants_preferred_seat",
    "wants_in_flight_meals",
    "flight_duration",
    "booking_complete",
)


def _ba_shaped_seed(rng: np.random.Generator, n: int) -> pd.DataFrame:
    """BA-shaped public seed. Real Kaggle file is optional; schema matches the public set."""
    kaggle = DATA_DIR / "raw_kaggle" / "customer_booking.csv"
    if kaggle.exists():
        raw = pd.read_csv(kaggle)
        return raw.sample(n=min(n, len(raw)), random_state=SEED).reset_index(drop=True)

    sales = rng.choice(["Internet", "Mobile"], size=n, p=[0.7, 0.3])
    return pd.DataFrame(
        {
            "num_passengers": rng.integers(1, 5, size=n),
            "sales_channel": sales,
            "trip_type": rng.choice(["RoundTrip", "OneWay"], size=n, p=[0.75, 0.25]),
            "purchase_lead": rng.integers(1, 365, size=n),
            "length_of_stay": rng.integers(1, 21, size=n),
            "flight_hour": rng.integers(0, 23, size=n),
            "flight_day": rng.choice(list("MTWTFSS"), size=n),
            "route": rng.choice(["LTNPRG", "JFKDXB", "LHRBOM", "CDGSYD", "AUHBOM"], size=n),
            "booking_origin": rng.choice(["United Kingdom", "UAE", "India", "USA", "France"], size=n),
            "wants_extra_baggage": rng.integers(0, 2, size=n),
            "wants_preferred_seat": rng.integers(0, 2, size=n),
            "wants_in_flight_meals": rng.integers(0, 2, size=n),
            "flight_duration": rng.uniform(2.0, 15.0, size=n).round(2),
            "booking_complete": rng.integers(0, 2, size=n),
        }
    )


def build(n: int = N_ROWS, seed: int = SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Import generator only inside the builder — never from new_model.
    from generator.wtp import latent_wtp

    rng = np.random.default_rng(seed)
    seed_df = _ba_shaped_seed(rng, n)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GENERATOR_DIR.mkdir(parents=True, exist_ok=True)
    seed_df.to_csv(DATA_DIR / "ba_shaped_seed.csv", index=False)

    rows = []
    hidden = []
    for i in range(n):
        src = seed_df.iloc[i % len(seed_df)]
        route = str(rng.choice(ROUTES))
        product = str(rng.choice(PRODUCTS, p=[0.55, 0.45]))
        channel = "airport" if src["sales_channel"] == "Mobile" and rng.random() < 0.25 else str(
            rng.choice(["web", "app", "airport"], p=[0.62, 0.25, 0.13])
        )
        fare = str(rng.choice(FARE_TYPES, p=[0.28, 0.32, 0.25, 0.15]))
        loyalty = str(rng.choice(LOYALTY, p=[0.55, 0.22, 0.15, 0.08]))
        cabin = str(rng.choice(CABINS, p=[0.86, 0.14]))
        dtd = int(np.clip(int(src["purchase_lead"]) % 90, 1, 89))
        remaining = int(rng.integers(0, 22))
        party = int(np.clip(int(src["num_passengers"]), 1, 6))

        displayed = current_price(
            route=route,
            days_to_departure=dtd,
            product_type=product,
            channel=channel,
            remaining_extra_legroom=remaining,
        )
        # Current Pricing jitter so the New Model sees a range of offered prices.
        displayed = float(max(40, displayed + int(rng.integers(-20, 25))))
        displayed = float(round(displayed / 5) * 5)

        wtp, rule_id, elast = latent_wtp(
            rng=rng,
            route=route,
            days_to_departure=dtd,
            product_type=product,
            channel=channel,
            remaining_extra_legroom=remaining,
            loyalty=loyalty,
            cabin=cabin,
            party_size=party,
        )
        purchased = int(wtp >= displayed)

        booking_id = f"B{i:06d}"
        rows.append(
            {
                "booking_id": booking_id,
                "route": route,
                "fare_type": fare,
                "loyalty": loyalty,
                "channel": channel,
                "cabin": cabin,
                "days_to_departure": dtd,
                "remaining_extra_legroom": remaining,
                "party_size": party,
                "product_type": product,
                "displayed_price": displayed,
                "purchased": purchased,
            }
        )
        hidden.append(
            {
                "booking_id": booking_id,
                "latent_wtp": wtp,
                "generator_rule_id": rule_id,
                "true_elasticity": elast,
            }
        )

    offer = pd.DataFrame(rows)
    hid = pd.DataFrame(hidden)
    train = offer[TRAINING_FEATURES + [TARGET]].copy()
    assert not any(c in train.columns for c in GENERATOR_ONLY)

    offer.to_parquet(OFFER_LOG, index=False)
    train.to_parquet(TRAIN_LOG, index=False)
    hid.to_parquet(HIDDEN_WTP, index=False)

    meta = {
        "n_rows": n,
        "kaggle_used": (DATA_DIR / "raw_kaggle" / "customer_booking.csv").exists(),
        "train_columns": list(train.columns),
        "hidden_path": str(HIDDEN_WTP),
        "seed": seed,
    }
    (DATA_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return offer, train


def main() -> None:
    offer, train = build()
    print(f"offer_log: {len(offer):,} rows -> {OFFER_LOG}")
    print(f"train_log: {len(train):,} rows, columns={list(train.columns)}")
    print(f"hidden WTP: {HIDDEN_WTP} (not for training)")


if __name__ == "__main__":
    main()
