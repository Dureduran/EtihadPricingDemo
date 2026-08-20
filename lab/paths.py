from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
GENERATOR_DIR = ROOT / "generator"
MODEL_DIR = ROOT / "new_model"
STATE_DIR = ROOT / "lab_state"
DATABRICKS_RUNS = ROOT / "databricks" / "runs"

OFFER_LOG = DATA_DIR / "offer_log.parquet"
TRAIN_LOG = DATA_DIR / "offer_log_train.parquet"
HIDDEN_WTP = GENERATOR_DIR / "hidden_wtp.parquet"
MODEL_PATH = MODEL_DIR / "model.joblib"
ENCODER_PATH = MODEL_DIR / "encoders.joblib"
ROLLOUT_STATE = STATE_DIR / "rollout.json"
OFFERS_LOG = STATE_DIR / "offers.parquet"
TEMP_CAPS = STATE_DIR / "temporary_caps.json"
