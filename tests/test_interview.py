from pathlib import Path

from lab.copy import (
    BUSINESS_RULES,
    CURRENT_PRICING,
    FORBIDDEN_UI_WORDS,
    NEW_MODEL,
    SIMULATED_BANNER,
)

ROOT = Path(__file__).resolve().parents[1]
INTERVIEW = ROOT / "interview"
STORY = INTERVIEW / "2_minute_story.md"
HIREVUE = INTERVIEW / "hirevue_map.md"
CASE = INTERVIEW / "case_outline.md"
RESUME = INTERVIEW / "resume_links.md"
PACK = (STORY, HIREVUE, CASE, RESUME)


def test_two_minute_story_opening_and_four_screens():
    text = STORY.read_text(encoding="utf-8")
    opening = text.split("Then show")[0]
    assert "Etihad already has" in opening
    assert "in-house ancillary" in opening.lower()
    assert "production lab" in opening.lower()
    assert "dashboard" in opening.lower()
    for screen in (
        "Price Explanation",
        "Pricing Controls",
        "Pricing Test Results",
        "Production Monitor",
    ):
        assert screen in text
    assert text.index("Price Explanation") < text.index("Pricing Controls")
    assert text.index("Pricing Controls") < text.index("Pricing Test Results")
    assert text.index("Pricing Test Results") < text.index("Production Monitor")
    lead = opening.lower()
    assert not lead.strip().startswith("doha")
    assert "rask" not in lead
    assert "overbooking" not in lead


def test_hirevue_maps_four_screens_to_required_beats():
    text = HIREVUE.read_text(encoding="utf-8")
    assert "Price Explanation" in text
    assert "Pricing Controls" in text
    assert "Pricing Test Results" in text
    assert "Production Monitor" in text
    assert "Inherit existing pricing" in text
    assert BUSINESS_RULES in text
    assert "Safe rollout" in text
    assert "Commercial impact" in text
    assert "HOLD" in text
    assert "Checkout fallback" in text


def test_case_outline_is_eight_minute_lab_with_spoken_90_day_ideas():
    text = CASE.read_text(encoding="utf-8")
    assert "8-minute" in text
    assert "90-day" in text
    assert "fare-brand buy-up" in text
    assert "fare+ancillary" in text or "fare + ancillary" in text
    assert "Spoken 90-day" in text


def test_resume_leads_with_lab_placeholder_then_qa_dashboard():
    text = RESUME.read_text(encoding="utf-8")
    lab_url = "https://dureduran.github.io/EtihadPricingDemo/"
    assert lab_url in text
    assert "https://qa-dashboard-lac.vercel.app/" in text
    assert "supporting" in text.lower()
    assert text.index("Ancillary Pricing Production Lab") < text.index(
        "https://qa-dashboard-lac.vercel.app/"
    )
    assert text.index(lab_url) < text.index("https://qa-dashboard-lac.vercel.app/")


def test_demo_language_aed_current_new_and_banner_aloud():
    story = STORY.read_text(encoding="utf-8")
    assert "AED" in story
    assert CURRENT_PRICING in story
    assert NEW_MODEL in story
    assert SIMULATED_BANNER in story


def test_pack_does_not_record_heygen_or_scrape_or_use_forbidden_ui_words():
    blob = "\n".join(path.read_text(encoding="utf-8") for path in PACK)
    assert "HeyGen" not in blob
    assert ".docx" not in blob
    assert "scrape" not in blob.lower()
    for word in FORBIDDEN_UI_WORDS:
        assert word not in blob
