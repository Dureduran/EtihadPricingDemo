from pathlib import Path

from lab.copy import (
    BUSINESS_RULES,
    CURRENT_PRICING,
    DISCLAIMER,
    FORBIDDEN_UI_WORDS,
    HEADLINE,
    NEW_MODEL,
    PRICING_TEST_RESULTS,
    RETURN_TO_CURRENT,
    ROLLOUT_DECISION,
    SUBTITLE,
)

ROOT = Path(__file__).resolve().parents[1]
SCAN = [
    ROOT / "app",
    ROOT / "README.md",
    ROOT / "DATA_CARD.md",
]
REQUIRED_FOLDERS = (
    "data",
    "current_pricing",
    "business_rules",
    "new_model",
    "rollout",
    "monitor",
    "app",
    "databricks",
    "interview",
)
REQUIRED_LANGUAGE = (
    CURRENT_PRICING,
    NEW_MODEL,
    BUSINESS_RULES,
    ROLLOUT_DECISION,
    RETURN_TO_CURRENT,
    PRICING_TEST_RESULTS,
)


def _readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def test_forbidden_words_not_in_ui_copy():
    hits = []
    files = []
    for path in SCAN:
        if path.is_file():
            files.append(path)
        else:
            files.extend(path.rglob("*.py"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        # lab/copy.py may list forbidden words as a detection tuple.
        if path.name == "copy.py":
            continue
        for word in FORBIDDEN_UI_WORDS:
            if word in text:
                hits.append(f"{path}: {word}")
    assert hits == []


def test_forbidden_ui_words_include_policy():
    assert "Policy" in FORBIDDEN_UI_WORDS
    assert "Champion" in FORBIDDEN_UI_WORDS
    assert "Challenger" in FORBIDDEN_UI_WORDS
    assert "Rollback" in FORBIDDEN_UI_WORDS


def test_readme_opens_with_headline_subtitle_disclaimer():
    lines = [line.strip() for line in _readme().splitlines() if line.strip()]
    assert lines[0] == f"# {HEADLINE}"
    assert lines[1] == SUBTITLE
    assert lines[2] == DISCLAIMER


def test_readme_uses_required_language_and_v1_products():
    text = _readme()
    for phrase in REQUIRED_LANGUAGE:
        assert phrase in text
    assert "extra baggage" in text.lower()
    assert "extra-legroom" in text.lower() or "extra legroom" in text.lower()
    assert "future expansion" in text.lower()


def test_folder_layout_exists():
    missing = [name for name in REQUIRED_FOLDERS if not (ROOT / name).is_dir()]
    assert missing == []


def test_data_card_has_four_honesty_sections():
    text = (ROOT / "DATA_CARD.md").read_text(encoding="utf-8")
    assert "## A. Public seed" in text
    assert "british-airways" in text.lower() or "british airways" in text.lower()
    assert "## B. Synthetic fields" in text
    assert "## C. What the New Model may see" in text
    assert "displayed price" in text.lower()
    assert "## D. What I would request in week one on the job" in text
