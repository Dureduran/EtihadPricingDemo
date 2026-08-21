# Databricks notebook source
# Independent portfolio prototype. Synthetic/public data only.
%pip install xgboost scikit-learn joblib pyarrow

# COMMAND ----------

import sys

ROOT = "/Volumes/workspace/default/ancillary_lab"
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def run_script(rel: str) -> None:
    path = f"{ROOT}/{rel}"
    namespace = {
        "spark": spark,
        "dbutils": dbutils,
        "__name__": "__main__",
        "__file__": path,
    }
    with open(path, encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)


print("INGEST")
run_script("databricks/01_ingest_offer_log.py")
print("TRAIN")
run_script("databricks/02_train_new_model.py")
print("DONE")
