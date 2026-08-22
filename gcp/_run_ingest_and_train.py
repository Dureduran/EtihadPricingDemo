# Vertex AI Workbench / Colab notebook source
# Independent portfolio prototype. Synthetic/public data only.
%pip install xgboost scikit-learn joblib pyarrow pandas google-cloud-bigquery google-cloud-storage --quiet

# ---

import sys
from pathlib import Path

ROOT = next(
    (
        path
        for path in (
            Path.cwd(),
            Path.cwd().parent,
            Path("/content/EtihadPricingDemo"),
            Path("/home/jupyter/EtihadPricingDemo"),
        )
        if (path / "new_model").exists()
    ),
    Path.cwd(),
)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_script(rel: str) -> None:
    path = ROOT / rel
    namespace = {"__name__": "__main__", "__file__": str(path)}
    with open(path, encoding="utf-8") as handle:
        exec(compile(handle.read(), str(path), "exec"), namespace)


print("INGEST")
run_script("gcp/01_ingest_offer_log.py")
print("TRAIN")
run_script("gcp/02_train_new_model.py")
print("DONE")
