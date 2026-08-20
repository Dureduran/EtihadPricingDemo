from lab.constants import FIXTURE_BOOKING
from lab.paths import MODEL_PATH, ROOT
from new_model.score import predict_buy_proba


def test_model_artifact_exists_for_local_scoring():
    assert MODEL_PATH.exists()


def test_higher_price_does_not_increase_p_buy():
    low = dict(FIXTURE_BOOKING, displayed_price=80)
    high = dict(FIXTURE_BOOKING, displayed_price=150)
    p_low = predict_buy_proba(low)
    p_high = predict_buy_proba(high)
    assert 0 <= p_high <= 1
    assert 0 <= p_low <= 1
    assert p_high <= p_low + 1e-6


def test_fixture_score_is_a_probability():
    p = predict_buy_proba(dict(FIXTURE_BOOKING, displayed_price=115))
    assert 0.0 <= p <= 1.0


def test_readme_explains_train_and_local_export_load():
    text = (ROOT / "databricks" / "README_DATABRICKS.md").read_text(encoding="utf-8")
    assert "02_train_new_model.py" in text
    assert "model.joblib" in text
    assert "predict_buy_proba" in text or "score.py" in text
    assert "Model Serving" in text


def test_train_run_metrics_file_exists():
    metrics = ROOT / "databricks" / "runs" / "local_train_metrics.json"
    train_run = ROOT / "databricks" / "runs" / "train_run.json"
    assert metrics.exists()
    text = metrics.read_text(encoding="utf-8")
    assert "auc" in text
    assert "log_loss" in text
    record = train_run.read_text(encoding="utf-8")
    assert "xgboost_monotonic_price" in record
    assert "mlflow_run_id" in record
