# HVVL LMS VAPT Retest Runbook

Date: 2026-06-09

This runbook is for the authorized HVVL LMS UAT RBAC and SQL-injection retest after the local-server UAT stack is redeployed.

## Current Status

- UAT is intended to run the complete local Docker stack from `docker-compose.uat.yml`.
- `https://hvlabonline-uat.singaporetech.edu.sg/api/v1/*` should proxy to the local `backend-api` container.
- UAT should not depend on the old external Cloud Run API path.
- `https://xsitestg.singaporetech.edu.sg/d2l/home/6874` is reachable and redirects to Brightspace login.

The June 17 retest showed the UAT site was reachable but still running stale API behavior: `/api/v1/auth/me` returned `404`, while sensitive anonymous reads still returned `200`. Redeploy the local stack using `UAT_LOCAL_DEPLOYMENT.md`, then rerun this retest.

## Tooling

Caido is installed locally in `output/tools/caido/` and can act as the Burp-compatible interception/proxy layer.

Expected local endpoints:

- Caido UI: `http://127.0.0.1:8090`
- Caido proxy: `http://127.0.0.1:8081`

Start Caido if it is not already running:

```sh
output/tools/caido/caido-cli \
  --ui-listen 127.0.0.1:8090 \
  --proxy-listen 127.0.0.1:8081 \
  --no-open \
  --no-sync \
  --allow-guests \
  --data-path output/tools/caido/data
```

## Retest Commands

Direct safe retest:

```sh
python3 scripts/hvvl_vapt_retest.py
```

Retest through Caido/Burp proxy:

```sh
python3 scripts/hvvl_vapt_retest.py \
  --proxy http://127.0.0.1:8081 \
  --insecure
```

Retest with invalid-body write auth-gate probes:

```sh
python3 scripts/hvvl_vapt_retest.py \
  --proxy http://127.0.0.1:8081 \
  --insecure \
  --include-auth-gate-posts
```

The script writes raw headers, bodies, `summary.json`, and `summary.md` under `output/evidence/retest-<timestamp>/`.

## Authenticated Phase

Before authenticated retesting, deploy the remediation code with `docker-compose.uat.yml` and set the shared API-token environment variables documented in `UAT_LOCAL_DEPLOYMENT.md` and `VAPT_REMEDIATION_IMPLEMENTATION.md`.

Run the deployment gate first. Do not begin authenticated testing unless it
passes:

```sh
sh scripts/verify-deployed-vapt-controls.sh \
  https://hvlabonline-uat.singaporetech.edu.sg
```

After logging in manually through the browser/proxy, export captured session material as environment variables. Use only the values for the authorized UAT accounts.

Student profile:

```sh
export HVVL_STUDENT_COOKIE='name=value; other=value'
export HVVL_STUDENT_AUTHORIZATION='Bearer ey...'
```

Teacher profile:

```sh
export HVVL_TEACHER_COOKIE='name=value; other=value'
export HVVL_TEACHER_AUTHORIZATION='Bearer ey...'
```

Object IDs for cross-role checks:

```sh
export HVVL_COURSE_ID='1'
export HVVL_OTHER_COURSE_ID='2'
export HVVL_STUDENT_ID='1'
export HVVL_STUDENT_EMAIL='student@example.edu'
export HVVL_MODULE_ID='00000000-0000-0000-0000-000000000000'
```

Then rerun:

```sh
python3 scripts/hvvl_vapt_retest.py \
  --proxy http://127.0.0.1:8081 \
  --insecure
```

If the Caido or Burp CA certificate is installed into Python's trust store, omit `--insecure`.

## Expected Closure Criteria

- Anonymous calls to student lists, rosters, result endpoints, student response endpoints, and signed URL generation return `401`, `403`, or a login redirect.
- Student sessions cannot read another student's responses or a course-wide result endpoint.
- Teacher sessions can read assigned course results but cannot read unassigned course results.
- SQLi probes return controlled `400`, `401`, `403`, `404`, or `422` responses without SQL/database error leakage.
- Invalid-body write probes are blocked by authentication before request validation.
- Retest evidence is captured through Caido/Burp and linked from the final report.
