from __future__ import annotations

from typing import Mapping

import joblib
import pandas as pd

from lab.constants import TRAINING_FEATURES
from lab.paths import MODEL_PATH

_PIPE = None


def load_model():
    global _PIPE
    if _PIPE is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"New Model artifact missing: {MODEL_PATH}")
        _PIPE = joblib.load(MODEL_PATH)
    return _PIPE


def predict_buy_proba(context: Mapping) -> float:
    row = {k: context[k] for k in TRAINING_FEATURES}
    frame = pd.DataFrame([row])
    model = load_model()
    return float(model.predict_proba(frame)[0, 1])
