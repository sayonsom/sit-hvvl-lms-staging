# SIT HVVL Staging Deployment

This repository is dedicated to the SIT staging server and refuses to deploy a
production `FRONTEND_URL`.

The populated `.env.uat` is server-owned and must never be committed. Keep the
file at the repository root with permission mode `0600`.

## Deploy or repair staging

```sh
cd /usr/local/src/sit-hvvl-lms-staging
git pull --ff-only origin main
sudo python3 scripts/deploy_staging.py .env.uat
```

That single deployment command:

- validates the staging URLs and required configuration without printing values;
- replaces a legacy short PostgreSQL password with a generated strong value;
- synchronises the password inside the existing PostgreSQL volume;
- reuses the existing `sit_test_v1` Compose project and its data volumes;
- preserves PostgreSQL, Redis, and local-storage data volumes;
- rebuilds the frontend and both APIs from the checked-out source; and
- waits until all five services report healthy.

It is safe to rerun after an interrupted attempt. Never use `docker compose
down -v`, `docker volume rm`, or manually delete the PostgreSQL volume.

## Verify

```sh
sudo docker compose --env-file .env.uat -f docker-compose.uat.yml ps
curl --fail --show-error http://127.0.0.1:3000/health
sudo sh scripts/verify-deployed-vapt-controls.sh \
  https://hvlabonline-uat.singaporetech.edu.sg
```

The Compose listing must contain five healthy services: `postgres`, `redis`,
`backend-api`, `lti-backend`, and `virtuallab`. The final verifier line must be:

```text
PASS: deployed VAPT controls verified at https://hvlabonline-uat.singaporetech.edu.sg
```

If deployment fails, send the redacted diagnostic output produced by
`deploy_staging.py`; do not send `.env.uat`.
