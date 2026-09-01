#!/usr/bin/env python3
"""Generate the BlueTeamer HVVL UAT interim VAPT report."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import CellStyle


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
EVIDENCE_DIR = ROOT / "output" / "evidence"
PDF_PATH = OUT_DIR / "BlueTeamer_HVVL_UAT_Interim_VAPT_Report_2026-07-13.pdf"
MD_PATH = OUT_DIR / "BlueTeamer_HVVL_UAT_Interim_VAPT_Report_2026-07-13.md"

FONT_DIR = Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts")
FONT_FILES = {
    "Calibri": FONT_DIR / "Calibri.ttf",
    "Calibri-Bold": FONT_DIR / "Calibrib.ttf",
    "Calibri-Italic": FONT_DIR / "Calibrii.ttf",
    "Calibri-BoldItalic": FONT_DIR / "Calibriz.ttf",
}

BRAND_BLUE = colors.HexColor("#015EB8")
BRAND_DEEP = colors.HexColor("#0C0E12")
BRAND_SURFACE = colors.HexColor("#111417")
BRAND_CLOUD = colors.HexColor("#F8FBFF")
BRAND_GOLD = colors.HexColor("#F6BE2A")
TEXT = colors.HexColor("#1E2933")
MUTED = colors.HexColor("#5B6875")
LINE = colors.HexColor("#D7E0E8")
HIGH = colors.HexColor("#B42318")
MEDIUM = colors.HexColor("#B54708")
LOW = colors.HexColor("#175CD3")
INFO = colors.HexColor("#475467")
PASS = colors.HexColor("#067647")
PARTIAL = colors.HexColor("#B54708")
OPEN = colors.HexColor("#B42318")
PENDING = colors.HexColor("#475467")


def register_fonts() -> None:
    for name, path in FONT_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Required Calibri font not found: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Calibri",
        normal="Calibri",
        bold="Calibri-Bold",
        italic="Calibri-Italic",
        boldItalic="Calibri-BoldItalic",
    )
    rl_config.canvas_basefontname = "Calibri"
    CellStyle.fontname = "Calibri"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def cell(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(str(text), style)


class ReportDoc(BaseDocTemplate):
    def __init__(
        self,
        filename: str,
        styles: dict[str, ParagraphStyle],
        title: str = "HVVL LMS UAT Interim VAPT Report",
        subject: str = "Interim web application VAPT remediation retest",
        header_title: str = "HVVL UAT Interim VAPT Report",
        cover_footer: str = "CONFIDENTIAL - INTERIM SECURITY ASSESSMENT",
    ):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=23 * mm,
            bottomMargin=20 * mm,
            title=title,
            author="BlueTeamer",
            subject=subject,
        )
        self.styles_ref = styles
        self.header_title = header_title
        self.cover_footer = cover_footer
        width, height = A4
        cover_frame = Frame(22 * mm, 20 * mm, width - 44 * mm, height - 40 * mm, id="cover")
        body_frame = Frame(18 * mm, 20 * mm, width - 36 * mm, height - 43 * mm, id="body")
        self.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=[cover_frame], onPage=self.draw_cover),
                PageTemplate(id="Body", frames=[body_frame], onPage=self.draw_body),
            ]
        )

    def draw_cover(self, canvas, _doc) -> None:
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(BRAND_DEEP)
        canvas.rect(0, 0, width, height, stroke=0, fill=1)
        canvas.setFillColor(BRAND_BLUE)
        canvas.rect(0, 0, 8 * mm, height, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#1B2027"))
        canvas.rect(8 * mm, 0, width - 8 * mm, 16 * mm, stroke=0, fill=1)
        canvas.setFont("Calibri", 8.5)
        canvas.setFillColor(colors.HexColor("#C7D0DA"))
        canvas.drawString(22 * mm, 6 * mm, self.cover_footer)
        canvas.restoreState()

    def draw_body(self, canvas, doc) -> None:
        width, height = A4
        canvas.saveState()
        logo = OUT_DIR / "assets" / "blueteamer-logo-blue.png"
        if logo.exists():
            canvas.drawImage(str(logo), 18 * mm, height - 15.5 * mm, 7 * mm, 7 * mm, mask="auto")
        canvas.setFillColor(BRAND_BLUE)
        canvas.setFont("Calibri-Bold", 9)
        canvas.drawString(27 * mm, height - 12 * mm, "BlueTeamer")
        canvas.setFillColor(MUTED)
        canvas.setFont("Calibri", 8)
        canvas.drawRightString(width - 18 * mm, height - 12 * mm, self.header_title)
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, height - 17 * mm, width - 18 * mm, height - 17 * mm)
        canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
        canvas.setFont("Calibri", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 9 * mm, "https://blueteamer.co")
        canvas.drawCentredString(width / 2, 9 * mm, "CONFIDENTIAL")
        canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
            elif style_name == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))


class CalibriCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("initialFontName", "Calibri")
        kwargs.setdefault("initialFontSize", 10)
        kwargs.setdefault("initialLeading", 12)
        super().__init__(*args, **kwargs)


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}
    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Calibri",
        fontSize=9.5,
        leading=13,
        textColor=TEXT,
        spaceAfter=5,
    )
    styles["BodySmall"] = ParagraphStyle(
        "BodySmall",
        parent=styles["Body"],
        fontSize=8,
        leading=10.5,
        spaceAfter=3,
    )
    styles["BodyMuted"] = ParagraphStyle(
        "BodyMuted",
        parent=styles["Body"],
        textColor=MUTED,
    )
    styles["H1"] = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontName="Calibri-Bold",
        fontSize=19,
        leading=22,
        textColor=BRAND_DEEP,
        spaceBefore=4,
        spaceAfter=9,
        keepWithNext=True,
    )
    styles["H2"] = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontName="Calibri-Bold",
        fontSize=13,
        leading=16,
        textColor=BRAND_BLUE,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )
    styles["H3"] = ParagraphStyle(
        "H3",
        parent=base["Heading3"],
        fontName="Calibri-Bold",
        fontSize=10.5,
        leading=13,
        textColor=BRAND_DEEP,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True,
    )
    styles["CoverBrand"] = ParagraphStyle(
        "CoverBrand",
        fontName="Calibri-Bold",
        fontSize=19,
        leading=22,
        textColor=colors.white,
        spaceAfter=20,
    )
    styles["CoverTitle"] = ParagraphStyle(
        "CoverTitle",
        fontName="Calibri-Bold",
        fontSize=27,
        leading=31,
        textColor=colors.white,
        spaceAfter=12,
    )
    styles["CoverSub"] = ParagraphStyle(
        "CoverSub",
        fontName="Calibri",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#D7E0E8"),
        spaceAfter=18,
    )
    styles["CoverMeta"] = ParagraphStyle(
        "CoverMeta",
        fontName="Calibri",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#C7D0DA"),
    )
    styles["TableHeader"] = ParagraphStyle(
        "TableHeader",
        fontName="Calibri-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_LEFT,
    )
    styles["TableCell"] = ParagraphStyle(
        "TableCell",
        fontName="Calibri",
        fontSize=7.8,
        leading=10,
        textColor=TEXT,
    )
    styles["TableCellBold"] = ParagraphStyle(
        "TableCellBold",
        parent=styles["TableCell"],
        fontName="Calibri-Bold",
    )
    styles["Caption"] = ParagraphStyle(
        "Caption",
        fontName="Calibri-Italic",
        fontSize=7.5,
        leading=9.5,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=7,
    )
    styles["Callout"] = ParagraphStyle(
        "Callout",
        fontName="Calibri-Bold",
        fontSize=10,
        leading=14,
        textColor=BRAND_DEEP,
    )
    styles["Right"] = ParagraphStyle(
        "Right",
        parent=styles["BodySmall"],
        alignment=TA_RIGHT,
    )
    styles["Center"] = ParagraphStyle(
        "Center",
        parent=styles["Body"],
        alignment=TA_CENTER,
    )
    return styles


def make_table(
    rows: list[list],
    widths: list[float],
    header: bool = True,
    font_size: float = 7.8,
    repeat_rows: int = 1,
) -> LongTable:
    table = LongTable(rows, colWidths=widths, repeatRows=repeat_rows if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Calibri"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, BRAND_CLOUD]),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_SURFACE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Calibri-Bold"),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def status_badge(label: str, color: colors.Color, styles: dict[str, ParagraphStyle]) -> Table:
    t = Table([[cell(label, styles["TableHeader"])]], colWidths=[35 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("BOX", (0, 0), (-1, -1), 0, color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


def callout(title: str, body: str, color: colors.Color, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[cell(title, styles["Callout"])], [cell(body, styles["Body"])]]
    t = Table(rows, colWidths=[174 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ("LINEBEFORE", (0, 0), (0, -1), 4, color),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return t


def finding_header(
    finding_id: str,
    title: str,
    severity: str,
    status: str,
    severity_color: colors.Color,
    styles: dict[str, ParagraphStyle],
) -> Table:
    left = cell(f"<b>{finding_id}</b><br/>{title}", styles["Body"])
    right = cell(f"<b>{severity}</b><br/>{status}", styles["Right"])
    t = Table([[left, right]], colWidths=[132 * mm, 42 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ("LINEBEFORE", (0, 0), (0, 0), 5, severity_color),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return t


def add_dash_items(story: list, items: list[str], styles: dict[str, ParagraphStyle]) -> None:
    for item in items:
        story.append(p(f"- {item}", styles["Body"]))


def load_retest_results() -> list[dict]:
    path = EVIDENCE_DIR / "retest-20260713-direct" / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))["results"]


def build_markdown() -> str:
    return """# BlueTeamer HVVL LMS UAT Interim VAPT Report

Report ID: BT-VAPT-HVVL-UAT-20260713-INT-01  
Assessment date: 13 July 2026  
Target: https://hvlabonline-uat.singaporetech.edu.sg  
Prepared by: BlueTeamer - https://blueteamer.co  
Classification: Confidential  

## Interim acceptance position

Conditional UAT acceptance is supportable for continued controlled testing, but a clean security closure is not yet supportable. Anonymous RBAC exposure, public API documentation, malformed JWT handling, CORS allowlisting, common security headers, repository secret leakage, frontend dependency risk, and production source maps were retested successfully. The remaining acceptance conditions are vulnerable Python dependencies, an LTI launch failure ending at `/lti-required?error=invalid_token`, authenticated cross-user and cross-course RBAC coverage, managed-cookie disposition, runtime-config cache policy, and independent confirmation of database-level constraints/RLS.

## Finding summary

| ID | Severity | Status | Finding |
| --- | --- | --- | --- |
| BT-HVVL-2026-001 | High | Open | Known-vulnerable backend dependency versions remain |
| BT-HVVL-2026-002 | Low | Open | Public runtime config is cacheable for 30 seconds |
| BT-HVVL-2026-003 | Low | Partially mitigated | Managed infrastructure cookies lack the target attribute set |
| BT-HVVL-2026-004 | Informational | Accepted/Review | Optional response headers reported by Nuclei |

Operational observation: Brightspace login succeeded, but the VHVL launch ended at `/lti-required?error=invalid_token`, preventing an authenticated application session.

## Verified remediation results

- Direct safe retest: 19 pass, 0 fail, 0 review, 0 inconclusive.
- Caido-captured safe retest: 19 pass, 0 fail, 0 review, 0 inconclusive.
- Anonymous student lists, rosters, course results, student responses, student ID lookup, student-course mapping, signed URL generation, and local file access returned 401/403.
- Invalid anonymous writes were blocked before request validation.
- SQLi probes returned controlled 401/403 responses with no database or framework error leakage.
- Malformed and `alg=none` bearer tokens returned 401.
- Untrusted CORS preflight returned 400 without `Access-Control-Allow-Origin`; the exact Brightspace origin was allowed.
- `/docs` and `/openapi.json` returned 404; `/.env` and `/.git/config` returned 403.
- HTTP redirected to HTTPS, TRACE returned 405, and the certificate was valid with TLS 1.2/1.3 support.
- `npm audit --omit=dev` reported zero vulnerabilities.
- Gitleaks scanned 37 commits and found no leaks.
- The production frontend build completed and emitted zero source maps.

## Open acceptance conditions

1. Upgrade and re-audit Starlette, python-multipart, PyJWT, cryptography, pydantic-settings, and ecdsa dependencies.
2. Correct the LTI token/launch integration and repeat the authenticated student test.
3. Run student A vs student B, enrolled vs unenrolled course, assigned teacher vs unassigned course, and course-admin tests with authorized accounts.
4. Set `/env-config.js` to `Cache-Control: no-store` or document an approved exception.
5. Document AWS ALB/Cloudflare cookie ownership and approved compensating controls; verify application-owned session cookies after LTI works.
6. Confirm migration preflight cleanup, final uniqueness/NOT NULL constraints, runtime database role grants, and RLS enablement on the deployed PostgreSQL database.

## Evidence locations

- `output/evidence/retest-20260713-direct/`
- `output/evidence/retest-20260713-caido/`
- `output/evidence/vapt-20260713-nuclei/`
- `output/evidence/vapt-20260713-code/`
- `output/evidence/vapt-20260713-browser/caido-http-history.png`

This is an interim report for UAT/cloud acceptance planning. It is not a final certificate of security and does not authorize production rollout without closure or formal risk acceptance of the open conditions.
"""


def build_story(styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    logo_white = OUT_DIR / "assets" / "blueteamer-logo-white.png"
    if logo_white.exists():
        story.append(Image(str(logo_white), width=24 * mm, height=24 * mm))
    story.append(Spacer(1, 8 * mm))
    story.append(p("BLUETEAMER", styles["CoverBrand"]))
    story.append(p("Interim Web Application<br/>VAPT Retest Report", styles["CoverTitle"]))
    story.append(p("SIT Virtual High Voltage Laboratory - UAT", styles["CoverSub"]))
    cover_status = Table(
        [[cell("CONDITIONAL UAT ACCEPTANCE", styles["TableHeader"])]],
        colWidths=[82 * mm],
    )
    cover_status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cover_status)
    story.append(Spacer(1, 24 * mm))
    story.append(
        p(
            "<b>Target</b><br/>https://hvlabonline-uat.singaporetech.edu.sg<br/><br/>"
            "<b>Assessment date</b><br/>13 July 2026<br/><br/>"
            "<b>Report ID</b><br/>BT-VAPT-HVVL-UAT-20260713-INT-01<br/><br/>"
            "<b>Prepared by</b><br/>BlueTeamer - https://blueteamer.co",
            styles["CoverMeta"],
        )
    )
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    story.append(p("Document Control", styles["H1"]))
    doc_rows = [
        [cell("Field", styles["TableHeader"]), cell("Value", styles["TableHeader"])],
        [cell("Document title", styles["TableCellBold"]), cell("HVVL LMS UAT Interim VAPT Retest Report", styles["TableCell"])],
        [cell("Client environment", styles["TableCellBold"]), cell("Singapore Institute of Technology UAT", styles["TableCell"])],
        [cell("Assessment type", styles["TableCellBold"]), cell("Authorized, non-destructive web application and API remediation retest", styles["TableCell"])],
        [cell("Prepared by", styles["TableCellBold"]), cell("BlueTeamer - https://blueteamer.co", styles["TableCell"])],
        [cell("Classification", styles["TableCellBold"]), cell("Confidential", styles["TableCell"])],
        [cell("Version", styles["TableCellBold"]), cell("Interim 1.0", styles["TableCell"])],
        [cell("Status", styles["TableCellBold"]), cell("Conditional UAT acceptance; not a final security certificate", styles["TableCell"])],
    ]
    story.append(make_table(doc_rows, [43 * mm, 131 * mm]))
    story.append(Spacer(1, 7 * mm))
    story.append(
        callout(
            "Use and distribution",
            "This report is intended for the client project, cloud, security, and deployment teams. It contains security-sensitive implementation details and should be distributed on a need-to-know basis.",
            BRAND_BLUE,
            styles,
        )
    )
    story.append(Spacer(1, 8 * mm))
    story.append(p("Contents", styles["H1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC1", fontName="Calibri", fontSize=9.5, leading=14, leftIndent=0, textColor=TEXT),
        ParagraphStyle("TOC2", fontName="Calibri", fontSize=8.5, leading=12, leftIndent=10, textColor=MUTED),
    ]
    story.append(toc)
    story.append(PageBreak())

    story.append(p("1. Executive Summary", styles["H1"]))
    story.append(
        callout(
            "Interim position: Conditional UAT acceptance",
            "The deployed UAT site shows material improvement and can continue controlled client acceptance testing. A clean closure or production security sign-off is not yet supportable because backend dependency advisories remain open, the Brightspace LTI launch fails with invalid_token, and authenticated cross-user/cross-course RBAC could not be completed.",
            BRAND_GOLD,
            styles,
        )
    )
    story.append(Spacer(1, 7 * mm))
    summary_rows = [
        [cell("Risk level", styles["TableHeader"]), cell("Count", styles["TableHeader"]), cell("Disposition", styles["TableHeader"])],
        [cell("High", styles["TableCellBold"]), cell("1", styles["TableCell"]), cell("Open - acceptance condition", styles["TableCell"])],
        [cell("Medium", styles["TableCellBold"]), cell("0", styles["TableCell"]), cell("None verified", styles["TableCell"])],
        [cell("Low", styles["TableCellBold"]), cell("2", styles["TableCell"]), cell("Open / partially mitigated", styles["TableCell"])],
        [cell("Informational", styles["TableCellBold"]), cell("1", styles["TableCell"]), cell("Review / accepted design context", styles["TableCell"])],
        [cell("Operational blocker", styles["TableCellBold"]), cell("1", styles["TableCell"]), cell("LTI invalid_token prevents authenticated app test", styles["TableCell"])],
    ]
    story.append(make_table(summary_rows, [42 * mm, 24 * mm, 108 * mm]))
    story.append(Spacer(1, 6 * mm))
    story.append(p("What is demonstrably improved", styles["H2"]))
    add_dash_items(
        story,
        [
            "Anonymous access to student lists, course rosters, results, responses, student identifiers, student-course mappings, signed URL generation, and local files is blocked with 401/403.",
            "Invalid anonymous writes are stopped by authentication/service-token checks before request validation.",
            "Low-impact SQLi probes produce controlled 401/403 responses without SQL, driver, framework, or stack-trace leakage.",
            "Malformed and alg=none bearer tokens are rejected with 401; invalid service tokens are rejected with 403.",
            "CORS permits the exact Brightspace origin and rejects an untrusted origin without reflecting Access-Control-Allow-Origin.",
            "Public API documentation and common sensitive files are closed; root/static/API error responses carry the core security headers.",
            "Frontend production dependencies, repository secrets, source maps, and the production build passed the current checks.",
        ],
        styles,
    )
    story.append(p("Why this is not a clean pass", styles["H2"]))
    add_dash_items(
        story,
        [
            "Python dependency audits report known advisories affecting authentication, request parsing, availability, and URL/host interpretation.",
            "Brightspace authentication succeeds, but the Virtual Lab launch terminates at /lti-required?error=invalid_token.",
            "A valid application student session and a staff/teacher session were unavailable, so IDOR and course-scope authorization remain partially verified.",
            "Database migration SQL contains pending/commented final constraints and RLS policies that were not independently verified on UAT.",
        ],
        styles,
    )
    story.append(PageBreak())

    story.append(p("2. Scope and Rules of Engagement", styles["H1"]))
    scope_rows = [
        [cell("Item", styles["TableHeader"]), cell("Scope", styles["TableHeader"])],
        [cell("Primary target", styles["TableCellBold"]), cell("https://hvlabonline-uat.singaporetech.edu.sg", styles["TableCell"])],
        [cell("Integration path", styles["TableCellBold"]), cell("Brightspace training course used only to authenticate and launch the authorized LTI integration", styles["TableCell"])],
        [cell("Accounts", styles["TableCellBold"]), cell("Authorized Brightspace training student account; no staff credential was available in this test window", styles["TableCell"])],
        [cell("Assessment window", styles["TableCellBold"]), cell("13 July 2026 IST", styles["TableCell"])],
        [cell("Test mode", styles["TableCellBold"]), cell("Non-destructive, low-rate, UAT-only remediation retest", styles["TableCell"])],
    ]
    story.append(make_table(scope_rows, [45 * mm, 129 * mm]))
    story.append(p("Explicit exclusions", styles["H2"]))
    add_dash_items(
        story,
        [
            "No denial-of-service, resource exhaustion, brute-force, credential stuffing, token spraying, or destructive payloads.",
            "No broad network or port-range scan and no testing of unrelated singaporetech.edu.sg services.",
            "No modification or deletion of client data and no authenticated upload mutation while the LTI session was unavailable.",
            "No claim that the Brightspace platform itself was assessed; it was used only as the approved authentication/launch boundary.",
        ],
        styles,
    )
    story.append(p("Standards and references", styles["H2"]))
    story.append(
        p(
            "The test design was aligned to OWASP Web Security Testing Guide themes, OWASP API Security Top 10 authorization and injection risks, OWASP ASVS session/access-control expectations, and the repository's prior VAPT closure criteria. This interim report records evidence rather than treating scanner silence as proof.",
            styles["Body"],
        )
    )

    story.append(p("3. Methodology and Tooling", styles["H1"]))
    tool_rows = [
        [cell("Tool / technique", styles["TableHeader"]), cell("Use in this assessment", styles["TableHeader"])],
        [cell("Caido 0.57.0", styles["TableCellBold"]), cell("Intercepting proxy and request/response evidence trail", styles["TableCell"])],
        [cell("Custom HVVL retest harness", styles["TableCellBold"]), cell("19 controlled availability, RBAC, auth-gate, and SQLi checks", styles["TableCell"])],
        [cell("Nuclei 3.11.0", styles["TableCellBold"]), cell("11 signed, targeted templates; intrusive/fuzz/DoS/brute-force checks excluded", styles["TableCell"])],
        [cell("curl / OpenSSL", styles["TableCellBold"]), cell("Headers, methods, CORS, JWT rejection, TLS protocol and certificate validation", styles["TableCell"])],
        [cell("npm audit / pip-audit", styles["TableCellBold"]), cell("Production dependency advisory checks", styles["TableCell"])],
        [cell("Gitleaks / Bandit", styles["TableCellBold"]), cell("Repository secret history scan and application-only Python static analysis", styles["TableCell"])],
        [cell("Manual code review", styles["TableCellBold"]), cell("Route dependencies, course/student authorization helpers, parameterized SQL, storage path checks, and migration status", styles["TableCell"])],
    ]
    story.append(make_table(tool_rows, [48 * mm, 126 * mm]))
    story.append(p("Test sequence", styles["H2"]))
    add_dash_items(
        story,
        [
            "Baseline reachability, redirect, TLS, methods, cache, and response-header review.",
            "Anonymous authorization and object-reference probes against sensitive API routes.",
            "Malformed JWT, alg=none token, invalid service token, and CORS origin tests.",
            "Low-impact quote and boolean SQLi probes at representative identifiers and numeric routes.",
            "Targeted exposure/misconfiguration templates and public artifact checks.",
            "Repository dependency, secret, source-map, static-analysis, RBAC, SQL parameterization, and migration review.",
            "Authenticated Brightspace launch attempt and coverage-gap recording.",
        ],
        styles,
    )
    story.append(PageBreak())

    story.append(p("4. Remediation Retest Matrix", styles["H1"]))
    matrix = [
        [cell("Prior recommendation", styles["TableHeader"]), cell("Status", styles["TableHeader"]), cell("Current evidence", styles["TableHeader"])],
        [cell("Frontend dependency closure", styles["TableCellBold"]), cell("Fixed", styles["TableCell"]), cell("npm audit production: 0 vulnerabilities", styles["TableCell"])],
        [cell("Backend dependency closure", styles["TableCellBold"]), cell("Open", styles["TableCell"]), cell("pip-audit reports vulnerable versions across all three Python requirement sets", styles["TableCell"])],
        [cell("Disable public API docs", styles["TableCellBold"]), cell("Fixed", styles["TableCell"]), cell("/docs and /openapi.json return 404; API-prefixed variants also return 404", styles["TableCell"])],
        [cell("Anonymous API authorization", styles["TableCellBold"]), cell("Fixed for tested routes", styles["TableCell"]), cell("Sensitive reads return 401/403; 19/19 direct and Caido checks pass", styles["TableCell"])],
        [cell("Cross-user and cross-course IDOR", styles["TableCellBold"]), cell("Partially verified", styles["TableCell"]), cell("Code has course/student checks; live authenticated matrix blocked by invalid LTI token and absent staff credential", styles["TableCell"])],
        [cell("SQL injection hardening", styles["TableCellBold"]), cell("Partially verified", styles["TableCell"]), cell("Representative anonymous probes blocked cleanly; active queries use positional parameters; authenticated workflow probes pending", styles["TableCell"])],
        [cell("Security headers and CSP", styles["TableCellBold"]), cell("Mostly fixed", styles["TableCell"]), cell("Strict CSP, no unsafe-inline/wildcard, exact frame ancestors, HSTS, nosniff, referrer, permissions, COOP and CORP present", styles["TableCell"])],
        [cell("CORS allowlist", styles["TableCellBold"]), cell("Fixed", styles["TableCell"]), cell("Untrusted preflight rejected; exact Brightspace origin allowed", styles["TableCell"])],
        [cell("Cookie/session closure", styles["TableCellBold"]), cell("Partially verified", styles["TableCell"]), cell("Managed ALB/Cloudflare cookie exceptions remain; application session cookie not observable", styles["TableCell"])],
        [cell("Runtime config exposure", styles["TableCellBold"]), cell("Partially fixed", styles["TableCell"]), cell("Only public config observed, but Cache-Control is public,max-age=30 instead of no-store", styles["TableCell"])],
        [cell("Secrets and build hygiene", styles["TableCellBold"]), cell("Fixed in current evidence", styles["TableCell"]), cell("Gitleaks: 37 commits, 0 leaks; build: 0 source maps", styles["TableCell"])],
        [cell("File and local-storage access", styles["TableCellBold"]), cell("Partially verified", styles["TableCell"]), cell("Anonymous signed URL/local file access blocked; code validates path, extension, and size; authenticated upload pending", styles["TableCell"])],
        [cell("Database constraints and RLS", styles["TableCellBold"]), cell("Not independently verified", styles["TableCell"]), cell("Migration defines structures; final uniqueness/NOT NULL/RLS steps remain conditional/commented", styles["TableCell"])],
    ]
    story.append(make_table(matrix, [55 * mm, 30 * mm, 89 * mm], font_size=7.3))
    story.append(Spacer(1, 6 * mm))
    story.append(
        callout(
            "Retest result",
            "Direct harness: 19 pass, 0 fail, 0 review, 0 inconclusive. Caido-captured harness: 19 pass, 0 fail, 0 review, 0 inconclusive. These counts apply to the safe anonymous and auth-gate suite only; they do not represent full authenticated RBAC coverage.",
            PASS,
            styles,
        )
    )
    story.append(PageBreak())

    story.append(p("5. Detailed Findings", styles["H1"]))
    story.append(
        finding_header(
            "BT-HVVL-2026-001",
            "Known-vulnerable backend dependency versions remain",
            "High",
            "Open",
            HIGH,
            styles,
        )
    )
    story.append(p("Description", styles["H3"]))
    story.append(
        p(
            "Current pip-audit resolution reports known advisories in each Python requirement set. The affected classes include JWT algorithm-policy enforcement, form and multipart parsing, host/path URL interpretation, cryptography, settings source handling, and timing behavior in python-ecdsa. Some advisories have constrained exploit prerequisites, but the repository's own closure standard requires clean backend dependency audits.",
            styles["Body"],
        )
    )
    dep_rows = [
        [cell("Component", styles["TableHeader"]), cell("Current", styles["TableHeader"]), cell("Advisories", styles["TableHeader"]), cell("Fixed version / disposition", styles["TableHeader"])],
        [cell("starlette", styles["TableCellBold"]), cell("0.50.0", styles["TableCell"]), cell("PYSEC-2026-161, PYSEC-2026-248, PYSEC-2026-249, CVE-2026-48817, CVE-2026-48818", styles["TableCell"]), cell("Coordinate FastAPI upgrade for Starlette >= 1.3.1", styles["TableCell"])],
        [cell("python-multipart", styles["TableCellBold"]), cell("0.0.27", styles["TableCell"]), cell("CVE-2026-53538, CVE-2026-53539, CVE-2026-53540", styles["TableCell"]), cell(">= 0.0.31", styles["TableCell"])],
        [cell("PyJWT", styles["TableCellBold"]), cell("2.12.1", styles["TableCell"]), cell("PYSEC-2026-175 through PYSEC-2026-179", styles["TableCell"]), cell(">= 2.13.0", styles["TableCell"])],
        [cell("cryptography", styles["TableCellBold"]), cell("48.0.0", styles["TableCell"]), cell("GHSA-537c-gmf6-5ccf", styles["TableCell"]), cell(">= 48.0.1", styles["TableCell"])],
        [cell("pydantic-settings", styles["TableCellBold"]), cell("2.14.0", styles["TableCell"]), cell("GHSA-4xgf-cpjx-pc3j", styles["TableCell"]), cell(">= 2.14.2", styles["TableCell"])],
        [cell("ecdsa", styles["TableCellBold"]), cell("0.19.2", styles["TableCell"]), cell("PYSEC-2026-1325", styles["TableCell"]), cell("No upstream fix; remove/replace or prove non-signing exposure and risk-accept", styles["TableCell"])],
    ]
    story.append(make_table(dep_rows, [33 * mm, 20 * mm, 72 * mm, 49 * mm], font_size=7.2))
    story.append(p("Evidence", styles["H3"]))
    add_dash_items(
        story,
        [
            "backend-api/requirements.txt: 10 advisory records across 3 packages.",
            "backend-lti/requirements.txt: 19 advisory records across 5 packages.",
            "lti_tool/requirements.txt: 8 advisory records in PyJWT (duplicates reflect audit-source records).",
            "The live malformed and alg=none token tests returned 401, which is a positive control but does not supersede the dependency advisories.",
        ],
        styles,
    )
    story.append(p("Recommendation", styles["H3"]))
    add_dash_items(
        story,
        [
            "Upgrade the FastAPI/Starlette pair as a compatibility-tested unit and pin patched versions.",
            "Upgrade python-multipart, PyJWT, cryptography, and pydantic-settings to at least the listed fixed versions.",
            "Remove python-ecdsa if not required; otherwise document the exact operation and prevent its use for private-key signing/ECDH.",
            "Rebuild all UAT images from clean dependency locks and rerun pip-audit against the deployed lock/image inventory.",
        ],
        styles,
    )
    story.append(Spacer(1, 8 * mm))

    story.append(
        finding_header(
            "BT-HVVL-2026-002",
            "Public runtime configuration is cacheable",
            "Low",
            "Open",
            LOW,
            styles,
        )
    )
    story.append(
        p(
            "The public /env-config.js response contains only client-side configuration in the observed sample, but it is served with Cache-Control: public, max-age=30. The agreed closure criterion calls for no-store so authentication endpoints and environment policy cannot remain stale in shared/intermediate caches.",
            styles["Body"],
        )
    )
    story.append(p("Recommendation", styles["H3"]))
    story.append(p("Serve /env-config.js with Cache-Control: no-store, no-cache, must-revalidate and retain the common security headers.", styles["Body"]))
    story.append(Spacer(1, 8 * mm))

    story.append(
        finding_header(
            "BT-HVVL-2026-003",
            "Managed infrastructure cookies do not meet the full target attribute set",
            "Low",
            "Partially mitigated",
            LOW,
            styles,
        )
    )
    story.append(
        p(
            "AWSALB was observed without Secure, HttpOnly, or SameSite; AWSALBCORS uses SameSite=None; Secure but is not HttpOnly. The Cloudflare bot-management cookie is Secure and HttpOnly but uses SameSite=None and a parent-domain scope. These appear infrastructure-managed, not application session cookies. Their ownership and exceptions still require documented disposition.",
            styles["Body"],
        )
    )
    story.append(p("Recommendation", styles["H3"]))
    story.append(
        p(
            "Confirm cookie ownership with the platform team, configure stronger attributes where supported, and document vendor limitations plus compensating controls. Repeat the review for application-owned cookies after a successful LTI session.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    story.append(
        finding_header(
            "BT-HVVL-2026-004",
            "Optional response headers reported by targeted Nuclei checks",
            "Informational",
            "Review / accepted context",
            INFO,
            styles,
        )
    )
    story.append(
        p(
            "Nuclei reported absent X-Frame-Options, X-Permitted-Cross-Domain-Policies, and Cross-Origin-Embedder-Policy. X-Frame-Options is intentionally superseded by the stricter CSP frame-ancestors directive, which allows only self and the exact Brightspace/UAT origins needed for LTI. The other two headers are legacy/optional hardening controls and may be incompatible with required embedded content if enabled without testing.",
            styles["Body"],
        )
    )
    story.append(p("Recommendation", styles["H3"]))
    story.append(p("Retain CSP frame-ancestors as the authoritative clickjacking control. Add X-Permitted-Cross-Domain-Policies: none if compatible; introduce COEP only after testing all LTI, video, document, and 3D asset flows.", styles["Body"]))
    story.append(PageBreak())

    story.append(p("6. Operational Acceptance Observation", styles["H1"]))
    story.append(
        finding_header(
            "BT-HVVL-OBS-001",
            "Brightspace launch ends with invalid_token",
            "Operational",
            "Open",
            MEDIUM,
            styles,
        )
    )
    story.append(
        p(
            "The authorized training student successfully authenticated to the Brightspace sandbox and opened the VHVL-UAT (SIT) activity. The new application window then navigated to https://hvlabonline-uat.singaporetech.edu.sg/lti-required?error=invalid_token. No authenticated VHVL bearer/session context was established, so the student dashboard and authenticated RBAC workflows could not be exercised.",
            styles["Body"],
        )
    )
    story.append(p("Impact on acceptance", styles["H2"]))
    add_dash_items(
        story,
        [
            "Students cannot reliably reach the client-facing application through the intended launch path.",
            "Authenticated student-vs-student, enrolled-vs-unenrolled course, and upload/submission tests remain blocked.",
            "The issue is treated as an integration/availability blocker, not as evidence of a security bypass.",
        ],
        styles,
    )
    story.append(p("Required next action", styles["H2"]))
    story.append(
        p(
            "Review UAT backend-lti logs and align the LTI issuer, client ID, deployment ID, JWKS URL, redirect URI, Redis state/nonce storage, clock synchronization, and shared backend token settings. After correction, repeat the full launch through Caido and export an authenticated student token only within the approved test process.",
            styles["Body"],
        )
    )

    story.append(p("7. Verified Security Controls", styles["H1"]))
    control_rows = [
        [cell("Control", styles["TableHeader"]), cell("Result", styles["TableHeader"]), cell("Evidence", styles["TableHeader"])],
        [cell("TLS and redirect", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("HTTP 301 to HTTPS; TLS 1.2/1.3; valid certificate through 28 Mar 2027", styles["TableCell"])],
        [cell("Unsafe method", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("TRACE returned 405", styles["TableCell"])],
        [cell("Malformed Host", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Cloudflare returned 400 for malformed Host", styles["TableCell"])],
        [cell("CORS", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Untrusted origin rejected; exact Brightspace origin reflected", styles["TableCell"])],
        [cell("JWT rejection", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Malformed and alg=none tokens returned 401 without stack/error leakage", styles["TableCell"])],
        [cell("Service token", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Invalid service token returned 403 before request processing", styles["TableCell"])],
        [cell("Public API docs", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("/docs and /openapi.json return 404", styles["TableCell"])],
        [cell("Sensitive files", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("/.env and /.git/config return 403; Nuclei found no config exposure", styles["TableCell"])],
        [cell("CSP", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("No wildcard/unsafe-inline; object-src none; exact frame ancestors", styles["TableCell"])],
        [cell("Anonymous RBAC", styles["TableCellBold"]), cell("Pass for tested routes", styles["TableCell"]), cell("Sensitive endpoints consistently return 401/403", styles["TableCell"])],
        [cell("Frontend dependencies", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("npm audit --omit=dev: zero vulnerabilities", styles["TableCell"])],
        [cell("Repository secrets", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Gitleaks: 37 commits, no leaks", styles["TableCell"])],
        [cell("Production source maps", styles["TableCellBold"]), cell("Pass", styles["TableCell"]), cell("Build completed; zero .map files emitted", styles["TableCell"])],
    ]
    story.append(make_table(control_rows, [46 * mm, 34 * mm, 94 * mm], font_size=7.4))
    story.append(PageBreak())

    story.append(p("8. Authenticated RBAC Coverage Gap", styles["H1"]))
    story.append(
        p(
            "The following tests are mandatory before final closure. Their status is Pending, not Failed, because the required application sessions were unavailable during this window.",
            styles["Body"],
        )
    )
    auth_rows = [
        [cell("Required scenario", styles["TableHeader"]), cell("Expected result", styles["TableHeader"]), cell("Current status", styles["TableHeader"])],
        [cell("Student reads own profile/courses/responses", styles["TableCellBold"]), cell("200 for provisioned/enrolled records", styles["TableCell"]), cell("Pending - invalid LTI token", styles["TableCell"])],
        [cell("Student reads another student's records", styles["TableCellBold"]), cell("403", styles["TableCell"]), cell("Pending", styles["TableCell"])],
        [cell("Student accesses unenrolled course", styles["TableCellBold"]), cell("403", styles["TableCell"]), cell("Pending", styles["TableCell"])],
        [cell("Student submits as another student", styles["TableCellBold"]), cell("403", styles["TableCell"]), cell("Pending", styles["TableCell"])],
        [cell("Assigned teacher reads roster/results", styles["TableCellBold"]), cell("200", styles["TableCell"]), cell("Pending - no staff test session", styles["TableCell"])],
        [cell("Teacher reads unassigned course results", styles["TableCellBold"]), cell("403", styles["TableCell"]), cell("Pending", styles["TableCell"])],
        [cell("Course admin opens and manages course", styles["TableCellBold"]), cell("200 for approved admin; role visible in /auth/me", styles["TableCell"]), cell("Pending", styles["TableCell"])],
        [cell("Expired/tampered authenticated token", styles["TableCellBold"]), cell("401 and session cleared", styles["TableCell"]), cell("Malformed anonymous token check passed; real-session variant pending", styles["TableCell"])],
    ]
    story.append(make_table(auth_rows, [73 * mm, 49 * mm, 52 * mm], font_size=7.4))
    story.append(Spacer(1, 7 * mm))
    story.append(
        callout(
            "Final RBAC closure rule",
            "Do not convert these Pending scenarios to Pass from code review alone. Capture request/response evidence using two authorized student identities and assigned/unassigned staff contexts after the LTI/AD launch paths are working.",
            BRAND_BLUE,
            styles,
        )
    )

    story.append(p("9. Database and SQL Injection Review", styles["H1"]))
    story.append(p("Application query construction", styles["H2"]))
    story.append(
        p(
            "The active asyncpg CRUD and RBAC queries reviewed use positional parameters ($1, $2, and so on). A targeted search did not find f-string or .format construction passed into execute/fetch/fetchrow/fetchval. The five live quote/boolean probes returned controlled authorization responses without database errors.",
            styles["Body"],
        )
    )
    story.append(p("Database enforcement status", styles["H2"]))
    db_rows = [
        [cell("Control", styles["TableHeader"]), cell("Repository status", styles["TableHeader"]), cell("UAT verification", styles["TableHeader"])],
        [cell("Canonical users/roles/identities", styles["TableCellBold"]), cell("Defined in additive migration", styles["TableCell"]), cell("Not directly verified", styles["TableCell"])],
        [cell("course_staff", styles["TableCellBold"]), cell("Defined and backfilled from legacy instructor mapping", styles["TableCell"]), cell("Application currently also uses legacy course instructor mapping; live state unknown", styles["TableCell"])],
        [cell("Enrollment uniqueness/NOT NULL", styles["TableCellBold"]), cell("Preflight present; final statements commented pending cleanup", styles["TableCell"]), cell("Not verified", styles["TableCell"])],
        [cell("Student-response uniqueness/NOT NULL", styles["TableCellBold"]), cell("Preflight present; final statements commented pending cleanup", styles["TableCell"]), cell("Not verified", styles["TableCell"])],
        [cell("PostgreSQL RLS", styles["TableCellBold"]), cell("Policy examples present but enable/create statements commented", styles["TableCell"]), cell("Not verified / should be treated as not enabled until proven", styles["TableCell"])],
        [cell("Runtime DB grants", styles["TableCellBold"]), cell("Example grants present", styles["TableCell"]), cell("Not verified", styles["TableCell"])],
    ]
    story.append(make_table(db_rows, [49 * mm, 63 * mm, 62 * mm], font_size=7.4))
    story.append(
        p(
            "Conclusion: application-layer SQLi resistance and anonymous auth gating are materially improved. Full database hardening closure requires a deployment-side migration transcript and read-only catalog evidence for constraints, policies, and grants.",
            styles["Body"],
        )
    )
    story.append(PageBreak())

    story.append(p("10. Remediation Plan and Exit Criteria", styles["H1"]))
    plan_rows = [
        [cell("Priority", styles["TableHeader"]), cell("Action", styles["TableHeader"]), cell("Owner", styles["TableHeader"]), cell("Closure evidence", styles["TableHeader"])],
        [cell("P0", styles["TableCellBold"]), cell("Upgrade vulnerable Python dependencies and rebuild UAT images", styles["TableCell"]), cell("Application team", styles["TableCell"]), cell("Clean pip-audit outputs and image/package inventory", styles["TableCell"])],
        [cell("P0", styles["TableCellBold"]), cell("Fix Brightspace LTI invalid_token launch", styles["TableCell"]), cell("Application + LMS team", styles["TableCell"]), cell("Successful Caido-captured LTI launch and /auth/me for student", styles["TableCell"])],
        [cell("P0", styles["TableCellBold"]), cell("Run full authenticated RBAC/IDOR matrix", styles["TableCell"]), cell("Security + app team", styles["TableCell"]), cell("Student A/B and assigned/unassigned staff evidence", styles["TableCell"])],
        [cell("P1", styles["TableCellBold"]), cell("Set env-config cache policy to no-store", styles["TableCell"]), cell("Frontend/DevOps", styles["TableCell"]), cell("Response headers from deployed UAT", styles["TableCell"])],
        [cell("P1", styles["TableCellBold"]), cell("Document or improve managed-cookie attributes", styles["TableCell"]), cell("Cloud/platform team", styles["TableCell"]), cell("Cookie ownership and approved exception/compensating control", styles["TableCell"])],
        [cell("P1", styles["TableCellBold"]), cell("Apply/verify final DB constraints, RLS, and grants", styles["TableCell"]), cell("Database owner", styles["TableCell"]), cell("Migration output and pg_catalog extracts", styles["TableCell"])],
        [cell("P2", styles["TableCellBold"]), cell("Add optional legacy headers if compatible", styles["TableCell"]), cell("DevOps", styles["TableCell"]), cell("Header matrix and regression check", styles["TableCell"])],
        [cell("P2", styles["TableCellBold"]), cell("Add timeouts to legacy requests.get JWKS helpers or remove dead helpers", styles["TableCell"]), cell("Backend team", styles["TableCell"]), cell("Bandit triage and focused tests", styles["TableCell"])],
    ]
    story.append(make_table(plan_rows, [16 * mm, 70 * mm, 39 * mm, 49 * mm], font_size=7.2))
    story.append(p("Final report exit criteria", styles["H2"]))
    add_dash_items(
        story,
        [
            "Zero open critical/high findings, or formally approved risk acceptance with compensating controls.",
            "Clean production frontend and backend dependency audits.",
            "Successful Brightspace and staff login flows with authenticated role evidence.",
            "All cross-user/cross-course RBAC scenarios pass with 401/403/200 behavior as designed.",
            "Runtime config, managed cookies, database controls, and authenticated uploads have closure evidence.",
            "A focused retest confirms no regression in the 19 currently passing anonymous/auth-gate checks.",
        ],
        styles,
    )

    story.append(p("11. Evidence Appendix", styles["H1"]))
    story.append(p("A. Direct and Caido retest cases", styles["H2"]))
    results = load_retest_results()
    result_rows = [
        [cell("Case", styles["TableHeader"]), cell("HTTP", styles["TableHeader"]), cell("Verdict", styles["TableHeader"]), cell("Reason", styles["TableHeader"])],
    ]
    for result in results:
        result_rows.append(
            [
                cell(result["title"], styles["TableCell"]),
                cell(str(result["status"]), styles["TableCell"]),
                cell(result["verdict"].upper(), styles["TableCellBold"]),
                cell(result["reason"], styles["TableCell"]),
            ]
        )
    story.append(make_table(result_rows, [76 * mm, 18 * mm, 23 * mm, 57 * mm], font_size=6.9))
    story.append(Spacer(1, 5 * mm))
    story.append(p("The same request set was replayed through Caido and produced the same 19 pass / 0 fail result.", styles["BodySmall"]))

    story.append(p("B. Targeted Nuclei and TLS evidence", styles["H2"]))
    nuclei_rows = [
        [cell("Item", styles["TableHeader"]), cell("Observed result", styles["TableHeader"])],
        [cell("Targeted templates", styles["TableCellBold"]), cell("11 signed templates; 111 requests completed; intrusive/DoS/fuzz/brute-force excluded", styles["TableCell"])],
        [cell("Matches", styles["TableCellBold"]), cell("TLS 1.2, TLS 1.3, Cloudflare, and three informational missing-header checks", styles["TableCell"])],
        [cell("No match", styles["TableCellBold"]), cell("CORS misconfiguration, directory listing, git config, JS runtime secrets, OpenAPI/Swagger exposure, weak cipher, expired certificate", styles["TableCell"])],
        [cell("Certificate", styles["TableCellBold"]), cell("CN=*.singaporetech.edu.sg; Sectigo OV issuer; valid 25 Feb 2026 to 28 Mar 2027; verification OK", styles["TableCell"])],
        [cell("Negotiated sample", styles["TableCellBold"]), cell("TLS 1.3 / TLS_AES_256_GCM_SHA384", styles["TableCell"])],
    ]
    story.append(make_table(nuclei_rows, [45 * mm, 129 * mm]))

    story.append(p("C. Code and supply-chain evidence", styles["H2"]))
    code_rows = [
        [cell("Check", styles["TableHeader"]), cell("Result", styles["TableHeader"])],
        [cell("npm audit --omit=dev", styles["TableCellBold"]), cell("0 total vulnerabilities", styles["TableCell"])],
        [cell("pip-audit", styles["TableCellBold"]), cell("Failed closure criterion: known advisories in all three requirement sets", styles["TableCell"])],
        [cell("Gitleaks", styles["TableCellBold"]), cell("37 commits scanned; no leaks found", styles["TableCell"])],
        [cell("Bandit application-only", styles["TableCellBold"]), cell("0 high; 3 medium heuristics (two requests without timeout, one expected container bind to 0.0.0.0)", styles["TableCell"])],
        [cell("Frontend build", styles["TableCellBold"]), cell("Pass; zero production source maps", styles["TableCell"])],
        [cell("SQL construction review", styles["TableCellBold"]), cell("Active asyncpg paths use positional parameters; no f-string/.format query execution match", styles["TableCell"])],
    ]
    story.append(make_table(code_rows, [54 * mm, 120 * mm]))

    screenshot = EVIDENCE_DIR / "vapt-20260713-browser" / "caido-http-history.png"
    if screenshot.exists():
        story.append(PageBreak())
        story.append(p("D. Caido proxy evidence", styles["H2"]))
        story.append(Image(str(screenshot), width=174 * mm, height=96 * mm))
        story.append(p("Caido HTTP history showing the controlled RBAC/auth-gate/SQLi request set and 401/403 responses.", styles["Caption"]))

    story.append(p("12. Limitations and Statement of Use", styles["H1"]))
    add_dash_items(
        story,
        [
            "This is an interim assessment based on the UAT state observed during the stated window.",
            "A security test is sample-based and cannot prove the absence of every vulnerability.",
            "Authenticated application testing was constrained by the invalid LTI token outcome and lack of a staff test session.",
            "No production environment, unrelated SIT systems, denial-of-service, social engineering, or destructive testing was performed.",
            "Database-level controls were reviewed from migration/code artifacts but not verified through direct UAT database access.",
            "The report supports controlled UAT/cloud acceptance planning; it is not a final certificate of security.",
        ],
        styles,
    )
    story.append(Spacer(1, 10 * mm))
    story.append(
        callout(
            "Recommended decision",
            "Proceed with controlled UAT acceptance while treating BT-HVVL-2026-001 and BT-HVVL-OBS-001 as release-blocking conditions for final security closure. Schedule a focused authenticated retest immediately after dependency and LTI remediation.",
            BRAND_BLUE,
            styles,
        )
    )
    story.append(Spacer(1, 15 * mm))
    sign_rows = [
        [cell("Prepared by", styles["TableHeader"]), cell("Assessment reference", styles["TableHeader"])],
        [cell("BlueTeamer<br/>https://blueteamer.co", styles["TableCellBold"]), cell("BT-VAPT-HVVL-UAT-20260713-INT-01<br/>Interim 1.0", styles["TableCell"])],
    ]
    story.append(make_table(sign_rows, [87 * mm, 87 * mm]))
    return story


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    styles = build_styles()
    MD_PATH.write_text(build_markdown(), encoding="utf-8")
    doc = ReportDoc(str(PDF_PATH), styles)
    doc.multiBuild(build_story(styles), canvasmaker=CalibriCanvas)
    print(PDF_PATH)
    print(MD_PATH)


if __name__ == "__main__":
    main()
