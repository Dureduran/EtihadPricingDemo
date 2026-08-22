# GCP (Colab / Vertex AI Workbench) — ingest and train

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

The offer log is ingested here so the resume can honestly say **BigQuery** and **Vertex AI** / **Colab**, without linking a login-walled console. Paid Vertex Prediction is **not** required. The Streamlit lab scores with the exported artifact.

## What these notebooks do

1. `01_ingest_offer_log.py` — load `data/offer_log_train.parquet` into BigQuery tables `offer_log_raw` and `offer_log_train` using only training columns.
2. `02_train_new_model.py` — train XGBoost `P(buy | price, context)` with a decreasing constraint on price, log metrics, export `new_model/model.joblib`.
3. `run_ingest_and_train.ipynb` — Colab / Vertex notebook that runs ingest then train.

The same New Model code as Databricks (`new_model/train.py`). Local pytest uses parquet, not BigQuery.

## Free-tier steps (Colab + BigQuery sandbox)

1. Create a **Google Cloud** project (BigQuery sandbox is enough; Vertex AI Workbench is optional) or open [Google Colab](https://colab.research.google.com/).
2. Clone [https://github.com/Dureduran/EtihadPricingDemo](https://github.com/Dureduran/EtihadPricingDemo) into the notebook runtime, or upload this folder to a **Vertex AI Workbench** instance.
3. Locally: `python -m data.build_offer_log`. Upload `data/offer_log.parquet` (raw) and `data/offer_log_train.parquet` (train) to a GCS bucket, or leave them in the cloned repo.
4. In Colab, authenticate and set the project:

   ```python
   from google.colab import auth
   auth.authenticate_user()
   import os
   os.environ["GCP_PROJECT"] = "YOUR_PROJECT_ID"
   os.environ["GCP_INGEST_BQ"] = "1"
   ```

   Optional: `GCP_TRAIN_PATH=gs://YOUR_BUCKET/offer_log_train.parquet`.
5. Run `gcp/01_ingest_offer_log.py` (or the ingest cells in `run_ingest_and_train.ipynb`). Expected tables: `ancillary_lab.offer_log_raw` and `ancillary_lab.offer_log_train`.
6. In BigQuery, `SELECT column_name FROM YOUR_PROJECT.ancillary_lab.INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'offer_log_train'`. Columns are only the TRAINING_FEATURES list plus `purchased`. No `latent_wtp`, `generator_rule_id`, or `true_elasticity`.
7. Copy the printed `RUN_RECORD::` JSON into `gcp/runs/ingest_run.json` so `runtime` is `gcp`, not only `local`.
8. Run `02_train_new_model.py` on the same runtime. It trains XGBoost `P(buy)` with a decreasing constraint on `displayed_price`, writes metrics to `gcp/runs/train_run.json` (and Vertex AI Experiment `ancillary-new-model` when the SDK is available), and exports `new_model/model.joblib`. Paid Vertex Prediction / Model Registry serving is not required.
9. Copy `new_model/model.joblib` (and `new_model/encoders.joblib`) into the repo if you trained only in the cloud. The Streamlit lab loads that artifact in `new_model/score.py` via `predict_buy_proba` — no Vertex endpoint.
10. Overwrite `gcp/runs/train_run.json` so `runtime` is `gcp` and `vertex_run_id` is filled when the cloud job succeeds.

A Deepair-style DNN is a spoken future A/B only; it is not the hero model.

Dataset: `ancillary_lab`. Tables: `offer_log_raw`, `offer_log_train`.

## Secrets

Do not commit tokens, service-account JSON, or `GOOGLE_APPLICATION_CREDENTIALS` files. Use Colab auth, Workbench ADC, or environment variables. This repo has no Etihad credentials and must never have any.
