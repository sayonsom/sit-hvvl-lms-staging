# VAPT Remediation Guide

This guide is the engineering checklist for closing the current VAPT findings for the SIT Virtual HV Lab application and keeping the repository certification-ready after remediation.

Current evidence source:

- Harness run: `/Users/sayon/Documents/Codes/Frontend/blueteamer-vapt-harness/runs/sit-uat-active-20260508-zap-fixed-deduped`
- Current deduped result: 24 findings
- Severity summary: 1 critical, 1 high, 9 medium, 13 low
- Main risk classes: vulnerable dependencies, weak/missing security headers, exposed API docs, third-party script integrity, managed-cookie posture, public runtime config, and information disclosure.

## Closure Standard

A finding is closed only when all of these are true:

1. The code or platform configuration has been changed.
2. The change is covered by a local test, CI check, or repeatable manual verification step.
3. The same harness profile no longer reports the finding, or the finding is explicitly triaged as `false_positive` or `risk_accepted` with a written reason.
4. The final report contains before and after evidence.
5. No critical or high finding remains open.

Do not treat scanner silence as proof by itself. For each fix, keep the exact command output, HTTP response header evidence, package audit output, and deployment version used for retest.

## Priority Order

Remediate in this order:

1. Critical and high dependency findings.
2. Public production debug or API-documentation exposure.
3. Authentication and authorization enforcement.
4. Browser security headers and CSP.
5. Cookie and session hardening.
6. Information disclosure and runtime configuration exposure.
7. Low-risk hygiene findings and documented managed-service exceptions.

## 1. Dependency and Vulnerable JS Library Closure

Findings covered:

- `DEP-001`: Vulnerable JavaScript dependencies.
- `ZAP-001`: Vulnerable deployed JavaScript library.

### Required Changes

1. Replace Create React App/react-scripts as the production build tool.
   - `react-scripts@5.0.1` commonly pins vulnerable transitive packages and is difficult to remediate cleanly.
   - Migrate the frontend build to Vite or another maintained build chain.
   - Remove `react-scripts` from `package.json`.
   - Replace scripts with equivalent Vite scripts:

```json
{
  "scripts": {
    "start": "vite --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview --host 0.0.0.0"
  }
}
```

2. Rebuild and redeploy the frontend image.
   - ZAP observed deployed Axios `v1.6.5` in `/static/js/main.f20e175f.js`.
   - The repository already declares a newer Axios range, so the UAT image is likely older than the current source.
   - Confirm the deployed bundle hash changes after redeploy.

3. Audit production dependencies separately from development dependencies:

```bash
npm ci
npm audit --omit=dev
npm audit
npm run build
```

4. Keep a Software Bill of Materials for the release:

```bash
npx @cyclonedx/cyclonedx-npm --output-file sbom-frontend.json
```

5. Audit backend Python dependencies:

```bash
python3 -m pip install pip-audit
pip-audit -r backend-api/requirements.txt
pip-audit -r backend-lti/requirements.txt
pip-audit -r lti_tool/requirements.txt
```

6. Pin patched Python versions based on `pip-audit` output.
   - Do not leave backend packages unpinned in production requirements.
   - Pay special attention to `fastapi`, `pydantic`, `python-multipart`, `requests`, `cryptography`, `uvicorn`, `gunicorn`, and auth/JWT libraries.

### Acceptance Criteria

- `npm audit --omit=dev` returns zero critical/high vulnerabilities.
- `pip-audit` returns zero critical/high vulnerabilities for all backend requirement files.
- ZAP no longer reports `Vulnerable JS Library`.
- The final Docker image is rebuilt from the remediated lockfile.

## 2. API Documentation and Debug Surface Closure

Findings covered:

- `HTTP-006`: `/openapi.json` publicly exposed.
- `HTTP-007`: `/docs` publicly exposed.

### Required Changes

1. Keep production API docs disabled by default.
   - `backend-api/main.py` and `backend-lti/app/main.py` should set `docs_url`, `redoc_url`, and `openapi_url` only when an explicit production-safe flag is enabled.
   - Default should be closed.

2. Ensure nginx blocks debug routes in UAT/prod:

```nginx
location ^~ /docs {
    return 404;
}

location = /openapi.json {
    return 404;
}
```

3. Set these deployment variables in UAT/prod:

```bash
ENABLE_DEBUG_ROUTES=false
ENABLE_API_DOCS=false
```

4. Add an automated deployment smoke check:

```bash
curl -i https://hvlabonline-uat.singaporetech.edu.sg/docs
curl -i https://hvlabonline-uat.singaporetech.edu.sg/openapi.json
```

### Acceptance Criteria

- `/docs` returns `404` or `403`.
- `/openapi.json` returns `404` or `403`.
- Blocked debug responses still include security headers.
- Harness no longer reports public API documentation exposure.

## 3. Authentication, Authorization, and IDOR Closure

This area is required for certification even when the current active run is mostly header/dependency-focused. Client-side authorization is not sufficient.

### Required Changes

1. Every backend API route that reads or mutates tenant, student, module, assignment, progress, or file data must require server-side authentication.
2. Every object access must enforce ownership, role, or course membership on the backend.
3. Do not trust user identifiers, role claims, course IDs, or student IDs supplied only by the browser.
4. Service-to-service routes must require `X-Service-Token` or a stronger signed service credential.
5. Administrative routes must require staff/admin role checks, not just a valid login.

### Implementation Checklist

- Add route-level dependencies for JWT validation or service-token validation.
- Create shared authorization helpers for:
  - `require_authenticated_user`
  - `require_staff_or_admin`
  - `require_course_membership`
  - `require_student_owner_or_staff`
  - `require_service_token`
- Update database queries so authorization filters are part of the query, not a later frontend filter.
- Add tests for direct-object access:
  - User A cannot read User B records.
  - Student cannot modify another student's data.
  - Unauthenticated API requests fail.
  - Invalid or missing service token fails.

### Acceptance Criteria

- Unauthenticated API requests return `401`.
- Authenticated but unauthorized requests return `403`.
- IDOR tests are present and passing.
- No sensitive API route relies on frontend-only authorization.

## 4. Security Header and CSP Closure

Findings covered:

- Missing or inconsistent CSP.
- CSP wildcard directive.
- `script-src 'unsafe-inline'`.
- `style-src 'unsafe-inline'`.
- Missing clickjacking protection.
- Missing `Permissions-Policy`.
- Missing `Referrer-Policy`.
- COOP, COEP, and CORP hardening warnings.

### Root Cause to Fix

nginx `add_header` inheritance is easy to get wrong. If a child `location` has any `add_header`, parent-level `add_header` directives are not inherited. This means headers set at the `server` level can disappear for `/env-config.js`, static files, HTML, debug route responses, and cached assets.

### Required Changes

1. Create a reusable nginx security header include. Generate this file from `docker-entrypoint.sh` so the CSP value is literal at container start:

```nginx
# /etc/nginx/snippets/security-headers.conf
add_header X-Content-Type-Options "nosniff" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self' data:; img-src 'self' data: blob: https:; connect-src 'self' https://maps.googleapis.com https://api.mapbox.com https://events.mapbox.com; frame-src https://www.youtube.com https://www.youtube-nocookie.com https://docs.google.com; object-src 'none'; base-uri 'self'; frame-ancestors 'self' https://exact-approved-lms-host.example" always;
```

If the approved LMS host differs by environment, have `docker-entrypoint.sh` write the snippet with the exact host list for that environment. Do not leave shell-style variables directly inside nginx config unless nginx defines them.

2. Include the same security header snippet in every nginx location that sets any header:

```nginx
location = /env-config.js {
    include /etc/nginx/snippets/security-headers.conf;
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always;
}

location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|json)$ {
    include /etc/nginx/snippets/security-headers.conf;
    add_header Cache-Control "public, immutable" always;
}

location ~* \.(html)$ {
    include /etc/nginx/snippets/security-headers.conf;
    add_header Cache-Control "no-store" always;
}
```

3. Replace wildcard frame ancestors with exact approved LMS origins.
   - Avoid `https://*.singaporetech.edu.sg` and `https://*.brightspace.com`.
   - Use exact hostnames from the signed LTI integration approval.

4. Remove `script-src 'unsafe-inline'`.
   - Move inline scripts to external bundled files.
   - Avoid inline event handlers.
   - If a script must be inline, use a CSP hash generated during build.

5. Remove `style-src 'unsafe-inline'` where possible.
   - Self-host external fonts.
   - Avoid inline style attributes for security-sensitive pages.
   - If required by a third-party library, document the exception and scope it narrowly.

6. Remove or self-host third-party scripts and styles.
   - ZAP reports missing Subresource Integrity on external scripts/styles.
   - Google Tag Manager scripts are dynamic and are usually not practical to protect with SRI.
   - For UAT, remove analytics unless explicitly required.
   - Self-host `rsms.me/inter` fonts or remove the external stylesheet.

7. Add clickjacking protection through CSP:

```nginx
frame-ancestors 'self' https://exact-approved-lms-host.example
```

Use `frame-ancestors`, not only `X-Frame-Options`, because the app may legitimately run inside an LMS iframe.

### Acceptance Criteria

Run:

```bash
curl -I https://hvlabonline-uat.singaporetech.edu.sg/
curl -I https://hvlabonline-uat.singaporetech.edu.sg/env-config.js
curl -I https://hvlabonline-uat.singaporetech.edu.sg/manifest.json
curl -I https://hvlabonline-uat.singaporetech.edu.sg/static/js/main.f20e175f.js
```

All responses must include:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `Strict-Transport-Security`
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`

The harness must no longer report missing CSP, missing clickjacking control, missing permissions policy, missing referrer policy, or CSP wildcard/unsafe-inline findings.

## 5. Cookie and Session Closure

Findings covered:

- Cookie missing `HttpOnly`.
- Cookie missing `Secure`.
- Cookie `SameSite=None`.
- Cookie missing `SameSite`.
- Timestamp disclosure from cookie values.
- Loosely scoped managed cookies.

### Required Changes

1. Application session cookies must be set server-side with:

```text
Secure
HttpOnly
SameSite=Lax
```

2. For LTI iframe flows that require cross-site cookie behavior, use:

```text
Secure
HttpOnly
SameSite=None
```

Only use `SameSite=None` when iframe cross-site behavior is required, and document the reason.

3. Do not store bearer/session tokens in `localStorage`.
   - Prefer server-side sessions with HttpOnly cookies.
   - If a short-lived frontend token is unavoidable, keep it in memory or `sessionStorage` only and clear it on logout.

4. Managed cookies from AWS ALB, Cloudflare, or similar providers must be handled one of two ways:
   - Configure the provider to set secure attributes where supported.
   - If the provider does not allow full control, document the cookie name, purpose, owner, limitation, and compensating controls in `triage.yml` as `risk_accepted`.

5. Confirm cookie scope.
   - Avoid broad `Domain=singaporetech.edu.sg` unless required by the platform owner.
   - Prefer host-only cookies.

### Acceptance Criteria

Run:

```bash
curl -I https://hvlabonline-uat.singaporetech.edu.sg/
curl -I https://hvlabonline-uat.singaporetech.edu.sg/env-config.js
```

For every application-owned `Set-Cookie`, confirm:

- `Secure`
- `HttpOnly`
- `SameSite=Lax` or documented `SameSite=None; Secure`
- no broad domain unless approved

Managed-service cookie exceptions must be documented in the triage file with vendor evidence.

## 6. Runtime Configuration Exposure Closure

Finding covered:

- `HTTP-005`: `/env-config.js` publicly reachable.

This file can be public only if it contains no secrets.

### Required Changes

1. Audit all values emitted by `docker-entrypoint.sh`.
2. Keep only public frontend configuration in `env-config.js`.
3. Never expose:
   - API secrets
   - service tokens
   - private keys
   - database endpoints or credentials
   - privileged role lists if they reveal sensitive authorization policy
4. Keep `Cache-Control: no-store` on `/env-config.js`.
5. Include all security headers on `/env-config.js`.

### Acceptance Criteria

```bash
curl -s https://hvlabonline-uat.singaporetech.edu.sg/env-config.js
curl -I https://hvlabonline-uat.singaporetech.edu.sg/env-config.js
```

The body contains only non-secret public config, and headers include `Cache-Control: no-store` plus the common security headers.

## 7. Information Disclosure Closure

Findings covered:

- nginx banner disclosure.
- timestamp disclosure.
- public cache metadata.

### Required Changes

1. Add this to nginx `http` block:

```nginx
server_tokens off;
```

2. Avoid exposing precise server version headers.
   - If infrastructure still emits a `Server` header, document whether it comes from nginx, Cloudflare, AWS, or another layer.
   - Remove it where feasible.

3. Avoid caching sensitive HTML and authenticated pages:

```nginx
location ~* \.(html)$ {
    add_header Cache-Control "no-store" always;
}
```

4. Keep long immutable caching only for fingerprinted static assets.

### Acceptance Criteria

- `curl -I` does not expose precise nginx version.
- HTML and authenticated routes are not cacheable.
- Static fingerprinted assets may remain cacheable.
- Timestamp disclosures are either eliminated or documented as managed-service cookie behavior.

## 8. Secrets and Build Artifact Hygiene

This repository has had hard-coded secret and environment-specific findings before. Keep this permanently closed.

### Required Changes

1. Do not copy cloud credentials into Docker images.
   - `backend-api/Dockerfile` must not copy `gcloud/keys/*.json`.
   - Use workload identity, secret manager, or mounted runtime secrets.

2. Remove committed credentials from the repository and rotate them.
   - Removing a file from the latest commit is not enough if it was committed previously.
   - Rotate any credential that was ever committed.

3. Add secret scanning:

```bash
gitleaks detect --source .
```

4. Add a pre-commit secret check for developers.

5. Ensure production source maps are not published:

```bash
find build -name '*.map' -print
```

The command should return no production source maps unless explicitly approved for a private debug environment.

### Acceptance Criteria

- No credential files are copied into production images.
- No secrets are present in repo files, docs, scripts, Dockerfiles, or sample configs.
- Secret scanner passes.
- Source maps are not deployed publicly.

## 9. File Upload and Local Storage Closure

### Required Changes

1. Enforce maximum upload size on every upload route.
2. Enforce allowlisted file extensions and MIME types.
3. Normalize and validate all storage paths.
4. Reject absolute paths and parent traversal.
5. Store uploaded files outside the static frontend root.
6. Scan uploaded content where feasible.
7. Never return local file paths to the browser.

### Acceptance Criteria

- Path traversal tests fail safely.
- Unexpected extensions fail safely.
- Oversized files fail safely.
- Upload routes require authentication and authorization.

## 10. Deployment Configuration Checklist

For UAT and production, set:

```bash
ENABLE_DEBUG_ROUTES=false
ENABLE_API_DOCS=false
ENABLE_DEBUG_MODE=false
GENERATE_SOURCEMAP=false
CORS_ALLOWED_ORIGINS=https://hvlabonline-uat.singaporetech.edu.sg,<exact LMS origin>
TRUSTED_PROXY_HOSTS=<exact proxy CIDRs or hostnames>
BACKEND_API_SERVICE_TOKEN=<secret manager reference>
API_SERVICE_TOKEN=<secret manager reference>
```

Do not set wildcard CORS origins. Do not trust all proxies.

## 11. CI Security Gates

Add these checks to CI before merge:

```bash
npm ci
npm audit --omit=dev
npm run build

python3 -m pip install pip-audit
pip-audit -r backend-api/requirements.txt
pip-audit -r backend-lti/requirements.txt
pip-audit -r lti_tool/requirements.txt

gitleaks detect --source .
```

Add these checks before release:

```bash
docker build -t sit-hvvl-lms:security-candidate .
docker run --rm -p 8080:80 sit-hvvl-lms:security-candidate
```

Then run the harness against the local candidate first:

```bash
cd /Users/sayon/Documents/Codes/Frontend/blueteamer-vapt-harness
python3 -m btvapt scan \
  --scope examples/sit-local.scope.yml \
  --repo /Users/sayon/Documents/Codes/Frontend/sit_hvvl_lms-main \
  --out runs/sit-local-remediation-candidate \
  --min-docx-pages 55
```

Only after local checks pass should the UAT active profile be run inside the approved testing window.

## 12. UAT Retest Procedure

Use this process after deployment:

1. Confirm deployment version and image digest.
2. Confirm the signed testing window is active.
3. Run passive and active harness profiles:

```bash
cd /Users/sayon/Documents/Codes/Frontend/blueteamer-vapt-harness

python3 -m btvapt scan \
  --scope examples/sit-uat-passive.scope.yml \
  --repo /Users/sayon/Documents/Codes/Frontend/sit_hvvl_lms-main \
  --out runs/sit-uat-passive-retest \
  --min-docx-pages 55 \
  --write-triage-template runs/sit-uat-passive-retest/triage.yml

python3 -m btvapt scan \
  --scope examples/sit-uat-active.scope.yml \
  --repo /Users/sayon/Documents/Codes/Frontend/sit_hvvl_lms-main \
  --out runs/sit-uat-active-retest \
  --active \
  --min-docx-pages 55 \
  --write-triage-template runs/sit-uat-active-retest/triage.yml
```

4. Apply manual triage decisions only when justified:

```bash
python3 -m btvapt scan \
  --scope examples/sit-uat-active.scope.yml \
  --repo /Users/sayon/Documents/Codes/Frontend/sit_hvvl_lms-main \
  --out runs/sit-uat-active-retest-reviewed \
  --active \
  --triage runs/sit-uat-active-retest/triage.yml \
  --min-docx-pages 55
```

5. Run DOCX QA if LibreOffice is installed:

```bash
python3 -m btvapt qa-docx \
  --docx runs/sit-uat-active-retest-reviewed/vapt-report.docx \
  --out runs/sit-uat-active-retest-reviewed/docx-qa
```

## 13. Triage Rules

Use `false_positive` only when the scanner observation is technically wrong.

Use `risk_accepted` only when:

- the finding is real,
- remediation is not feasible or not owned by this application team,
- the business owner accepts the residual risk,
- compensating controls are documented.

Examples that may require `risk_accepted` rather than code changes:

- Cloudflare-managed cookies with provider-controlled attributes.
- AWS ALB cookies where attributes cannot be modified.
- Third-party LMS framing behavior required by the LTI contract.

Do not risk-accept vulnerable libraries, exposed API docs, missing server-side authorization, or public secrets.

## 14. Final Certification Exit Criteria

Before issuing a clean or closure report:

- Zero open critical findings.
- Zero open high findings.
- Medium findings remediated or documented with compensating controls.
- All public debug routes closed.
- All authentication and authorization tests pass.
- Security headers present on root, static assets, runtime config, API responses, and error responses.
- Dependency audits pass for production frontend and backend dependency sets.
- Active harness retest completed inside approved window.
- DOCX report generated and visually QAed, or QA limitation documented if renderer is unavailable.
