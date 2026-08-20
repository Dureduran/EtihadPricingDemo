from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("Champion", "Challenger", "Rollback")
SCAN = [
    ROOT / "app",
    ROOT / "README.md",
    ROOT / "DATA_CARD.md",
]


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
        for word in FORBIDDEN:
            if word in text:
                hits.append(f"{path}: {word}")
    assert hits == []
