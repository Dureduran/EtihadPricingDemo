# Databricks Free — train New Model P(buy).
# Gradient-boosted XGBoost with a decreasing constraint on displayed_price.
# Must not load the hidden WTP package. Exports new_model/model.joblib for the lab.
# Future A/B only (not this model): a Deepair-style DNN challenger.

from pathlib import Path
import json
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.paths import DATABRICKS_RUNS
from new_model.train import train


if __name__ == "__main__":
    banned = [n for n in sys.modules if n == "generator" or n.startswith("generator.")]
    if banned:
        raise SystemExit(f"refusing to train; generator imported: {banned}")
    metrics = train()
    print(json.dumps(metrics, indent=2))
    mlflow_run_id = None
    has_spark = "spark" in dir()
    runtime = "databricks" if has_spark else "local"
    try:
        import mlflow

        experiment = "ancillary-new-model"
        try:
            user = spark.sql("SELECT current_user()").collect()[0][0]  # noqa: F821
            if user:
                experiment = f"/Users/{user}/ancillary-new-model"
        except Exception:
            pass
        mlflow.set_experiment(experiment)
        with mlflow.start_run(run_name="new-model-pbuy") as run:
            mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, (int, float))})
            mlflow.log_param("model", "xgboost_monotonic_price")
            mlflow_run_id = run.info.run_id
            print("mlflow experiment", experiment)
            print("mlflow run", mlflow_run_id)
            runtime = "databricks"
    except Exception as exc:  # noqa: BLE001
        print("mlflow optional:", exc)
        if not has_spark:
            runtime = "local"

    DATABRICKS_RUNS.mkdir(parents=True, exist_ok=True)
    record = {
        "script": "databricks/02_train_new_model.py",
        "runtime": runtime,
        "model": "xgboost_monotonic_price",
        "mlflow_run_id": mlflow_run_id,
        "metrics": metrics,
        "artifact": "new_model/model.joblib",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    (DATABRICKS_RUNS / "train_run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("RUN_RECORD::" + json.dumps(record))
