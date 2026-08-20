# Databricks Free — ingest and train

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

The New Model is trained here so the resume can honestly say **Databricks**, without linking a login-walled workspace.

## What these notebooks do

1. `01_ingest_offer_log.py` — load `data/offer_log_train.parquet` into tables `offer_log_raw` and `offer_log_train` using only training columns.
2. `02_train_new_model.py` — train XGBoost `P(buy | price, context)` with a decreasing constraint on price, log metrics, export `new_model/model.joblib`.

Paid Model Serving is **not** required. The Streamlit lab scores with the exported artifact.

## Free Edition steps

1. Create a **Databricks Free** workspace (login at [databricks.com](https://www.databricks.com/)) and start a cluster or serverless compute that can run Python.
2. Clone [https://github.com/Dureduran/EtihadPricingDemo](https://github.com/Dureduran/EtihadPricingDemo) into Repos, or upload this folder.
3. Locally: `python -m data.build_offer_log`. Upload `data/offer_log.parquet` (raw) and `data/offer_log_train.parquet` (train) to a workspace Volume, or set the notebook widget `train_path` to that Volume path.
4. In the notebook/script `01_ingest_offer_log.py`, confirm widget `train_path`. Run it. Expected tables: `offer_log_raw` and `offer_log_train` (Unity Catalog name `workspace.ancillary_lab.offer_log_train` when the catalog exists; otherwise workspace tables with those names).
5. `DESCRIBE` `offer_log_train`: columns are only the TRAINING_FEATURES list plus `purchased`. No `latent_wtp`, `generator_rule_id`, or `true_elasticity`.
6. Copy the job run JSON (or a redacted screenshot) into `databricks/runs/ingest_run.json` so `runtime` is `databricks`, not only `local`.
7. Run `02_train_new_model.py` on the same compute. It trains XGBoost `P(buy)` with a decreasing constraint on `displayed_price`, writes metrics to `databricks/runs/train_run.json` (and MLflow experiment `ancillary-new-model` when MLflow is available), and exports `new_model/model.joblib`. Paid Model Serving is not required.
8. Copy `new_model/model.joblib` (and `new_model/encoders.joblib`) into the repo if you trained only in the cloud. The Streamlit lab loads that artifact in `new_model/score.py` via `predict_buy_proba` — no Databricks endpoint.
9. Overwrite `databricks/runs/train_run.json` so `runtime` is `databricks` and `mlflow_run_id` is filled when the Free job succeeds.

A Deepair-style DNN is a spoken future A/B only; it is not the hero model.

Catalog/schema: `workspace.ancillary_lab`. Tables: `offer_log_raw`, `offer_log_train`.

## Secrets

Do not commit tokens. Use Databricks secrets or environment variables. This repo has no Etihad credentials and must never have any.
