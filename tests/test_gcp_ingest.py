import importlib.util
import json

import pandas as pd

from lab.constants import GENERATOR_ONLY, TARGET, TRAINING_FEATURES
from lab.paths import ROOT

TRAIN_COLUMNS = list(TRAINING_FEATURES) + [TARGET]


def _load_ingest():
    path = ROOT / "gcp" / "01_ingest_offer_log.py"
    spec = importlib.util.spec_from_file_location("gcp_ingest_offer_log", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_gcp_ingest_train_path_has_no_generator_columns(tmp_path, monkeypatch):
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
    monkeypatch.setattr(mod, "GCP_RUNS", tmp_path / "runs")
    monkeypatch.delenv("GCP_INGEST_BQ", raising=False)
    monkeypatch.delenv("VERTEX_PRODUCT", raising=False)
    monkeypatch.delenv("CLOUD_ML_PROJECT_ID", raising=False)
    log = mod.ingest(train_path=str(src))
    out = pd.read_parquet(tmp_path / "out_train.parquet")
    assert set(out.columns) == set(TRAIN_COLUMNS)
    assert not set(GENERATOR_ONLY).intersection(out.columns)
    assert log["n_rows"] == 1
    assert log["runtime"] == "local"
    assert log["dataset"] == "ancillary_lab"
    assert (tmp_path / "runs" / "ingest_run.json").exists()
    record = json.loads((tmp_path / "runs" / "ingest_run.json").read_text(encoding="utf-8"))
    assert record["tables"] == ["offer_log_raw", "offer_log_train"]
    assert record["generator_columns_present"] is False


def test_gcp_ingest_rejects_generator_columns(tmp_path, monkeypatch):
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
    monkeypatch.setattr(mod, "GCP_RUNS", tmp_path / "runs")
    try:
        mod.ingest(train_path=str(src))
        raise AssertionError("expected leak to fail")
    except ValueError as exc:
        assert "generator" in str(exc)


def test_gcp_readme_lists_free_tier_steps():
    text = (ROOT / "gcp" / "README_GCP.md").read_text(encoding="utf-8")
    assert "Colab" in text
    assert "Vertex AI Workbench" in text
    assert "BigQuery" in text
    assert "GCP_TRAIN_PATH" in text
    assert "ancillary_lab" in text
    assert "offer_log_raw" in text
    assert "offer_log_train" in text
    assert "YOUR_PROJECT_ID" in text


def test_gcp_notebooks_exist_and_do_not_import_generator():
    ingest_nb = (ROOT / "gcp" / "ingest_offer_log.ipynb").read_text(encoding="utf-8")
    train_nb = (ROOT / "gcp" / "train_new_model.ipynb").read_text(encoding="utf-8")
    combined = (ROOT / "gcp" / "run_ingest_and_train.ipynb").read_text(encoding="utf-8")
    assert "01_ingest_offer_log.py" in ingest_nb
    assert "02_train_new_model.py" in train_nb
    assert "ancillary_lab" in combined
    for src in (ingest_nb, train_nb, combined):
        assert "import generator" not in src
        assert "from generator" not in src


def test_committed_gcp_ingest_run_is_repo_relative():
    record = json.loads((ROOT / "gcp" / "runs" / "ingest_run.json").read_text(encoding="utf-8"))
    assert record["runtime"] in {"local", "gcp"}
    assert record["dataset"] == "ancillary_lab"
    assert "C:\\Users" not in record["train_path"]
    assert "Users/Lenovo" not in record["train_path"]


def test_gcp_train_script_matches_databricks_contract():
    text = (ROOT / "gcp" / "02_train_new_model.py").read_text(encoding="utf-8")
    assert "xgboost_monotonic_price" in text
    assert "vertex_run_id" in text
    assert "new_model/model.joblib" in text
    assert "refusing to train; generator imported" in text
