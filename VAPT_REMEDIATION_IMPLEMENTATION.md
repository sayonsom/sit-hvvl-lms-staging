# HVVL LMS VAPT Remediation Implementation

Date: 2026-06-09

This note documents the code changes made to improve the next RBAC/IDOR/SQLi-focused VAPT run.

## Implemented Fixes

- Added signed backend API actor validation in `backend-api/app/core/auth.py`.
- Added DB-backed RBAC helpers in `backend-api/app/core/rbac.py`.
- Added `/api/v1/auth/me` for API token validation.
- Gated sensitive student, course, module, assignment, question, instructor, response, result, and file endpoints.
- Reordered route dependencies so anonymous requests are blocked before database access.
- Response submission now resolves the student from the authenticated actor and rejects mismatched `student_id`.
- Course-wide result access now requires staff/admin/service role and course assignment where current schema supports it.
- Student response reads now require self, admin/service, or a teacher assigned to one of the student's courses.
- Local file URL generation now requires authentication and returns short-lived signed file URLs.
- Local file serving now requires either a valid signed file URL or an authenticated API actor.
- Backend LTI now mints short-lived API tokens for student and staff sessions.
- Staff allow-list checks now run server-side before an API token is issued.
- Frontend now stores the API token separately and uses it for backend API calls.
- Cached staff sessions are validated against `/api/v1/auth/me` instead of trusting `sessionStorage.staff_user` alone.
- Completed LTI launches now place only a 60-second one-time login code in the browser URL; long-lived session tokens are returned after an atomic server-side exchange.
- Redis state and login-code values are atomically consumed to prevent replay races, and token/state fragments are no longer written to logs.
- Frontend, API, and LTI dynamic responses use no-store origin/CDN directives; `/env-config.js` has a dedicated deployed verification gate.
- Backend readiness rejects missing, placeholder, short, or reused security values and requires the UAT staff OIDC registration.
- Upgraded Axios to `1.19.0`, React Router DOM to `7.18.2`, Vite to `7.3.6`, and backend cryptography to `50.0.0`; full npm audit and all three Python manifest audits report zero known vulnerabilities.

## Required Deployment Environment

Set the same signing secret on both backend services:

```sh
BACKEND_API_JWT_SECRET=<shared random secret>
```

The API also accepts `VHVL_SIGNING_KEY` as a fallback, but `BACKEND_API_JWT_SECRET` is clearer for deployment.

Set service-token values consistently:

```sh
# backend-api
API_SERVICE_TOKEN=<shared service token>

# backend-lti
BACKEND_API_SERVICE_TOKEN=<same shared service token>
```

Optional but recommended:

```sh
BACKEND_API_JWT_AUDIENCE=hvvl-backend-api
LOCAL_STORAGE_SIGNING_KEY=<shared random secret>
STAFF_ALLOWED_EMAIL_DOMAIN=singaporetech.edu.sg
STAFF_ALLOWED_EMAILS=
STAFF_ALLOWED_ROLES=
STAFF_ALLOWED_GROUP_IDS=
STAFF_ADMIN_EMAILS=munhin.yong@singaporetech.edu.sg
REQUIRE_STAFF_OIDC=true
LOGIN_CODE_TTL=60
```

If `BACKEND_API_JWT_AUDIENCE` is set, set the same value on both `backend-api` and `backend-lti`.
Use independent random values of at least 32 characters for the service token,
JWT secret, and local-storage signing key. Brightspace and ADFS client or
deployment identifiers must come from their registrations and must not be
randomly generated.

## UAT Deployment Target

UAT should deploy the complete local-server stack from `docker-compose.uat.yml`:

- `virtuallab`
- `lti-backend`
- `backend-api`
- `postgres`
- `redis`

The frontend should keep `REACT_APP_API_URL=/api/v1`, and nginx should proxy `/api/v1/*` to `http://backend-api:8080/api/v1` inside the Docker network. Do not point UAT back to the old external API service for this remediation.

Use `UAT_LOCAL_DEPLOYMENT.md` as the operator runbook for the UAT team.

## Expected Next VAPT Improvements

- Anonymous sensitive API reads should return `401` before database access.
- Anonymous student list, student ID lookup, student courses, course roster, course results, student responses, signed URL generation, and local file access should no longer return data.
- Student tokens should not be able to read or submit for another student.
- Student tokens should not be able to access course-wide results.
- Staff tokens should only be issued after server-side staff allow-list checks pass.
- Staff course-result access is constrained by the current `Courses.instructor_id -> Instructors.email` mapping until the full `course_staff` database migration is applied.
- Invalid anonymous write probes should return `401`, and student write probes against staff/admin endpoints should return `403`.
- React Router audit finding should close after retest.

## Remaining Work

- Deploy these code changes to UAT with the local Docker stack before rerunning Caido/Burp testing.
- Apply and validate the database hardening migration after duplicate/null data cleanup.
- Replace the current single-instructor course mapping with the `course_staff` table for full teacher/course RBAC.
- Rerun `scripts/hvvl_vapt_retest.py` directly and through Caido after the UAT app/API return healthy responses.
