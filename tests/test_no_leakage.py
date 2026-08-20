from pathlib import Path

import pandas as pd

from lab.constants import GENERATOR_ONLY, TARGET, TRAINING_FEATURES
from lab.paths import ROOT, TRAIN_LOG

ALLOWED = set(TRAINING_FEATURES + [TARGET])
TRAIN_DIRS = [
    ROOT / "new_model",
    ROOT / "databricks",
]


def test_training_features_file_matches_constants():
    text = (ROOT / "data" / "TRAINING_FEATURES.md").read_text(encoding="utf-8")
    for col in TRAINING_FEATURES + [TARGET]:
        assert col in text


def test_train_frame_has_no_generator_columns():
    assert TRAIN_LOG.exists()
    cols = set(pd.read_parquet(TRAIN_LOG, columns=None).columns)
    assert not (cols & set(GENERATOR_ONLY))
    assert cols <= ALLOWED


def test_training_code_does_not_import_generator():
    offenders = []
    for folder in TRAIN_DIRS:
        for path in folder.rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            if "import generator" in src or "from generator" in src:
                offenders.append(str(path))
        for path in folder.rglob("*.ipynb"):
            src = path.read_text(encoding="utf-8")
            if "import generator" in src or "from generator" in src:
                offenders.append(str(path))
    assert offenders == []
