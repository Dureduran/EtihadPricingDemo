# Databricks Free — train New Model P(buy).
# Must not load the hidden WTP package. Exports new_model/model.joblib for the lab.

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from new_model.train import train


if __name__ == "__main__":
    banned = [n for n in sys.modules if n == "generator" or n.startswith("generator.")]
    if banned:
        raise SystemExit(f"refusing to train; generator imported: {banned}")
    metrics = train()
    print(json.dumps(metrics, indent=2))
    try:
        import mlflow

        mlflow.set_experiment("ancillary-new-model")
        with mlflow.start_run(run_name="new-model-pbuy"):
            mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, (int, float))})
            mlflow.log_param("model", "xgboost_monotonic_price")
            print("mlflow run", mlflow.active_run().info.run_id)
    except Exception as exc:  # noqa: BLE001
        print("mlflow optional:", exc)
