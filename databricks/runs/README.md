`ingest_run.json` and `train_run.json` now record a Databricks Free workspace run (`"runtime": "databricks"`).

In-notebook MLflow on Free serverless Spark Connect cannot read `spark.mlflow.modelRegistryUri`. Metrics for this train were logged to the workspace MLflow experiment `ancillary-new-model`; `mlflow_run_id` is in `train_run.json`. Do not hyperlink the workspace.

The Streamlit lab still scores from a locally compatible `new_model/model.joblib` (Databricks Runtime sklearn 1.3 pickles do not load on the lab's sklearn). Same training code and offer log.

Local-only training still writes `local_train_metrics.json` when you run `python -m new_model.train`.
