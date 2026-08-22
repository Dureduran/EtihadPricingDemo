# Vertex AI Workbench / Colab ingest
# Env: GCP_TRAIN_PATH, GCP_PROJECT (optional). Creates BigQuery
# ancillary_lab.offer_log_raw and ancillary_lab.offer_log_train
# using only TRAINING_FEATURES + purchased. Never reads generator/.

from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lab.constants import GENERATOR_ONLY, TARGET, TRAINING_FEATURES
from lab.paths import GCP_RUNS, OFFER_LOG, TRAIN_LOG

DATASET = os.environ.get("GCP_BQ_DATASET", "ancillary_lab")
TABLE_RAW = f"{DATASET}.offer_log_raw"
TABLE_TRAIN = f"{DATASET}.offer_log_train"
TRAIN_COLUMNS = list(TRAINING_FEATURES) + [TARGET]


def _on_gcp_runtime() -> bool:
    if os.environ.get("GCP_INGEST_BQ") == "1":
        return True
    if os.environ.get("VERTEX_PRODUCT"):
        return True
    if os.environ.get("CLOUD_ML_PROJECT_ID"):
        return True
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def _project(explicit: str | None = None) -> str | None:
    return (
        explicit
        or os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("CLOUD_ML_PROJECT_ID")
        or os.environ.get("DEVSHELL_PROJECT_ID")
    )


def _record_path(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(_ROOT).as_posix()
    except ValueError:
        return path


def _train_path(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("GCP_TRAIN_PATH")
    if env:
        return env
    return str(TRAIN_LOG)


def _read_parquet(path: str):
    import pandas as pd

    if path.startswith("gs://"):
        from google.cloud import storage

        rest = path[5:]
        bucket_name, _, blob_name = rest.partition("/")
        payload = storage.Client().bucket(bucket_name).blob(blob_name).download_as_bytes()
        return pd.read_parquet(io.BytesIO(payload))
    return pd.read_parquet(path)


def _write_bigquery(raw, train, project: str) -> None:
    from google.cloud import bigquery

    location = os.environ.get("GCP_BQ_LOCATION", "US")
    client = bigquery.Client(project=project)
    dataset_id = f"{project}.{DATASET}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(raw, f"{dataset_id}.offer_log_raw", job_config=job_config).result()
    client.load_table_from_dataframe(train, f"{dataset_id}.offer_log_train", job_config=job_config).result()
    print(f"wrote BigQuery tables {TABLE_RAW}, {TABLE_TRAIN} in {dataset_id}")


def ingest(
    train_path: str | None = None,
    raw_path: str | None = None,
    project: str | None = None,
) -> dict:
    path = _train_path(train_path)
    frame = _read_parquet(path)
    extra = set(GENERATOR_ONLY).intersection(frame.columns)
    if extra:
        raise ValueError(f"generator columns leaked into train table: {extra}")
    missing = set(TRAIN_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing train columns: {missing}")
    train = frame[TRAIN_COLUMNS].copy()

    raw_source = raw_path or os.environ.get("GCP_RAW_PATH") or str(OFFER_LOG)
    raw_file = Path(raw_source)
    if str(raw_source).startswith("gs://"):
        raw = _read_parquet(str(raw_source))
    elif raw_file.exists():
        raw = _read_parquet(str(raw_file))
    else:
        raw = train.copy()

    runtime = "local"
    project_id = _project(project)
    if _on_gcp_runtime() and project_id:
        try:
            _write_bigquery(raw, train, project_id)
            runtime = "gcp"
        except Exception as exc:  # noqa: BLE001 — sandbox projects vary
            print("bigquery optional:", exc)
            TRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
            train.to_parquet(TRAIN_LOG, index=False)
            print(f"local ingest OK after BigQuery miss -> {TRAIN_LOG} rows={len(train)}")
    else:
        TRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
        train.to_parquet(TRAIN_LOG, index=False)
        print(f"local ingest OK -> {TRAIN_LOG} rows={len(train)}")

    GCP_RUNS.mkdir(parents=True, exist_ok=True)
    log = {
        "script": "gcp/01_ingest_offer_log.py",
        "runtime": runtime,
        "project": project_id,
        "dataset": DATASET,
        "tables": ["offer_log_raw", "offer_log_train"],
        "train_path": _record_path(path),
        "n_rows": int(len(train)),
        "train_columns": list(train.columns),
        "generator_columns_present": False,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    (GCP_RUNS / "ingest_run.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("RUN_RECORD::" + json.dumps(log))
    return log


if __name__ == "__main__":
    ingest()
