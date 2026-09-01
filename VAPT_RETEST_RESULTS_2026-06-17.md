# HVVL LMS UAT VAPT Retest Results

Date: 2026-06-17

## Result

UAT is reachable again:

- `https://hvlabonline-uat.singaporetech.edu.sg/` returned `200`.
- `https://hvlabonline-uat.singaporetech.edu.sg/health` returned `200` with body `healthy`.
- `https://hvlabonline-uat.singaporetech.edu.sg/api/v1/courses` returned `200`.
- Brightspace course URL returned `200` and redirected to the xSiTe login boundary.

The browser-facing API is still vulnerable because sensitive endpoints return data anonymously.

## Direct Retest Summary

Authoritative evidence: `output/evidence/retest-20260617-direct/summary.md`

- Fail: 8
- Review: 1
- Pass: 10
- Inconclusive: 0

Failed checks:

- Anonymous all-students read returned `200`.
- Anonymous course roster read returned `200`.
- Anonymous course-wide results read returned `200`.
- Anonymous alternate course results read returned `200`.
- Anonymous student response read returned `200`.
- Anonymous student courses read returned `200`.
- Anonymous file signed URL generation returned `200`.
- Invalid anonymous course create returned `422`, meaning validation ran before authentication.

Review item:

- Anonymous student ID lookup for `vhvl_stud01` returned `404`; this should be retested with a known deployed student email and should still require authentication.

## SQL Injection Retest

No SQL/database error indicators were observed in the non-destructive probes:

- Email single-quote probe returned controlled `404`.
- Email boolean probe returned controlled `403`.
- Numeric route quote probes returned controlled `422`.

This does not close SQLi coverage for authenticated workflows; it only means the anonymous low-impact probes did not produce database error leakage.

## Deployment Gap

The remediation code does not appear to be deployed to this UAT target:

- `/api/v1/auth/me` returned `404`.
- Anonymous sensitive reads still returned `200`.

Deploy the RBAC remediation code and required environment variables from `VAPT_REMEDIATION_IMPLEMENTATION.md`, then rerun:

```sh
docker compose --env-file .env.uat -f docker-compose.uat.yml build --pull
docker compose --env-file .env.uat -f docker-compose.uat.yml up -d --remove-orphans

HVVL_COURSE_ID=2 \
HVVL_OTHER_COURSE_ID=1 \
HVVL_STUDENT_ID=1 \
HVVL_STUDENT_EMAIL=vhvl_stud01 \
python3 scripts/hvvl_vapt_retest.py \
  --api-base https://hvlabonline-uat.singaporetech.edu.sg/api/v1 \
  --uat-url https://hvlabonline-uat.singaporetech.edu.sg/ \
  --out output/evidence/retest-20260617-post-deploy \
  --include-auth-gate-posts
```

The corrected UAT deployment path is the all-in-one local-server stack documented in `UAT_LOCAL_DEPLOYMENT.md`; it should not proxy `/api/v1` to the old external API service.

## Artifacts

- Direct summary: `output/evidence/retest-20260617-direct/summary.md`
- Direct raw evidence: `output/evidence/retest-20260617-direct/`
- Reachability evidence: `output/evidence/recheck-2026-06-17/`
- Brightspace login boundary screenshot: `output/playwright/brightspace-login-boundary-20260617.png`
- Retest addendum PDF: `output/pdf/HVVL_LMS_UAT_VAPT_Retest_Addendum_2026-06-17.pdf`
