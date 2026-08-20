# Databricks Free — ingest and train

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

The New Model is trained here so the resume can honestly say **Databricks**, without linking a login-walled workspace.

## What these notebooks do

1. `01_ingest_offer_log.py` — load `data/offer_log_train.parquet` into tables `offer_log_raw` and `offer_log_train` using only training columns.
2. `02_train_new_model.py` — train XGBoost `P(buy | price, context)` with a decreasing constraint on price, log metrics, export `new_model/model.joblib`.

Paid Model Serving is **not** required. The Streamlit lab scores with the exported artifact.

## Free Edition steps

1. Create a Databricks Free workspace and a cluster / serverless compute that can run Python.
2. Clone [https://github.com/Dureduran/EtihadPricingDemo](https://github.com/Dureduran/EtihadPricingDemo) or upload this repo as a Repos folder.
3. Locally: `python -m data.build_offer_log` then upload `data/offer_log_train.parquet` to a workspace volume, or run the ingest notebook against a DBFS/volume path you set in the widget `train_path`.
4. Run `01_ingest_offer_log.py`, then `02_train_new_model.py`.
5. Download the exported `model.joblib` into `new_model/` if you trained only in the cloud.
6. Save the job run output (or a screenshot) into `databricks/runs/` so the repo proves it executed on Databricks, not only a laptop.

Catalog/schema suggestion: `workspace.ancillary_lab.offer_log_train`.

## Secrets

Do not commit tokens. Use Databricks secrets or environment variables. This repo has no Etihad credentials and must never have any.
