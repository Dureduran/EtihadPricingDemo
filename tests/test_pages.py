import re
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
    assert "data-notes" not in text
    assert "INTERVIEW NOTES" not in text
    assert 'class="slide"' not in text
    assert "\u2014" not in text
    assert "\u2013" not in text


def test_walkthrough_visible_copy_has_no_hyphens():
    html = (DOCS / "walkthrough.html").read_text(encoding="utf-8")
    stripped = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)
    stripped = re.sub(r"<script[\s\S]*?</script>", "", stripped, flags=re.I)
    visible = re.sub(r"<[^>]+>", " ", stripped)
    assert "-" not in visible
