import importlib.util
import json
from pathlib import Path

import pandas as pd

from lab.constants import GENERATOR_ONLY, TARGET, TRAINING_FEATURES
from lab.paths import ROOT

TRAIN_COLUMNS = list(TRAINING_FEATURES) + [TARGET]


def _load_ingest():
    path = ROOT / "databricks" / "01_ingest_offer_log.py"
    spec = importlib.util.spec_from_file_location("ingest_offer_log", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ingest_train_path_has_no_generator_columns(tmp_path, monkeypatch):
    mod = _load_ingest()
    src = tmp_path / "offer_log_train.parquet"
    frame = pd.DataFrame(
        {
            "route": ["AUH-LHR"],
            "fare_type": ["Basic"],
            "loyalty": ["None"],
            "channel": ["web"],
            "cabin": ["Economy"],
            "days_to_departure": [4],
            "remaining_extra_legroom": [7],
            "party_size": [1],
            "product_type": ["extra_legroom"],
            "displayed_price": [120.0],
            "purchased": [1],
        }
    )
    frame.to_parquet(src, index=False)
    monkeypatch.setattr(mod, "TRAIN_LOG", tmp_path / "out_train.parquet")
    monkeypatch.setattr(mod, "OFFER_LOG", tmp_path / "missing_raw.parquet")
    monkeypatch.setattr(mod, "DATABRICKS_RUNS", tmp_path / "runs")
    log = mod.ingest(train_path=str(src))
    out = pd.read_parquet(tmp_path / "out_train.parquet")
    assert set(out.columns) == set(TRAIN_COLUMNS)
    assert not set(GENERATOR_ONLY).intersection(out.columns)
    assert log["n_rows"] == 1
    assert log["runtime"] == "local"
    assert (tmp_path / "runs" / "ingest_run.json").exists()


def test_ingest_rejects_generator_columns(tmp_path, monkeypatch):
    mod = _load_ingest()
    src = tmp_path / "bad.parquet"
    pd.DataFrame(
        {
            "route": ["AUH-LHR"],
            "fare_type": ["Basic"],
            "loyalty": ["None"],
            "channel": ["web"],
            "cabin": ["Economy"],
            "days_to_departure": [4],
            "remaining_extra_legroom": [7],
            "party_size": [1],
            "product_type": ["extra_legroom"],
            "displayed_price": [120.0],
            "purchased": [1],
            "latent_wtp": [200.0],
        }
    ).to_parquet(src, index=False)
    monkeypatch.setattr(mod, "TRAIN_LOG", tmp_path / "out.parquet")
    monkeypatch.setattr(mod, "DATABRICKS_RUNS", tmp_path / "runs")
    try:
        mod.ingest(train_path=str(src))
        raise AssertionError("expected leak to fail")
    except ValueError as exc:
        assert "generator" in str(exc)


def test_readme_lists_free_edition_steps():
    text = (ROOT / "databricks" / "README_DATABRICKS.md").read_text(encoding="utf-8")
    assert "Databricks Free" in text
    assert "train_path" in text
    assert "workspace.ancillary_lab" in text
    assert "offer_log_raw" in text
    assert "offer_log_train" in text


def test_committed_train_parquet_matches_training_features():
    frame = pd.read_parquet(ROOT / "data" / "offer_log_train.parquet")
    assert set(GENERATOR_ONLY).isdisjoint(frame.columns)
    assert set(TRAIN_COLUMNS) <= set(frame.columns)
