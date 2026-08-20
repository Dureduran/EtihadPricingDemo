# Databricks Free ingest
# Widgets: train_path (optional). Uses only TRAINING_FEATURES columns.

from pathlib import Path

TRAIN_COLUMNS = [
    "route",
    "fare_type",
    "loyalty",
    "channel",
    "cabin",
    "days_to_departure",
    "remaining_extra_legroom",
    "party_size",
    "product_type",
    "displayed_price",
    "purchased",
]
FORBIDDEN = {"latent_wtp", "generator_rule_id", "true_elasticity"}

def ingest(train_path: str | None = None):
    import pandas as pd

    path = train_path or str(Path("data/offer_log_train.parquet"))
    frame = pd.read_parquet(path)
    extra = FORBIDDEN.intersection(frame.columns)
    if extra:
        raise ValueError(f"generator columns leaked into train table: {extra}")
    missing = set(TRAIN_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing train columns: {missing}")
    train = frame[TRAIN_COLUMNS]
    try:
        spark  # noqa: F821 — present on Databricks
        spark.createDataFrame(train).write.mode("overwrite").saveAsTable("offer_log_train")
        print("wrote spark table offer_log_train")
    except NameError:
        out = Path("data/offer_log_train.parquet")
        train.to_parquet(out, index=False)
        print(f"local ingest OK -> {out} rows={len(train)}")
    return train


if __name__ == "__main__":
    ingest()
