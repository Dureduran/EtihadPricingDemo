Paste Databricks Free job output or a redacted screenshot note here after you run `01_ingest` and `02_train` in the workspace.

`ingest_run.json` is written by `01_ingest_offer_log.py`. On a laptop it records `"runtime": "local"`. After a Free workspace run, replace it so `"runtime": "databricks"`.

Local training metrics are written to `local_train_metrics.json` when you run `python -m new_model.train`.
