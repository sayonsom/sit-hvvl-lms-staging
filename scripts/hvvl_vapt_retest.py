#!/usr/bin/env python3
"""Safe HVVL LMS RBAC/SQLi retest runner.

The script is designed for authorized UAT testing. By default it performs only
read-only requests and saves response evidence for report updates.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


SQL_ERROR_RE = re.compile(
    r"(sqlstate|syntax error at or near|unterminated quoted string|"
    r"asyncpg|psycopg|postgres|odbc|database error|stack trace|traceback)",
    re.IGNORECASE,
)
XSS_EXECUTABLE_RE = re.compile(
    r"(<(?:script|svg)\b[^>]{0,300}bt-xss|"
    r"\bon(?:error|load|click)\s*=[^>]{0,300}bt-xss|"
    r"javascript\s*:[^\s<]{0,300}bt-xss)",
    re.IGNORECASE,
)

UNAVAILABLE_STATUSES = {0, 502, 503, 504}
AUTH_BLOCK_STATUSES = {401, 403}
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


@dataclasses.dataclass(frozen=True)
class Profile:
    name: str
    headers: dict[str, str]


@dataclasses.dataclass(frozen=True)
class Case:
    case_id: str
    title: str
    method: str
    url: str
    expectation: str
    body: bytes | None = None
    headers: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Result:
    case_id: str
    profile: str
    title: str
    url: str
    method: str
    expectation: str
    status: int
    verdict: str
    reason: str
    elapsed_ms: int
    header_file: str
    body_file: str


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run safe HVVL LMS UAT RBAC/SQLi retest probes and save evidence."
    )
    parser.add_argument(
        "--api-base",
        default=os.getenv(
            "HVVL_API_BASE",
            "https://hvlabonline-uat.singaporetech.edu.sg/api/v1",
        ),
        help="Backend API v1 base URL.",
    )
    parser.add_argument(
        "--uat-url",
        default=os.getenv(
            "HVVL_UAT_URL", "https://hvlabonline-uat.singaporetech.edu.sg/"
        ),
        help="HVVL UAT frontend URL.",
    )
    parser.add_argument(
        "--brightspace-url",
        default=os.getenv(
            "HVVL_BRIGHTSPACE_URL",
            "https://xsitestg.singaporetech.edu.sg/d2l/home/6874",
        ),
        help="Brightspace course URL used only for availability checks.",
    )
    parser.add_argument(
        "--proxy",
        default=os.getenv("HVVL_PROXY", ""),
        help="Optional HTTP proxy, for example http://127.0.0.1:8081 for Caido.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification. Use only with an authorized intercepting proxy.",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Evidence directory. Defaults to output/evidence/retest-<timestamp>.",
    )
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--pause", type=float, default=0.25, help="Delay between probes.")
    parser.add_argument(
        "--include-auth-gate-posts",
        action="store_true",
        help="Also send invalid-body POST requests that should be blocked before validation.",
    )
    return parser.parse_args()


def clean_base(url: str) -> str:
    return url.rstrip("/")


def quote_path(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def env_value(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value if value is not None and value != "" else default


def build_profiles() -> list[Profile]:
    profiles = [Profile("anonymous", {})]
    for name in ("student", "teacher"):
        headers: dict[str, str] = {}
        auth = env_value(f"HVVL_{name.upper()}_AUTHORIZATION")
        bearer = env_value(f"HVVL_{name.upper()}_BEARER_TOKEN")
        cookie = env_value(f"HVVL_{name.upper()}_COOKIE")
        if auth:
            headers["Authorization"] = auth
        elif bearer:
            headers["Authorization"] = f"Bearer {bearer}"
        if cookie:
            headers["Cookie"] = cookie
        if headers:
            profiles.append(Profile(name, headers))
    return profiles


def build_cases(args: argparse.Namespace) -> list[Case]:
    api = clean_base(args.api_base)
    uat = args.uat_url
    brightspace = args.brightspace_url
    course_id = env_value("HVVL_COURSE_ID", "1")
    other_course_id = env_value("HVVL_OTHER_COURSE_ID", "2")
    student_id = env_value("HVVL_STUDENT_ID", "1")
    student_email = env_value("HVVL_STUDENT_EMAIL", "vhvl_stud01")
    module_id = env_value("HVVL_MODULE_ID")
    xss_payload = "<svg/onload=alert('bt-xss')>"

    cases = [
        Case("avail-uat-root", "UAT frontend availability", "GET", uat, "availability"),
        Case(
            "avail-api-courses",
            "Backend API availability",
            "GET",
            f"{api}/courses",
            "availability_or_auth_gate",
        ),
        Case(
            "avail-brightspace-course",
            "Brightspace course availability",
            "GET",
            brightspace,
            "availability",
        ),
        Case(
            "rbac-anon-courses",
            "Anonymous course catalogue read",
            "GET",
            f"{api}/courses",
            "public_or_authenticated",
        ),
        Case(
            "rbac-anon-all-students",
            "Anonymous all-students read",
            "GET",
            f"{api}/students/",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-course-students",
            "Anonymous course roster read",
            "GET",
            f"{api}/courses/{quote_path(course_id)}/students",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-course-results",
            "Anonymous course-wide results read",
            "GET",
            f"{api}/courses/{quote_path(course_id)}/student-results",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-other-course-results",
            "Anonymous alternate course results read",
            "GET",
            f"{api}/courses/{quote_path(other_course_id)}/student-results",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-student-responses",
            "Anonymous student response read",
            "GET",
            f"{api}/students/{quote_path(student_id)}/assignments/responses",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-student-id-lookup",
            "Anonymous student ID lookup by identifier",
            "GET",
            f"{api}/student-id/{quote_path(student_email)}",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-student-courses",
            "Anonymous student courses read",
            "GET",
            f"{api}/students/{quote_path(student_email)}/courses",
            "sensitive_read_blocked",
        ),
        Case(
            "rbac-anon-signed-url",
            "Anonymous file signed URL generation",
            "GET",
            f"{api}/generate-signed-url/?blob_name={quote_path('content_files/test.txt')}",
            "sensitive_read_blocked",
        ),
        Case(
            "sqli-student-id-quote",
            "SQLi probe: student-id single quote",
            "GET",
            f"{api}/student-id/{quote_path(student_email + chr(39))}",
            "sqli_no_db_error",
        ),
        Case(
            "sqli-student-id-bool",
            "SQLi probe: student-id boolean expression",
            "GET",
            f"{api}/student-id/{quote_path(student_email + chr(39) + ' OR ' + chr(39) + '1' + chr(39) + '=' + chr(39) + '1')}",
            "sqli_no_db_error",
        ),
        Case(
            "sqli-student-courses-quote",
            "SQLi probe: student courses single quote",
            "GET",
            f"{api}/students/{quote_path(student_email + chr(39))}/courses",
            "sqli_no_db_error",
        ),
        Case(
            "sqli-course-results-quote",
            "SQLi probe: numeric course_id quote",
            "GET",
            f"{api}/courses/{quote_path(course_id + chr(39))}/student-results",
            "sqli_no_db_error",
        ),
        Case(
            "sqli-student-responses-quote",
            "SQLi probe: numeric student_id quote",
            "GET",
            f"{api}/students/{quote_path(student_id + chr(39))}/assignments/responses",
            "sqli_no_db_error",
        ),
        Case(
            "xss-student-id-reflection",
            "XSS probe: student identifier SVG event handler",
            "GET",
            f"{api}/student-id/{quote_path(xss_payload)}",
            "xss_no_executable_reflection",
        ),
        Case(
            "xss-student-courses-reflection",
            "XSS probe: student courses identifier script context",
            "GET",
            f"{api}/students/{quote_path(xss_payload)}/courses",
            "xss_no_executable_reflection",
        ),
    ]

    if module_id:
        cases.extend(
            [
                Case(
                    "rbac-anon-module-read",
                    "Anonymous module read",
                    "GET",
                    f"{api}/modules/{quote_path(module_id)}",
                    "sensitive_read_blocked",
                ),
                Case(
                    "rbac-anon-module-assignments",
                    "Anonymous module assignments read",
                    "GET",
                    f"{api}/modules/{quote_path(module_id)}/assignments",
                    "sensitive_read_blocked",
                ),
            ]
        )

    if args.include_auth_gate_posts:
        json_headers = {"Content-Type": "application/json"}
        cases.extend(
            [
                Case(
                    "gate-post-course-invalid",
                    "Invalid anonymous course create should be auth-blocked before validation",
                    "POST",
                    f"{api}/courses/",
                    "auth_gate_before_validation",
                    body=b"{}",
                    headers=json_headers,
                ),
                Case(
                    "gate-post-student-invalid",
                    "Invalid anonymous student create should be auth-blocked before validation",
                    "POST",
                    f"{api}/students/",
                    "auth_gate_before_validation",
                    body=b"{}",
                    headers=json_headers,
                ),
            ]
        )

    return cases


def build_opener(proxy: str, insecure: bool) -> urllib.request.OpenerDirector:
    ssl_context = (
        ssl._create_unverified_context() if insecure else ssl.create_default_context()
    )
    handlers: list[urllib.request.BaseHandler] = [
        urllib.request.HTTPSHandler(context=ssl_context),
        NoRedirect,
    ]
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener(*handlers)


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")[:120] or "case"


def response_headers_text(headers: Iterable[tuple[str, str]]) -> str:
    return "".join(f"{k}: {v}\n" for k, v in headers)


def run_case(
    opener: urllib.request.OpenerDirector,
    profile: Profile,
    case: Case,
    out_dir: Path,
    timeout: float,
) -> Result:
    headers = {
        "User-Agent": "HVVL-LMS-authorized-VAPT-retest/2026-06-09",
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    }
    headers.update(profile.headers)
    headers.update(case.headers)

    req = urllib.request.Request(
        case.url,
        data=case.body,
        headers=headers,
        method=case.method,
    )

    status = 0
    raw_headers = ""
    body = b""
    started = time.monotonic()
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.getcode()
            raw_headers = f"HTTP {status}\n" + response_headers_text(resp.headers.items())
            body = resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw_headers = f"HTTP {status}\n" + response_headers_text(exc.headers.items())
        body = exc.read()
    except Exception as exc:  # noqa: BLE001 - evidence needs transport errors too.
        raw_headers = f"TRANSPORT_ERROR: {type(exc).__name__}: {exc}\n"
        body = b""
    elapsed_ms = int((time.monotonic() - started) * 1000)

    stem = safe_slug(f"{profile.name}-{case.case_id}")
    header_file = out_dir / f"{stem}.headers"
    body_file = out_dir / f"{stem}.body"
    header_file.write_text(raw_headers, encoding="utf-8")
    body_file.write_bytes(body)

    verdict, reason = classify(case.expectation, status, body, raw_headers)
    return Result(
        case_id=case.case_id,
        profile=profile.name,
        title=case.title,
        url=case.url,
        method=case.method,
        expectation=case.expectation,
        status=status,
        verdict=verdict,
        reason=reason,
        elapsed_ms=elapsed_ms,
        header_file=str(header_file),
        body_file=str(body_file),
    )


def classify(expectation: str, status: int, body: bytes, headers: str) -> tuple[str, str]:
    text = (headers + "\n").encode("utf-8", "ignore") + body[:4096]
    decoded = text.decode("utf-8", "ignore")

    if status in UNAVAILABLE_STATUSES:
        return "inconclusive", f"target unavailable or transport failed with status {status}"

    if expectation == "availability":
        if 200 <= status < 400:
            return "pass", f"target reachable with status {status}"
        return "fail", f"availability check returned status {status}"

    if expectation == "availability_or_auth_gate":
        if 200 <= status < 400 or status in AUTH_BLOCK_STATUSES:
            return "pass", f"target reachable with status {status}"
        return "fail", f"availability check returned status {status}"

    if expectation == "public_or_authenticated":
        if status in AUTH_BLOCK_STATUSES or status in REDIRECT_STATUSES or 200 <= status < 300:
            return "pass", f"course catalogue returned acceptable status {status}"
        return "review", f"unexpected status {status} for course catalogue"

    if expectation == "sensitive_read_blocked":
        if status in AUTH_BLOCK_STATUSES:
            return "pass", f"sensitive endpoint blocked with status {status}"
        if status in REDIRECT_STATUSES:
            return "pass", f"sensitive endpoint redirected before data access with status {status}"
        if 200 <= status < 300:
            return "fail", f"sensitive endpoint returned success status {status}"
        if status == 404:
            return "review", "endpoint returned 404; confirm this is not identifier-dependent"
        return "review", f"sensitive endpoint returned status {status}; confirm auth gate behavior"

    if expectation == "auth_gate_before_validation":
        if status in AUTH_BLOCK_STATUSES or status in REDIRECT_STATUSES:
            return "pass", f"write endpoint auth-blocked with status {status}"
        if status == 422:
            return "fail", "request reached validation before authentication"
        if 200 <= status < 300:
            return "fail", f"invalid write request returned success status {status}"
        return "review", f"write auth-gate probe returned status {status}"

    if expectation == "sqli_no_db_error":
        if SQL_ERROR_RE.search(decoded):
            return "fail", "response contains database/framework error text"
        if status >= 500:
            return "review", f"server error {status}; triage for SQLi/error handling"
        return "pass", f"no SQL/database error indicator observed with status {status}"

    if expectation == "xss_no_executable_reflection":
        if XSS_EXECUTABLE_RE.search(decoded):
            return "fail", "response reflects executable HTML or an event-handler payload"
        if status in AUTH_BLOCK_STATUSES and "cloudflare" in decoded.lower():
            return "pass", f"payload blocked at the edge with status {status}; marker not reflected"
        if status >= 500:
            return "review", f"server error {status}; triage XSS/error handling"
        return "pass", f"no executable payload reflection observed with status {status}"

    return "review", f"unknown expectation {expectation}"


def write_summary(out_dir: Path, args: argparse.Namespace, results: list[Result]) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.verdict] = counts.get(result.verdict, 0) + 1

    summary = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "api_base": args.api_base,
        "uat_url": args.uat_url,
        "brightspace_url": args.brightspace_url,
        "proxy": args.proxy or None,
        "insecure_tls": args.insecure,
        "counts": counts,
        "results": [dataclasses.asdict(result) for result in results],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    lines = [
        "# HVVL LMS VAPT Retest Summary",
        "",
        f"Generated: {summary['generated_at']}",
        f"API base: `{args.api_base}`",
        f"UAT URL: `{args.uat_url}`",
        f"Proxy: `{args.proxy or 'none'}`",
        f"Insecure TLS: `{args.insecure}`",
        "",
        "| Verdict | Count |",
        "| --- | ---: |",
    ]
    for verdict in ("fail", "review", "inconclusive", "pass"):
        lines.append(f"| {verdict} | {counts.get(verdict, 0)} |")
    lines.extend(
        [
            "",
            "| Profile | Case | Status | Verdict | Reason |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for result in results:
        reason = result.reason.replace("|", "\\|")
        title = result.title.replace("|", "\\|")
        lines.append(
            f"| {result.profile} | {title} | {result.status} | {result.verdict} | {reason} |"
        )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out or f"output/evidence/retest-{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    opener = build_opener(args.proxy, args.insecure)
    profiles = build_profiles()
    cases = build_cases(args)

    results: list[Result] = []
    for profile in profiles:
        for case in cases:
            results.append(run_case(opener, profile, case, out_dir, args.timeout))
            time.sleep(args.pause)

    write_summary(out_dir, args, results)
    counts: dict[str, int] = {}
    for result in results:
        counts[result.verdict] = counts.get(result.verdict, 0) + 1

    print(f"Evidence written to {out_dir}")
    print(
        "Verdicts: "
        + ", ".join(f"{k}={counts.get(k, 0)}" for k in ("fail", "review", "inconclusive", "pass"))
    )
    return 1 if counts.get("fail", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
