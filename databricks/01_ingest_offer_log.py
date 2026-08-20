# Databricks Free ingest
# Widget: train_path (optional). Creates offer_log_raw and offer_log_train
# using only TRAINING_FEATURES + purchased. Never reads generator/.

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lab.constants import GENERATOR_ONLY, TARGET, TRAINING_FEATURES
from lab.paths import DATABRICKS_RUNS, OFFER_LOG, TRAIN_LOG

CATALOG_SCHEMA = "workspace.ancillary_lab"
TABLE_RAW = f"{CATALOG_SCHEMA}.offer_log_raw"
TABLE_TRAIN = f"{CATALOG_SCHEMA}.offer_log_train"
TRAIN_COLUMNS = list(TRAINING_FEATURES) + [TARGET]


def _widget_train_path(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    try:
        dbutils.widgets.text("train_path", "")  # noqa: F821
        value = dbutils.widgets.get("train_path")  # noqa: F821
        return value or None
    except NameError:
        return None


def ingest(train_path: str | None = None, raw_path: str | None = None) -> dict:
    import pandas as pd

    path = _widget_train_path(train_path) or str(TRAIN_LOG)
    frame = pd.read_parquet(path)
    extra = set(GENERATOR_ONLY).intersection(frame.columns)
    if extra:
        raise ValueError(f"generator columns leaked into train table: {extra}")
    missing = set(TRAIN_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing train columns: {missing}")
    train = frame[TRAIN_COLUMNS].copy()

    raw_source = Path(raw_path) if raw_path else OFFER_LOG
    if raw_source.exists():
        raw = pd.read_parquet(raw_source)
    else:
        raw = train.copy()

    runtime = "local"
    try:
        spark  # noqa: F821 — present on Databricks
        try:
            spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_SCHEMA}")  # noqa: F821
        except Exception:  # noqa: BLE001 — workspace catalogs vary on Free
            pass
        spark.createDataFrame(raw).write.mode("overwrite").saveAsTable("offer_log_raw")  # noqa: F821
        spark.createDataFrame(train).write.mode("overwrite").saveAsTable("offer_log_train")  # noqa: F821
        print(f"wrote spark tables offer_log_raw, offer_log_train ({TABLE_TRAIN})")
        runtime = "databricks"
    except NameError:
        TRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
        train.to_parquet(TRAIN_LOG, index=False)
        print(f"local ingest OK -> {TRAIN_LOG} rows={len(train)}")

    DATABRICKS_RUNS.mkdir(parents=True, exist_ok=True)
    log = {
        "script": "databricks/01_ingest_offer_log.py",
        "runtime": runtime,
        "catalog_schema": CATALOG_SCHEMA,
        "tables": ["offer_log_raw", "offer_log_train"],
        "train_path": path,
        "n_rows": int(len(train)),
        "train_columns": list(train.columns),
        "generator_columns_present": False,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    (DATABRICKS_RUNS / "ingest_run.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log


if __name__ == "__main__":
    ingest()
