"""One-page interview leave-behind for the Ancillary Pricing Production Lab."""

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Frame,
    PageTemplate,
    BaseDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

NAVY = HexColor("#0B1F33")
GOLD = HexColor("#C4A35A")
INK = HexColor("#1A2A3A")
MUTED = HexColor("#4A6074")
RULE = HexColor("#D5DEE6")
PAPER = HexColor("#F7F4EE")
GITHUB = "https://github.com/Dureduran/EtihadPricingDemo"
PDF_PATH = Path(__file__).resolve().parent / "one_page_brief.pdf"


def styles() -> dict[str, ParagraphStyle]:
    return {
        "kicker": ParagraphStyle(
            "kicker",
            fontName="Times-Bold",
            fontSize=8,
            leading=10,
            textColor=GOLD,
            tracking=1.2,
        ),
        "title": ParagraphStyle(
            "title",
            fontName="Times-Bold",
            fontSize=18,
            leading=21,
            textColor=white,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Times-Italic",
            fontSize=9.5,
            leading=12,
            textColor=HexColor("#E8EEF4"),
        ),
        "h": ParagraphStyle(
            "h",
            fontName="Times-Bold",
            fontSize=10.5,
            leading=13,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Times-Roman",
            fontSize=9.2,
            leading=12.1,
            textColor=INK,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="Times-Italic",
            fontSize=8,
            leading=10.5,
            textColor=MUTED,
        ),
        "label": ParagraphStyle(
            "label",
            fontName="Times-Bold",
            fontSize=8.4,
            leading=11,
            textColor=NAVY,
        ),
        "cell": ParagraphStyle(
            "cell",
            fontName="Times-Roman",
            fontSize=8.4,
            leading=11,
            textColor=INK,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Times-Roman",
            fontSize=8,
            leading=10,
            textColor=MUTED,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Times-Roman",
            fontSize=9.2,
            leading=12.1,
            textColor=INK,
            leftIndent=4,
        ),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 1.18 * inch, width, 1.18 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, height - 1.22 * inch, width, 0.045 * inch, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, 0.42 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 0.42 * inch, width, 0.03 * inch, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#9BB0C3"))
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(0.6 * inch, 0.18 * inch, GITHUB)
    canvas.drawRightString(
        width - 0.6 * inch,
        0.18 * inch,
        "Independent portfolio prototype  |  synthetic / public data only",
    )
    canvas.restoreState()


def build():
    s = styles()
    doc = BaseDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.58 * inch,
        rightMargin=0.58 * inch,
        topMargin=1.38 * inch,
        bottomMargin=0.55 * inch,
        title="Ancillary Pricing Production Lab",
        author="Independent portfolio prototype",
        subject="Interview one-page brief",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="one", frames=[frame], onPage=header_footer)])

    def header_with_title(canvas, doc_):
        header_footer(canvas, doc_)
        canvas.saveState()
        width, height = letter
        y = height - 0.28 * inch
        canvas.setFillColor(GOLD)
        canvas.setFont("Times-Bold", 8)
        canvas.drawString(0.6 * inch, y, "ANCILLARY PRICING PRODUCTION LAB")
        canvas.setFillColor(white)
        canvas.setFont("Times-Bold", 14)
        canvas.drawString(
            0.6 * inch,
            y - 22,
            "Testing, safely rolling out and monitoring ML pricing",
        )
        canvas.setFont("Times-Italic", 9)
        canvas.setFillColor(HexColor("#D5DEE6"))
        canvas.drawString(
            0.6 * inch,
            y - 38,
            "Extra baggage and extra-legroom seats  |  Current Pricing vs New Model  |  Business Rules keep final control",
        )
        canvas.restoreState()

    doc.pageTemplates[0].onPage = header_with_title

    story = []
    story.append(
        Paragraph(
            "Etihad already prices ancillaries in-house. The job is not to build a model that prints a price. "
            "It is to test a <b>New Model</b> against <b>Current Pricing</b>, keep <b>Business Rules</b> in control, "
            "roll out in traffic steps, and HOLD or <b>Return to Current Pricing</b> when the model is not healthy.",
            s["body"],
        )
    )

    two = Table(
        [
            [
                Paragraph("Current Pricing", s["label"]),
                Paragraph("New Model", s["label"]),
            ],
            [
                Paragraph(
                    "Simulated existing system using route, days to departure, product, channel, and remaining inventory.",
                    s["cell"],
                ),
                Paragraph(
                    "P(buy | price, booking context), then Price x P(buy) on an allowed grid. Trained on Databricks; BigQuery ingest in-repo. Scored in the lab from an exported artifact.",
                    s["cell"],
                ),
            ],
        ],
        colWidths=[3.55 * inch, 3.55 * inch],
    )
    two.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (0, -1), 0.4, GOLD),
                ("BOX", (1, 0), (1, -1), 0.4, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 0), (0, 0)),
            ]
        )
    )
    story.append(Spacer(1, 6))
    story.append(two)
    story.append(
        Paragraph(
            "<b>Business Rules</b> always finish the job (included-in-fare, loyalty, min/max, inventory, airport vs online bags, temporary RM caps). "
            "Example: recommend AED 175, cap AED 150, customer sees AED 150.",
            s["body"],
        )
    )

    story.append(Paragraph("Products, rollout, checkout", s["h"]))
    story.append(
        Paragraph(
            "<b>v1 products:</b> extra baggage and preferred / extra-legroom seat. Fare-brand upgrades are future expansion, not built here.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Rollout:</b> Offline to shadow (log New Model, customer still gets Current Pricing) to 5% to 20% to 50% to 100%. Pause or Return to Current Pricing at any time.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Checkout fallback:</b> New Model to Current Pricing to simple rules to a safe fixed price. If the model fails at checkout, the customer still gets a valid price.",
            s["body"],
        )
    )

    story.append(Paragraph("How to read the four screens", s["h"]))
    screens = [
        ("1. Price Explanation", "Why this booking's extra-legroom price moved versus Current Pricing. Both prices in AED."),
        ("2. Pricing Controls", "Traffic percent, price bands, temporary caps. Not per-passenger approval."),
        ("3. Pricing Test Results", "Revenue per passenger, conversion, average selling price. Simulated comparison."),
        ("4. Production Monitor", "Commercial, model, system, and rules health, then a Rollout Decision: HOLD / expand / return."),
    ]
    rows = [
        [Paragraph(title, s["label"]), Paragraph(desc, s["cell"])]
        for title, desc in screens
    ]
    grid = Table(rows, colWidths=[1.7 * inch, 5.4 * inch])
    grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
            ]
        )
    )
    story.append(grid)

    story.append(Paragraph("Two-minute walk", s["h"]))
    walk = [
        ("Price Explanation", "Show why the New Model recommends a different extra-legroom price than Current Pricing on AUH-LHR Economy Basic, four days out. Both prices are in AED."),
        ("Pricing Controls", "Revenue Management sets traffic, bands, pause, or Return to Current Pricing. Not per-passenger approval."),
        ("Pricing Test Results", "Ask whether revenue per passenger rose without damaging conversion. Say out loud: simulated result using synthetic/public data."),
        ("Production Monitor", "If behaviour drifts or quality drops, HOLD expansion or Return to Current Pricing. Checkout still has a fallback."),
    ]
    walk_rows = [
        [Paragraph(title, s["label"]), Paragraph(desc, s["cell"])]
        for title, desc in walk
    ]
    walk_grid = Table(walk_rows, colWidths=[1.7 * inch, 5.4 * inch])
    walk_grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
            ]
        )
    )
    story.append(walk_grid)

    story.append(Paragraph("Resume bullets", s["h"]))
    story.append(
        Paragraph(
            "Built a production lab that tests a New Model against Current Pricing for extra baggage and extra-legroom seats, then applies Business Rules so Revenue Management keeps final control.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Trained P(buy | price, booking context) on Databricks, selected price by expected revenue, and compared Current vs New on simulated offer logs (synthetic + public data).",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Added rollout (shadow to 5% to 20%), checkout fallback, and a monitor with a HOLD / Return to Current Pricing decision so a model is not left live when behaviour drifts.",
            s["body"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Honesty line for every interview answer: <i>Simulated result using synthetic/public data.</i> "
            "Do not claim Etihad employment, Etihad data, or a live airline A/B test.",
            s["small"],
        )
    )

    doc.build(story)
    print(f"wrote {PDF_PATH}")


if __name__ == "__main__":
    build()
