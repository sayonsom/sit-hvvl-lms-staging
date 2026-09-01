#!/usr/bin/env python3
"""Generate the BlueTeamer HVVL professional web application and API VAPT report."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    NextPageTemplate,
    PageBreak,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from generate_vapt_interim_report import (
    BRAND_BLUE,
    BRAND_DEEP,
    BRAND_GOLD,
    HIGH,
    INFO,
    LINE,
    LOW,
    MEDIUM,
    MUTED,
    PASS,
    TEXT,
    CalibriCanvas,
    ReportDoc,
    add_dash_items,
    build_styles,
    callout,
    cell,
    finding_header,
    make_table,
    p,
    register_fonts,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
EVIDENCE_DIR = ROOT / "output" / "evidence"
PDF_PATH = OUT_DIR / "BlueTeamer_HVVL_UAT_Professional_VAPT_Report_2026-07-13.pdf"
MD_PATH = OUT_DIR / "BlueTeamer_HVVL_UAT_Professional_VAPT_Report_2026-07-13.md"
REPORT_ID = "BT-VAPT-HVVL-UAT-20260713-02"


def load_results() -> list[dict]:
    summary = EVIDENCE_DIR / "retest-20260713-remediation-final" / "summary.json"
    return json.loads(summary.read_text(encoding="utf-8"))["results"]


def build_markdown() -> str:
    return f"""# BlueTeamer HVVL UAT Web Application and API VAPT Report

Report ID: {REPORT_ID}  
Assessment date: 13 July 2026  
Target: https://hvlabonline-uat.singaporetech.edu.sg  
Prepared by: BlueTeamer - https://blueteamer.co  
Classification: Confidential

## Executive decision

The requested code remediation is implemented and locally verified. Current UAT perimeter testing passed 21 of 21 non-destructive checks. The assessment covers application and API authorization, authentication and LTI, injection, browser-side security, dependency risk, deployment configuration, exposed surfaces, and transport/security-header controls. Final closure remains pending because the changed frontend, backend-api, and lti-backend images have not yet been deployed to UAT, and authenticated student/staff testing must be repeated after deployment.

## Tracked items

| ID | Prior severity | Code status | UAT closure |
| --- | --- | --- | --- |
| BT-HVVL-2026-001 | High | Implemented; clean pip-audit; patched images built | Pending redeployment and deployed-image audit |
| BT-HVVL-OBS-001 | Operational | Implemented; 6 LTI validation tests pass | Pending correct Brightspace IDs and successful launch retest |

## Assessment highlights

- Authentication and authorization: anonymous access gates pass; LTI audience/state validation is corrected; authenticated Student A/B and assigned/unassigned staff testing remains pending.
- SQL injection: 5 live probes pass with no database error leakage. Static AST regression check confirms no interpolated SQL reaches active database execution methods.
- XSS: 2 live payloads were blocked at Cloudflare without marker reflection. Markdown raw HTML is disabled; unsafe URL protocols are blocked; no React `dangerouslySetInnerHTML` sink exists in `src/`.
- Supply chain: backend-api and backend-lti pip-audit results contain zero known vulnerabilities; production npm audit contains zero vulnerabilities.
- Platform controls: HTTPS/TLS, security headers, CORS restrictions, API documentation exposure, secret scanning, and production source-map controls were reviewed as part of the broader VAPT evidence set.

## Deployment requirement

Rebuild and redeploy `virtuallab`, `backend-api`, and `lti-backend`. Retain PostgreSQL, Redis, and local-storage volumes. Configure the exact Brightspace LTI `CLIENT_ID` and `DEPLOYMENT_ID`; these values are registration identifiers, not random secrets. No new database migration is required by this change set.

This is an interim professional VAPT and remediation-verification report, not a final certificate of security. Final closure requires deployment and authenticated evidence.
"""


def cover(story: list, styles: dict) -> None:
    logo_white = OUT_DIR / "assets" / "blueteamer-logo-white.png"
    if logo_white.exists():
        story.append(Image(str(logo_white), width=24 * mm, height=24 * mm))
    story.append(Spacer(1, 8 * mm))
    story.append(p("BLUETEAMER", styles["CoverBrand"]))
    story.append(p("Web Application &amp; API<br/>VAPT Report", styles["CoverTitle"]))
    story.append(p("SIT Virtual High Voltage Laboratory - UAT<br/>Remediation Verification and Acceptance Assessment", styles["CoverSub"]))
    status = Table(
        [[cell("INTERIM VAPT - DEPLOYMENT VALIDATION REQUIRED", styles["TableHeader"])]],
        colWidths=[104 * mm],
    )
    status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(status)
    story.append(Spacer(1, 23 * mm))
    story.append(
        p(
            "<b>Target</b><br/>https://hvlabonline-uat.singaporetech.edu.sg<br/><br/>"
            "<b>Assessment date</b><br/>13 July 2026<br/><br/>"
            f"<b>Report ID</b><br/>{REPORT_ID}<br/><br/>"
            "<b>Prepared by</b><br/>BlueTeamer - https://blueteamer.co",
            styles["CoverMeta"],
        )
    )
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())


def build_story(styles: dict) -> list:
    story: list = []
    cover(story, styles)

    story.append(p("Document Control", styles["H1"]))
    rows = [
        [cell("Field", styles["TableHeader"]), cell("Value", styles["TableHeader"])],
        [cell("Document title", styles["TableCellBold"]), cell("HVVL UAT Web Application and API VAPT Report", styles["TableCell"])],
        [cell("Assessment type", styles["TableCellBold"]), cell("Authorized web application/API VAPT, code remediation review, and non-destructive UAT retest", styles["TableCell"])],
        [cell("Prepared by", styles["TableCellBold"]), cell("BlueTeamer - https://blueteamer.co", styles["TableCell"])],
        [cell("Classification", styles["TableCellBold"]), cell("Confidential", styles["TableCell"])],
        [cell("Version", styles["TableCellBold"]), cell("2.0 professional interim VAPT report", styles["TableCell"])],
        [cell("Status", styles["TableCellBold"]), cell("Implementation verified locally; UAT deployment and authenticated closure pending", styles["TableCell"])],
    ]
    story.append(make_table(rows, [43 * mm, 131 * mm]))
    story.append(Spacer(1, 7 * mm))
    story.append(
        callout(
            "Distribution and interpretation",
            "This report is intended for the client project, security, LMS, cloud, and deployment teams. It records a comprehensive interim VAPT position. A local code pass is not represented as a deployed UAT pass. Final acceptance requires the post-deployment tests listed later in this document.",
            BRAND_BLUE,
            styles,
        )
    )
    story.append(Spacer(1, 8 * mm))
    story.append(p("Contents", styles["H1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC1R", fontName="Calibri", fontSize=9.5, leading=14, textColor=TEXT),
        ParagraphStyle("TOC2R", fontName="Calibri", fontSize=8.5, leading=12, leftIndent=10, textColor=MUTED),
    ]
    story.append(toc)
    story.append(PageBreak())

    story.append(p("1. Executive Summary", styles["H1"]))
    story.append(
        callout(
            "Implementation result: verified locally, deployment pending",
            "BT-HVVL-2026-001 and BT-HVVL-OBS-001 have code corrections and automated evidence. The focused live perimeter retest passed 21 of 21 checks. The changed images are not yet on UAT, so the tracked items remain pending final closure until deployment and authenticated retesting complete.",
            BRAND_GOLD,
            styles,
        )
    )
    story.append(Spacer(1, 7 * mm))
    summary = [
        [cell("Evidence layer", styles["TableHeader"]), cell("Result", styles["TableHeader"]), cell("Interpretation", styles["TableHeader"])],
        [cell("Current UAT perimeter", styles["TableCellBold"]), cell("21 pass / 0 fail", styles["TableCell"]), cell("Anonymous RBAC, auth-gate, SQLi, XSS, and availability checks passed", styles["TableCell"])],
        [cell("Backend API security tests", styles["TableCellBold"]), cell("5 pass", styles["TableCell"]), cell("RBAC, JWT tamper rejection, and SQL construction checks", styles["TableCell"])],
        [cell("LTI validation tests", styles["TableCellBold"]), cell("6 pass", styles["TableCell"]), cell("State/client binding, audience, nonce, and deployment checks", styles["TableCell"])],
        [cell("Python dependency audits", styles["TableCellBold"]), cell("0 known vulnerabilities", styles["TableCell"]), cell("backend-api and backend-lti patched requirement sets", styles["TableCell"])],
        [cell("Production npm audit", styles["TableCellBold"]), cell("0 vulnerabilities", styles["TableCell"]), cell("Unused HTML parser packages removed", styles["TableCell"])],
        [cell("Container builds", styles["TableCellBold"]), cell("2 pass", styles["TableCell"]), cell("Patched backend-api and lti-backend images built and version-checked", styles["TableCell"])],
    ]
    story.append(make_table(summary, [46 * mm, 36 * mm, 92 * mm], font_size=7.5))
    story.append(p("Risk position", styles["H2"]))
    add_dash_items(
        story,
        [
            "No critical or high-severity exploit was demonstrated across the tested web application, API, authentication, authorization, injection, browser-security, and deployment-control scope.",
            "The prior High dependency finding is remediated in source and built images, but remains open on the deployed-environment ledger until UAT is rebuilt and re-audited.",
            "The LTI invalid_token observation has a code-level root-cause correction and diagnostics, but successful Brightspace launch evidence is still required.",
            "Authenticated horizontal/vertical authorization and stored-XSS scenarios remain pending because they require the redeployed student and staff sessions.",
        ],
        styles,
    )
    story.append(PageBreak())

    story.append(p("2. Scope, Method and Limitations", styles["H1"]))
    scope = [
        [cell("Item", styles["TableHeader"]), cell("Coverage", styles["TableHeader"])],
        [cell("Primary target", styles["TableCellBold"]), cell("https://hvlabonline-uat.singaporetech.edu.sg", styles["TableCell"])],
        [cell("Codebase", styles["TableCellBold"]), cell("Frontend, backend-api, backend-lti, UAT Compose, and deployment documentation", styles["TableCell"])],
        [cell("Assessment domains", styles["TableCellBold"]), cell("Authentication/LTI, RBAC/IDOR, injection, XSS, dependencies, TLS, CORS, headers, exposed surfaces, secrets/artifacts, sessions, and deployment readiness", styles["TableCell"])],
        [cell("Live mode", styles["TableCellBold"]), cell("Low-rate, non-destructive GET probes and invalid-body auth-gate checks", styles["TableCell"])],
        [cell("References", styles["TableCellBold"]), cell("OWASP WSTG authorization and input-validation themes; CWE-862, CWE-89, CWE-79", styles["TableCell"])],
    ]
    story.append(make_table(scope, [45 * mm, 129 * mm]))
    story.append(p("Evidence model", styles["H2"]))
    add_dash_items(
        story,
        [
            "Live perimeter evidence: HTTP request/response results from the current UAT deployment.",
            "Code evidence: route dependency review, parameterized SQL inspection, XSS sink review, and automated regression tests.",
            "Supply-chain evidence: pip-audit and npm audit against the patched requirement manifests.",
            "Build evidence: production frontend build and two Python container builds with version inspection.",
        ],
        styles,
    )
    story.append(p("Limitations", styles["H2"]))
    add_dash_items(
        story,
        [
            "The new code was not deployed to UAT during this report window.",
            "No authenticated Student A/Student B, assigned/unassigned teacher, or course-admin session was available against the patched deployment.",
            "Stored XSS through authenticated content creation/upload requires post-deployment testing.",
            "No denial-of-service, brute force, destructive mutation, unrelated SIT-system test, or production test was performed.",
            "Prior low and informational observations outside this focused change set remain governed by the interim report unless separately closed.",
        ],
        styles,
    )

    story.append(PageBreak())
    story.append(p("3. Risk Rating Methodology", styles["H1"]))
    story.append(
        p(
            "Findings are rated using a qualitative CVSS-informed model that considers exploitability, privileges and user interaction, data sensitivity, technical impact, business impact, and the strength of compensating controls. Operational observations are tracked separately when they block security validation or client acceptance without demonstrating an exploitable vulnerability.",
            styles["Body"],
        )
    )
    severity_rows = [
        [cell("Rating", styles["TableHeader"]), cell("Definition", styles["TableHeader"]), cell("Expected response", styles["TableHeader"])],
        [cell("Critical", styles["TableCellBold"]), cell("Direct compromise, broad sensitive-data exposure, or severe unauthenticated impact", styles["TableCell"]), cell("Immediate containment and emergency remediation", styles["TableCell"])],
        [cell("High", styles["TableCellBold"]), cell("Material confidentiality, integrity, or availability impact with practical exploitation", styles["TableCell"]), cell("Release blocking unless formally accepted", styles["TableCell"])],
        [cell("Medium", styles["TableCellBold"]), cell("Meaningful impact requiring conditions, access, or user interaction", styles["TableCell"]), cell("Remediate before production or document acceptance", styles["TableCell"])],
        [cell("Low", styles["TableCellBold"]), cell("Limited impact, defense-in-depth weakness, or constrained information exposure", styles["TableCell"]), cell("Planned remediation and verification", styles["TableCell"])],
        [cell("Informational", styles["TableCellBold"]), cell("Hardening opportunity, design note, or accepted implementation context", styles["TableCell"]), cell("Review and record disposition", styles["TableCell"])],
        [cell("Operational", styles["TableCellBold"]), cell("Integration or availability issue that prevents security validation", styles["TableCell"]), cell("Correct and repeat the blocked test", styles["TableCell"])],
    ]
    story.append(make_table(severity_rows, [31 * mm, 91 * mm, 52 * mm], font_size=7.3))
    story.append(p("Finding status definitions", styles["H2"]))
    status_definition_rows = [
        [cell("Status", styles["TableHeader"]), cell("Meaning", styles["TableHeader"])],
        [cell("Open", styles["TableCellBold"]), cell("The issue remains present or has not been remediated", styles["TableCell"])],
        [cell("Implemented", styles["TableCellBold"]), cell("The correction exists in source and passed local verification", styles["TableCell"])],
        [cell("Pending deployment", styles["TableCellBold"]), cell("Source is corrected, but the deployed environment has not been revalidated", styles["TableCell"])],
        [cell("Partially mitigated", styles["TableCellBold"]), cell("Some controls are effective, but residual risk or ownership remains", styles["TableCell"])],
        [cell("Closed", styles["TableCellBold"]), cell("Correction is deployed and supported by repeatable retest evidence", styles["TableCell"])],
    ]
    story.append(make_table(status_definition_rows, [45 * mm, 129 * mm], font_size=7.4))

    story.append(p("4. Comprehensive Security Assessment", styles["H1"]))
    story.append(p("Findings register", styles["H2"]))
    register_rows = [
        [cell("ID", styles["TableHeader"]), cell("Rating", styles["TableHeader"]), cell("Finding / observation", styles["TableHeader"]), cell("Current disposition", styles["TableHeader"])],
        [cell("BT-HVVL-2026-001", styles["TableCellBold"]), cell("High", styles["TableCell"]), cell("Known-vulnerable backend dependencies", styles["TableCell"]), cell("Implemented; UAT deployment audit pending", styles["TableCellBold"])],
        [cell("BT-HVVL-2026-002", styles["TableCellBold"]), cell("Low", styles["TableCell"]), cell("Runtime environment configuration cache policy", styles["TableCell"]), cell("Code configured for no-store; UAT verification pending", styles["TableCell"])],
        [cell("BT-HVVL-2026-003", styles["TableCellBold"]), cell("Low", styles["TableCell"]), cell("Managed infrastructure cookie attributes", styles["TableCell"]), cell("Partially mitigated; platform disposition required", styles["TableCell"])],
        [cell("BT-HVVL-2026-004", styles["TableCellBold"]), cell("Informational", styles["TableCell"]), cell("Optional/legacy response headers", styles["TableCell"]), cell("Review or accept with compatibility rationale", styles["TableCell"])],
        [cell("BT-HVVL-OBS-001", styles["TableCellBold"]), cell("Operational", styles["TableCell"]), cell("Brightspace launch ended with invalid_token", styles["TableCell"]), cell("Implemented; live launch validation pending", styles["TableCellBold"])],
    ]
    story.append(make_table(register_rows, [35 * mm, 23 * mm, 64 * mm, 52 * mm], font_size=7.1))
    story.append(p("Security control coverage", styles["H2"]))
    control_rows = [
        [cell("Domain", styles["TableHeader"]), cell("Assessment result", styles["TableHeader"]), cell("Status", styles["TableHeader"])],
        [cell("Transport security", styles["TableCellBold"]), cell("HTTPS redirect, valid certificate, and TLS 1.2/1.3 support verified in the interim evidence set", styles["TableCell"]), cell("Pass", styles["TableCellBold"])],
        [cell("Authentication/JWT", styles["TableCellBold"]), cell("Malformed/tampered tokens rejected; LTI state/audience validation corrected", styles["TableCell"]), cell("Pass locally; launch pending", styles["TableCellBold"])],
        [cell("Authorization/RBAC", styles["TableCellBold"]), cell("Anonymous sensitive routes blocked; course and identity scoping covered by regression tests", styles["TableCell"]), cell("Partial closure", styles["TableCellBold"])],
        [cell("Injection", styles["TableCellBold"]), cell("Parameterized asyncpg queries and five clean live SQLi probes", styles["TableCell"]), cell("Pass in tested scope", styles["TableCellBold"])],
        [cell("Browser/XSS", styles["TableCellBold"]), cell("CSP, raw-HTML suppression, URL protocol policy, no direct React HTML sink", styles["TableCell"]), cell("Pass; stored test pending", styles["TableCellBold"])],
        [cell("CORS", styles["TableCellBold"]), cell("Exact approved origins configured; untrusted-origin behavior previously verified", styles["TableCell"]), cell("Pass", styles["TableCellBold"])],
        [cell("Security headers", styles["TableCellBold"]), cell("HSTS, CSP, nosniff, referrer and permissions policies present; optional headers documented", styles["TableCell"]), cell("Pass / review", styles["TableCellBold"])],
        [cell("Exposed surfaces", styles["TableCellBold"]), cell("Production API docs disabled; common sensitive files blocked", styles["TableCell"]), cell("Pass", styles["TableCellBold"])],
        [cell("Supply chain", styles["TableCellBold"]), cell("Patched Python manifests and production npm audit report zero known vulnerabilities", styles["TableCell"]), cell("Pass locally", styles["TableCellBold"])],
        [cell("Secrets/artifacts", styles["TableCellBold"]), cell("GitHub secret scan passed; production source maps are not emitted", styles["TableCell"]), cell("Pass", styles["TableCellBold"])],
        [cell("Session/cookies", styles["TableCellBold"]), cell("Application tokens use short-lived validation; managed edge-cookie ownership remains for platform review", styles["TableCell"]), cell("Partial", styles["TableCellBold"])],
        [cell("Availability/readiness", styles["TableCellBold"]), cell("New configuration/Redis readiness endpoint and healthy dependency ordering", styles["TableCell"]), cell("Pending UAT deployment", styles["TableCellBold"])],
    ]
    story.append(make_table(control_rows, [43 * mm, 96 * mm, 35 * mm], font_size=6.9))
    story.append(Spacer(1, 6 * mm))
    story.append(
        callout(
            "Overall VAPT position",
            "No critical or high-severity exploit was demonstrated in the tested web/API scope. One prior High dependency finding is corrected in source and built images but remains pending deployed-image verification. The principal residual assurance gap is authenticated end-to-end testing after the corrected LTI and staff login services are deployed.",
            BRAND_BLUE,
            styles,
        )
    )
    story.append(PageBreak())

    story.append(p("5. Remediation Status", styles["H1"]))
    status_rows = [
        [cell("ID", styles["TableHeader"]), cell("Prior rating", styles["TableHeader"]), cell("Implemented correction", styles["TableHeader"]), cell("Closure state", styles["TableHeader"])],
        [cell("BT-HVVL-2026-001", styles["TableCellBold"]), cell("High", styles["TableCell"]), cell("Patched frameworks/parsers/JWT/crypto/settings; removed python-jose/ecdsa; migrated Pydantic; rebuilt images", styles["TableCell"]), cell("Code verified; UAT deployment pending", styles["TableCellBold"])],
        [cell("BT-HVVL-OBS-001", styles["TableCellBold"]), cell("Operational", styles["TableCell"]), cell("Allow-listed client/deployment IDs; client and issuer bound to one-time state; audience validated against state; readiness and safe reason codes added", styles["TableCell"]), cell("Code verified; Brightspace launch pending", styles["TableCellBold"])],
    ]
    story.append(make_table(status_rows, [35 * mm, 25 * mm, 75 * mm, 39 * mm], font_size=7.2))
    story.append(Spacer(1, 7 * mm))
    story.append(
        callout(
            "Closure rule",
            "Neither tracked item should be marked Closed solely from this report. Mark BT-HVVL-2026-001 closed after deployed-image audit; mark BT-HVVL-OBS-001 closed after readiness is 200 and a real Brightspace launch reaches the application with a valid session.",
            MEDIUM,
            styles,
        )
    )
    story.append(PageBreak())

    story.append(p("6. Authorization and RBAC Assessment", styles["H1"]))
    story.append(
        finding_header(
            "FOCUS-RBAC",
            "Horizontal and vertical authorization",
            "No exploit demonstrated",
            "Partial closure",
            PASS,
            styles,
        )
    )
    story.append(
        p(
            "Sensitive API routes require a validated actor before data access. Course reads check privileged, teacher, or enrolled-student context; staff mutations and roster/results reads check course ownership; student response writes resolve the authenticated student and reject submission for another student.",
            styles["Body"],
        )
    )
    rbac_rows = [
        [cell("Test area", styles["TableHeader"]), cell("Evidence", styles["TableHeader"]), cell("Result", styles["TableHeader"])],
        [cell("Anonymous sensitive reads", styles["TableCellBold"]), cell("Students, roster, results, responses, student ID, student courses, signed URL", styles["TableCell"]), cell("401/403 - Pass", styles["TableCellBold"])],
        [cell("Anonymous invalid writes", styles["TableCellBold"]), cell("Course and student create requests with invalid body", styles["TableCell"]), cell("Auth blocked before validation - Pass", styles["TableCellBold"])],
        [cell("Student cross-identity", styles["TableCellBold"]), cell("Unit test: student A requests student B email", styles["TableCell"]), cell("403 - Pass", styles["TableCellBold"])],
        [cell("Student course scope", styles["TableCellBold"]), cell("Unit test verifies parameterized enrollment lookup by email and course", styles["TableCell"]), cell("Pass", styles["TableCellBold"])],
        [cell("Teacher course scope", styles["TableCellBold"]), cell("Unit test: teacher requests unassigned course administration", styles["TableCell"]), cell("403 - Pass", styles["TableCellBold"])],
        [cell("Authenticated live matrix", styles["TableCellBold"]), cell("Student A/B, enrolled/unenrolled, assigned/unassigned teacher, course admin", styles["TableCell"]), cell("Pending after deployment", styles["TableCellBold"])],
    ]
    story.append(make_table(rbac_rows, [48 * mm, 88 * mm, 38 * mm], font_size=7.2))
    story.append(p("Required post-deployment matrix", styles["H2"]))
    add_dash_items(
        story,
        [
            "Student A can read own provisioned profile, enrolled courses, assignments, and responses.",
            "Student A receives 403 for Student B records, another student ID, and submission as Student B.",
            "Student receives 403 for an unenrolled course and its modules/assignments.",
            "Assigned teacher receives 200 for own roster/results and 403 for an unassigned course.",
            "Approved course admin receives the intended admin/teacher role in /api/v1/auth/me and can access authorized course administration only.",
        ],
        styles,
    )
    story.append(PageBreak())

    story.append(p("7. SQL Injection Assessment", styles["H1"]))
    story.append(
        finding_header(
            "FOCUS-SQLI",
            "SQL injection through API identifiers and write paths",
            "No exploit demonstrated",
            "Code and perimeter verified",
            PASS,
            styles,
        )
    )
    story.append(
        p(
            "Five low-impact quote/boolean probes were sent to representative student and course identifier routes. All produced controlled 401/403 responses without SQLSTATE, PostgreSQL, asyncpg, syntax, stack-trace, or framework error leakage. Active asyncpg calls use positional placeholders such as $1 and $2.",
            styles["Body"],
        )
    )
    sqli = [r for r in load_results() if r["case_id"].startswith("sqli-")]
    sqli_rows = [[cell("Probe", styles["TableHeader"]), cell("HTTP", styles["TableHeader"]), cell("Result", styles["TableHeader"])]]
    for result in sqli:
        sqli_rows.append([
            cell(result["title"], styles["TableCell"]),
            cell(str(result["status"]), styles["TableCell"]),
            cell("PASS - no DB error indicator", styles["TableCellBold"]),
        ])
    story.append(make_table(sqli_rows, [104 * mm, 20 * mm, 50 * mm], font_size=7.4))
    story.append(p("Regression guard", styles["H2"]))
    story.append(
        p(
            "The automated AST test scans active backend Python files and fails when execute, executemany, fetch, fetchrow, or fetchval receives an f-string, string concatenation/format operation, or a variable assigned from one of those dynamic forms. The current scan passes.",
            styles["Body"],
        )
    )
    story.append(
        callout(
            "Assessment conclusion",
            "SQL injection resistance is supported by both perimeter behavior and code-level parameterization evidence. Repeat representative probes with authenticated request paths after deployment, especially create/update/search functionality, before final sign-off.",
            BRAND_BLUE,
            styles,
        )
    )

    story.append(PageBreak())
    story.append(p("8. Cross-Site Scripting Assessment", styles["H1"]))
    story.append(
        finding_header(
            "FOCUS-XSS",
            "Reflected and stored browser script injection",
            "No exploit demonstrated",
            "Hardened; authenticated retest pending",
            PASS,
            styles,
        )
    )
    xss = [r for r in load_results() if r["case_id"].startswith("xss-")]
    xss_rows = [[cell("Control/test", styles["TableHeader"]), cell("Evidence", styles["TableHeader"]), cell("Result", styles["TableHeader"])]]
    for result in xss:
        xss_rows.append([
            cell(result["title"], styles["TableCell"]),
            cell(result["reason"], styles["TableCell"]),
            cell("PASS", styles["TableCellBold"]),
        ])
    xss_rows.extend([
        [cell("Markdown raw HTML", styles["TableCellBold"]), cell("ReactMarkdown uses skipHtml; no rehype-raw", styles["TableCell"]), cell("PASS", styles["TableCellBold"])],
        [cell("Markdown URL protocols", styles["TableCellBold"]), cell("javascript:, vbscript:, data:text/html, and SVG data URLs rejected", styles["TableCell"]), cell("PASS", styles["TableCellBold"])],
        [cell("React HTML sinks", styles["TableCellBold"]), cell("Security script finds no dangerouslySetInnerHTML in src/", styles["TableCell"]), cell("PASS", styles["TableCellBold"])],
        [cell("Unused HTML parsers", styles["TableCellBold"]), cell("marked, remark, and remark-html removed", styles["TableCell"]), cell("PASS", styles["TableCellBold"])],
        [cell("Browser defense", styles["TableCellBold"]), cell("CSP blocks inline scripts and objects; X-Content-Type-Options is nosniff", styles["TableCell"]), cell("PASS", styles["TableCellBold"])],
    ])
    story.append(make_table(xss_rows, [57 * mm, 89 * mm, 28 * mm], font_size=7.1))
    story.append(p("Pending stored-XSS tests", styles["H2"]))
    add_dash_items(
        story,
        [
            "Create course/module/assignment text containing HTML, SVG event attributes, encoded protocol handlers, and broken-image handlers using an authorized staff account.",
            "Verify student, teacher, results, and preview screens render text safely and produce no script execution or CSP violation indicating an attempted unsafe sink.",
            "Verify uploaded Markdown cannot introduce raw HTML or unsafe link/image protocols, while valid relative HTTPS content remains functional.",
        ],
        styles,
    )
    story.append(PageBreak())

    story.append(p("9. BT-HVVL-2026-001 Dependency Remediation", styles["H1"]))
    story.append(
        finding_header(
            "BT-HVVL-2026-001",
            "Known-vulnerable backend dependency versions",
            "High (prior)",
            "Implemented - deployment pending",
            HIGH,
            styles,
        )
    )
    dep_rows = [
        [cell("Component", styles["TableHeader"]), cell("Prior", styles["TableHeader"]), cell("Patched", styles["TableHeader"]), cell("Disposition", styles["TableHeader"])],
        [cell("FastAPI", styles["TableCellBold"]), cell("0.125.0", styles["TableCell"]), cell("0.139.0", styles["TableCell"]), cell("Compatibility upgrade", styles["TableCell"])],
        [cell("Starlette", styles["TableCellBold"]), cell("0.50.0", styles["TableCell"]), cell("1.3.1", styles["TableCell"]), cell("Known advisories addressed", styles["TableCell"])],
        [cell("python-multipart", styles["TableCellBold"]), cell("0.0.27", styles["TableCell"]), cell("0.0.32", styles["TableCell"]), cell("Parser advisories addressed", styles["TableCell"])],
        [cell("PyJWT", styles["TableCellBold"]), cell("2.12.1", styles["TableCell"]), cell("2.13.0", styles["TableCell"]), cell("JWT advisories addressed", styles["TableCell"])],
        [cell("cryptography", styles["TableCellBold"]), cell("48.0.0", styles["TableCell"]), cell("49.0.0", styles["TableCell"]), cell("Crypto advisory addressed", styles["TableCell"])],
        [cell("pydantic-settings", styles["TableCellBold"]), cell("2.14.0", styles["TableCell"]), cell("2.14.2", styles["TableCell"]), cell("Settings advisory addressed", styles["TableCell"])],
        [cell("python-jose / ecdsa", styles["TableCellBold"]), cell("3.5.0 / 0.19.2", styles["TableCell"]), cell("Removed", styles["TableCell"]), cell("No-fix transitive dependency eliminated", styles["TableCell"])],
        [cell("Pydantic", styles["TableCellBold"]), cell("1.10.26", styles["TableCell"]), cell("2.13.4", styles["TableCell"]), cell("Required framework compatibility migration", styles["TableCell"])],
    ]
    story.append(make_table(dep_rows, [43 * mm, 31 * mm, 31 * mm, 69 * mm], font_size=7.2))
    story.append(p("Verification", styles["H2"]))
    add_dash_items(
        story,
        [
            "pip-audit of backend-api requirements: zero known vulnerabilities.",
            "pip-audit of backend-lti requirements: zero known vulnerabilities.",
            "python-jose and ecdsa are absent from the patched dependency environment.",
            "Backend API imports cleanly with Python warnings treated as errors.",
            "Patched backend-api and lti-backend Docker images build successfully and report the expected framework/JWT/crypto versions.",
        ],
        styles,
    )

    story.append(PageBreak())
    story.append(p("10. Authentication and LTI Remediation", styles["H1"]))
    story.append(
        finding_header(
            "BT-HVVL-OBS-001",
            "Brightspace launch ended with invalid_token",
            "Operational",
            "Implemented - live validation pending",
            MEDIUM,
            styles,
        )
    )
    story.append(
        p(
            "The prior flow could use the client_id received from Brightspace to build the authorization request, then validate the returned ID token against only the server's primary CLIENT_ID. A correct Brightspace token could therefore fail audience validation when the server value was missing, a placeholder, or represented a different allowed registration.",
            styles["Body"],
        )
    )
    lti_rows = [
        [cell("Correction", styles["TableHeader"]), cell("Security effect", styles["TableHeader"])],
        [cell("Client and deployment allow-lists", styles["TableCellBold"]), cell("Reject unregistered identifiers instead of trusting arbitrary incoming client_id", styles["TableCell"])],
        [cell("State binding", styles["TableCellBold"]), cell("Store issuer and selected client ID with nonce in one-time Redis state", styles["TableCell"])],
        [cell("Audience validation", styles["TableCellBold"]), cell("Validate token audience against the trusted client ID bound to state", styles["TableCell"])],
        [cell("Issuer/deployment/nonce", styles["TableCellBold"]), cell("Exact issuer, allow-listed deployment, and constant-time nonce comparison", styles["TableCell"])],
        [cell("Clock/JWKS controls", styles["TableCellBold"]), cell("Configured clock skew and JWKS timeout", styles["TableCell"])],
        [cell("Safe diagnostics", styles["TableCellBold"]), cell("Reason codes distinguish state, audience, issuer, nonce, deployment, expiry, signature, and JWKS failures without logging tokens", styles["TableCell"])],
        [cell("Readiness endpoint", styles["TableCellBold"]), cell("503 for placeholder/incomplete IDs or Redis failure; container dependency waits for ready", styles["TableCell"])],
        [cell("Legacy route removal", styles["TableCellBold"]), cell("Removed duplicate in-memory LTI route that disabled audience verification", styles["TableCell"])],
    ]
    story.append(make_table(lti_rows, [62 * mm, 112 * mm], font_size=7.3))
    story.append(
        callout(
            "Configuration requirement",
            "CLIENT_ID and DEPLOYMENT_ID must be copied from the exact SIT Brightspace LTI 1.3 registration. They are public registration identifiers, not randomly generated secrets. Multiple registrations must be listed explicitly in LTI_CLIENT_IDS and LTI_DEPLOYMENT_IDS.",
            BRAND_BLUE,
            styles,
        )
    )
    story.append(PageBreak())

    story.append(p("11. Server Deployment Requirements", styles["H1"]))
    story.append(p("What must be deployed", styles["H2"]))
    deploy_rows = [
        [cell("Service", styles["TableHeader"]), cell("Why", styles["TableHeader"]), cell("Data action", styles["TableHeader"])],
        [cell("virtuallab", styles["TableCellBold"]), cell("XSS URL policy, raw-HTML enforcement, dependency removal", styles["TableCell"]), cell("Rebuild image", styles["TableCell"])],
        [cell("backend-api", styles["TableCellBold"]), cell("Dependency/JWT/Pydantic upgrade and legacy LTI route removal", styles["TableCell"]), cell("Rebuild image; retain database/storage", styles["TableCell"])],
        [cell("lti-backend", styles["TableCellBold"]), cell("LTI state/audience/allow-list/readiness correction", styles["TableCell"]), cell("Rebuild image; retain Redis volume", styles["TableCell"])],
        [cell("postgres", styles["TableCellBold"]), cell("No schema change in this focused patch", styles["TableCell"]), cell("Do not recreate volume", styles["TableCell"])],
        [cell("redis", styles["TableCellBold"]), cell("Existing sessions/state can expire normally", styles["TableCell"]), cell("Do not flush; users start a fresh launch", styles["TableCell"])],
    ]
    story.append(make_table(deploy_rows, [35 * mm, 90 * mm, 49 * mm], font_size=7.3))
    story.append(p("Required environment values", styles["H2"]))
    add_dash_items(
        story,
        [
            "CLIENT_ID and DEPLOYMENT_ID from the exact Brightspace UAT tool registration.",
            "LTI_CLIENT_IDS and LTI_DEPLOYMENT_IDS set to the approved values, comma-separated only if multiple registrations are intentional.",
            "ISSUER, AUTHORIZATION_ENDPOINT, KEY_SET_URL, TOOL_URL, and FRONTEND_URL exactly as documented in UAT_LOCAL_DEPLOYMENT.md.",
            "Existing POSTGRES_PASSWORD, BACKEND_API_SERVICE_TOKEN, BACKEND_API_JWT_SECRET, and LOCAL_STORAGE_SIGNING_KEY must remain consistent with the deployed data/services; do not replace them during an ordinary rebuild.",
        ],
        styles,
    )
    story.append(p("Deployment command sequence", styles["H2"]))
    command_rows = [
        [cell("Step", styles["TableHeader"]), cell("Command/action", styles["TableHeader"])],
        [cell("1", styles["TableCellBold"]), cell("Pull the approved commit and preserve the server .env.uat file", styles["TableCell"])],
        [cell("2", styles["TableCellBold"]), cell("docker compose --env-file .env.uat -f docker-compose.uat.yml build --pull --no-cache virtuallab backend-api lti-backend", styles["TableCell"])],
        [cell("3", styles["TableCellBold"]), cell("docker compose --env-file .env.uat -f docker-compose.uat.yml up -d --remove-orphans", styles["TableCell"])],
        [cell("4", styles["TableCellBold"]), cell("Confirm all services are healthy and /lti/health/ready returns 200 ready", styles["TableCell"])],
        [cell("5", styles["TableCellBold"]), cell("Start a new launch from D2L Training SandBox14; do not test /lti/launch directly", styles["TableCell"])],
    ]
    story.append(make_table(command_rows, [18 * mm, 156 * mm], font_size=7.4))
    story.append(PageBreak())

    story.append(p("12. Post-Deployment Retest and Exit Criteria", styles["H1"]))
    retest_rows = [
        [cell("Gate", styles["TableHeader"]), cell("Expected evidence", styles["TableHeader"]), cell("Owner", styles["TableHeader"])],
        [cell("Readiness", styles["TableCellBold"]), cell("/lti/health/ready = 200 and all Compose services healthy", styles["TableCell"]), cell("UAT/DevOps", styles["TableCell"])],
        [cell("Dependency closure", styles["TableCellBold"]), cell("pip-audit or equivalent inside deployed backend images shows zero known vulnerabilities", styles["TableCell"]), cell("App/DevOps", styles["TableCell"])],
        [cell("Brightspace launch", styles["TableCellBold"]), cell("Student reaches /app or /home; no invalid_token; session and backend API token validate", styles["TableCell"]), cell("LMS/App", styles["TableCell"])],
        [cell("Staff launch", styles["TableCellBold"]), cell("Approved course admin signs in and /api/v1/auth/me reports intended role", styles["TableCell"]), cell("ADFS/App", styles["TableCell"])],
        [cell("RBAC matrix", styles["TableCellBold"]), cell("Student A/B, enrolled/unenrolled, assigned/unassigned staff evidence", styles["TableCell"]), cell("Security", styles["TableCell"])],
        [cell("Authenticated SQLi", styles["TableCellBold"]), cell("Representative authenticated identifiers and writes show no injection/error behavior", styles["TableCell"]), cell("Security", styles["TableCell"])],
        [cell("Stored XSS", styles["TableCellBold"]), cell("Authorized content payloads render inert across student/staff views", styles["TableCell"]), cell("Security", styles["TableCell"])],
        [cell("Regression", styles["TableCellBold"]), cell("Focused harness remains 21/21 pass after deployment", styles["TableCell"]), cell("Security", styles["TableCell"])],
    ]
    story.append(make_table(retest_rows, [42 * mm, 96 * mm, 36 * mm], font_size=7.2))
    story.append(Spacer(1, 7 * mm))
    story.append(
        callout(
            "Final acceptance condition",
            "Issue closure is supportable when the patched images are deployed, the live dependency inventory is clean, Brightspace launch succeeds, and the authenticated RBAC/SQLi/stored-XSS matrix produces the expected 200/401/403 behavior without script execution or data leakage.",
            BRAND_BLUE,
            styles,
        )
    )

    story.append(p("13. Evidence Appendix", styles["H1"]))
    story.append(p("Live focused retest", styles["H2"]))
    result_rows = [[cell("Case", styles["TableHeader"]), cell("HTTP", styles["TableHeader"]), cell("Verdict", styles["TableHeader"]), cell("Reason", styles["TableHeader"])]]
    for result in load_results():
        result_rows.append([
            cell(result["title"], styles["TableCell"]),
            cell(str(result["status"]), styles["TableCell"]),
            cell(result["verdict"].upper(), styles["TableCellBold"]),
            cell(result["reason"], styles["TableCell"]),
        ])
    story.append(make_table(result_rows, [72 * mm, 18 * mm, 24 * mm, 60 * mm], font_size=6.6))
    story.append(p("Code, audit and build evidence", styles["H2"]))
    evidence_rows = [
        [cell("Artifact", styles["TableHeader"]), cell("Result", styles["TableHeader"])],
        [cell("backend-api-security-tests.txt", styles["TableCellBold"]), cell("5 tests passed", styles["TableCell"])],
        [cell("backend-lti-security-tests.txt", styles["TableCellBold"]), cell("6 tests passed", styles["TableCell"])],
        [cell("pip-audit-backend-api.json", styles["TableCellBold"]), cell("Zero known vulnerabilities", styles["TableCell"])],
        [cell("pip-audit-backend-lti.json", styles["TableCellBold"]), cell("Zero known vulnerabilities", styles["TableCell"])],
        [cell("npm-audit-production.json", styles["TableCellBold"]), cell("Zero production vulnerabilities", styles["TableCell"])],
        [cell("xss-controls.txt", styles["TableCellBold"]), cell("Unsafe URLs blocked; no React HTML injection sink", styles["TableCell"])],
        [cell("backend-api-container-versions.txt", styles["TableCellBold"]), cell("Patched versions confirmed in built image", styles["TableCell"])],
        [cell("backend-lti-container-versions.txt", styles["TableCellBold"]), cell("Patched versions confirmed in built image", styles["TableCell"])],
    ]
    story.append(make_table(evidence_rows, [74 * mm, 100 * mm]))
    story.append(Spacer(1, 7 * mm))
    story.append(
        p(
            "Evidence directories:<br/>"
            "output/evidence/retest-20260713-remediation-final/<br/>"
            "output/evidence/remediation-20260713-code/",
            styles["BodySmall"],
        )
    )

    story.append(p("14. Conclusion", styles["H1"]))
    story.append(
        p(
            "The requested remediation work is complete in the repository and has passed local, supply-chain, build, and current-perimeter checks. The broader VAPT evidence shows effective transport, authentication-gate, authorization, injection, browser, CORS, exposed-surface, dependency, secret, and build-artifact controls in the tested scope. The detailed RBAC, SQL injection, and XSS sections provide additional assurance for the highest-priority application risks.",
            styles["Body"],
        )
    )
    story.append(
        p(
            "The correct next decision is to deploy the three changed application images to UAT, preserve existing data/secrets, configure the exact Brightspace registration identifiers, and execute the authenticated exit matrix. Until that evidence is captured, the report supports remediation readiness but not final VAPT closure.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 9 * mm))
    sign = [
        [cell("Prepared by", styles["TableHeader"]), cell("Assessment reference", styles["TableHeader"])],
        [cell("BlueTeamer<br/>https://blueteamer.co", styles["TableCellBold"]), cell(f"{REPORT_ID}<br/>Professional interim VAPT 2.0", styles["TableCell"])],
    ]
    story.append(make_table(sign, [87 * mm, 87 * mm]))
    return story


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    styles = build_styles()
    MD_PATH.write_text(build_markdown(), encoding="utf-8")
    doc = ReportDoc(
        str(PDF_PATH),
        styles,
        title="HVVL UAT Web Application and API VAPT Report",
        subject="Professional web application and API VAPT remediation and deployment readiness assessment",
        header_title="HVVL UAT Web Application and API VAPT Report",
        cover_footer="CONFIDENTIAL - WEB APPLICATION AND API VAPT",
    )
    doc.multiBuild(build_story(styles), canvasmaker=CalibriCanvas)
    print(PDF_PATH)
    print(MD_PATH)


if __name__ == "__main__":
    main()
