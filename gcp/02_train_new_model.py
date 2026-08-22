# Vertex AI Workbench / Colab — train New Model P(buy).
# Gradient-boosted XGBoost with a decreasing constraint on displayed_price.
# Must not load the hidden WTP package. Exports new_model/model.joblib for the lab.
# Future A/B only (not this model): a Deepair-style DNN challenger.

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.paths import GCP_RUNS
from new_model.train import train


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


if __name__ == "__main__":
    banned = [n for n in sys.modules if n == "generator" or n.startswith("generator.")]
    if banned:
        raise SystemExit(f"refusing to train; generator imported: {banned}")
    metrics = train()
    print(json.dumps(metrics, indent=2))
    vertex_run_id = None
    runtime = "gcp" if _on_gcp_runtime() else "local"
    try:
        from google.cloud import aiplatform

        project = (
            os.environ.get("GCP_PROJECT")
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("CLOUD_ML_PROJECT_ID")
        )
        location = os.environ.get("GCP_LOCATION", "us-central1")
        experiment = "ancillary-new-model"
        if project and _on_gcp_runtime():
            aiplatform.init(project=project, location=location, experiment=experiment)
            aiplatform.start_run("new-model-pbuy")
            aiplatform.log_params({"model": "xgboost_monotonic_price"})
            aiplatform.log_metrics({k: v for k, v in metrics.items() if isinstance(v, (int, float))})
            aiplatform.end_run()
            vertex_run_id = f"{experiment}/new-model-pbuy"
            print("vertex experiment", experiment)
            print("vertex run", vertex_run_id)
            runtime = "gcp"
    except Exception as exc:  # noqa: BLE001
        print("vertex experiments optional:", exc)
        if not _on_gcp_runtime():
            runtime = "local"

    GCP_RUNS.mkdir(parents=True, exist_ok=True)
    record = {
        "script": "gcp/02_train_new_model.py",
        "runtime": runtime,
        "model": "xgboost_monotonic_price",
        "vertex_run_id": vertex_run_id,
        "metrics": metrics,
        "artifact": "new_model/model.joblib",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    (GCP_RUNS / "train_run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("RUN_RECORD::" + json.dumps(record))
