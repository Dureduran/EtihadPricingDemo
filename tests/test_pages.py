from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_github_pages_includes_walkthrough():
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    walkthrough = DOCS / "walkthrough.html"
    assert walkthrough.is_file()
    assert 'href="walkthrough.html"' in index
    text = walkthrough.read_text(encoding="utf-8")
    assert "EXECUTIVE WALKTHROUGH" in text
    assert "Return to Current Pricing" in text
