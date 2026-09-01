// Runtime environment configuration.
//
// In Docker/Nginx deployments, this file is generated at container start by
// `docker-entrypoint.sh` so the frontend can read runtime variables without a
// rebuild.
//
// In local development it will usually remain empty and the app will fall back
// to CRA build-time `process.env.REACT_APP_*` values.
window.__ENV = window.__ENV || {};

