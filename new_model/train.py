from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from lab.constants import TARGET, TRAINING_FEATURES
from lab.paths import DATABRICKS_RUNS, ENCODER_PATH, MODEL_DIR, MODEL_PATH, TRAIN_LOG

CAT = ["route", "fare_type", "loyalty", "channel", "cabin", "product_type"]
NUM = ["days_to_departure", "remaining_extra_legroom", "party_size", "displayed_price"]


def _assert_no_generator_import() -> None:
    import sys

    banned = [n for n in sys.modules if n == "generator" or n.startswith("generator.")]
    if banned:
        raise RuntimeError(f"training imported generator modules: {banned}")


def load_train_frame(path: Path | None = None) -> pd.DataFrame:
    frame = pd.read_parquet(path or TRAIN_LOG)
    allowed = set(TRAINING_FEATURES + [TARGET])
    extra = set(frame.columns) - allowed
    if extra:
        raise ValueError(f"train frame has forbidden columns: {extra}")
    return frame


def build_pipeline() -> Pipeline:
    # displayed_price is last numeric feature; monotone -1 = higher price, lower P(buy)
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
            ("num", "passthrough", NUM),
        ]
    )
    # After one-hot, numeric block is at the end; last column is displayed_price.
    clf = XGBClassifier(
        n_estimators=180,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=6,
        reg_lambda=1.5,
        objective="binary:logistic",
        eval_metric="logloss",
        n_jobs=4,
        random_state=42,
        monotone_constraints=None,  # set after knowing OHE width
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def _monotone_tuple(pipeline: Pipeline, x_sample: pd.DataFrame) -> tuple[int, ...]:
    pre: ColumnTransformer = pipeline.named_steps["pre"]
    pre.fit(x_sample)
    n_out = pre.transform(x_sample.iloc[:2]).shape[1]
    constraints = [0] * n_out
    constraints[-1] = -1  # displayed_price
    return tuple(constraints)


def train(path: Path | None = None) -> dict:
    _assert_no_generator_import()
    df = load_train_frame(path)
    x = df[TRAINING_FEATURES]
    y = df[TARGET].astype(int)
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    pipe = build_pipeline()
    mono = _monotone_tuple(pipe, x_tr)
    pipe.named_steps["clf"].set_params(monotone_constraints="(" + ",".join(map(str, mono)) + ")")
    pipe.fit(x_tr, y_tr)

    p = pipe.predict_proba(x_te)[:, 1]
    metrics = {
        "auc": float(roc_auc_score(y_te, p)),
        "log_loss": float(log_loss(y_te, p)),
        "n_train": int(len(x_tr)),
        "n_test": int(len(x_te)),
        "positive_rate": float(y.mean()),
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATABRICKS_RUNS.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    joblib.dump({"features": TRAINING_FEATURES, "cat": CAT, "num": NUM}, ENCODER_PATH)
    (DATABRICKS_RUNS / "local_train_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    _assert_no_generator_import()
    return metrics


def main() -> None:
    metrics = train()
    print(json.dumps(metrics, indent=2))
    print(f"saved {MODEL_PATH}")


if __name__ == "__main__":
    main()
