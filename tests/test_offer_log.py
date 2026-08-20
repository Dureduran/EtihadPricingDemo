from pathlib import Path

import pandas as pd

from data.build_offer_log import build
from lab.constants import GENERATOR_ONLY, ROUTES, TARGET, TRAINING_FEATURES
from lab.paths import ROOT, TRAIN_LOG

ALLOWED = set(TRAINING_FEATURES + [TARGET])
REQUIRED_OFFER_COLUMNS = {
    "displayed_price",
    "purchased",
    "route",
    "fare_type",
    "loyalty",
    "channel",
    "days_to_departure",
    "remaining_extra_legroom",
    "party_size",
    "product_type",
}
TRAIN_DIRS = [
    ROOT / "new_model",
    ROOT / "databricks",
]


def _patch_builder_paths(monkeypatch, tmp_path: Path):
    data_dir = tmp_path / "data"
    gen_dir = tmp_path / "generator"
    monkeypatch.setattr("data.build_offer_log.DATA_DIR", data_dir)
    monkeypatch.setattr("data.build_offer_log.GENERATOR_DIR", gen_dir)
    monkeypatch.setattr("data.build_offer_log.OFFER_LOG", data_dir / "offer_log.parquet")
    monkeypatch.setattr("data.build_offer_log.TRAIN_LOG", data_dir / "offer_log_train.parquet")
    monkeypatch.setattr("data.build_offer_log.HIDDEN_WTP", gen_dir / "hidden_wtp.parquet")
    return data_dir, gen_dir


def test_builder_writes_offer_train_and_hidden_wtp(tmp_path, monkeypatch):
    data_dir, gen_dir = _patch_builder_paths(monkeypatch, tmp_path)
    offer, train = build(n=40, seed=7)

    hidden_path = gen_dir / "hidden_wtp.parquet"
    assert (data_dir / "offer_log.parquet").exists()
    assert (data_dir / "offer_log_train.parquet").exists()
    assert hidden_path.exists()
    assert hidden_path.parent.name == "generator"

    assert REQUIRED_OFFER_COLUMNS <= set(offer.columns)
    assert set(offer["product_type"].unique()) <= {"extra_baggage", "extra_legroom"}
    assert set(offer["route"].unique()) <= set(ROUTES)
    for route in ("AUH-LHR", "AUH-JFK", "AUH-BOM", "AUH-CDG", "AUH-SYD"):
        assert route in set(ROUTES)

    assert offer["displayed_price"].min() > 0
    assert set(offer["purchased"].unique()) <= {0, 1}

    hidden = pd.read_parquet(hidden_path)
    for col in GENERATOR_ONLY:
        assert col in hidden.columns
        assert col not in train.columns

    assert set(train.columns) <= ALLOWED
    assert TARGET in train.columns
    assert "displayed_price" in train.columns


def test_builder_is_deterministic(tmp_path, monkeypatch):
    _patch_builder_paths(monkeypatch, tmp_path)
    a, _ = build(n=15, seed=3)
    b, _ = build(n=15, seed=3)
    pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True))


def test_committed_train_log_has_no_generator_columns():
    cols = set(pd.read_parquet(TRAIN_LOG).columns)
    assert not (cols & set(GENERATOR_ONLY))
    assert cols <= ALLOWED
    offer_cols = set(pd.read_parquet(ROOT / "data" / "offer_log.parquet").columns)
    assert REQUIRED_OFFER_COLUMNS <= offer_cols
    routes = set(pd.read_parquet(ROOT / "data" / "offer_log.parquet", columns=["route"])["route"])
    assert set(ROUTES) <= routes


def test_data_card_records_row_counts_and_public_split():
    text = (ROOT / "DATA_CARD.md").read_text(encoding="utf-8")
    assert "12,000" in text or "12000" in text
    assert "kaggle_used" in text
    assert "BA-shaped" in text or "british airways" in text.lower()
