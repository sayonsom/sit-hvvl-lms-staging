#!/bin/sh

set -eu

BASE_URL="${1:-${BASE_URL:-https://hvlabonline-uat.singaporetech.edu.sg}}"
BASE_URL="${BASE_URL%/}"
TMP_DIR="$(mktemp -d)"
HEADERS=""
BODY=""
STATUS=""

cleanup() {
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

fetch() {
  path="$1"
  suffix="$(printf '%s' "$path" | tr '/?&=' '_____')"
  HEADERS="$TMP_DIR/${suffix}.headers"
  BODY="$TMP_DIR/${suffix}.body"
  STATUS="$(
    curl -sS \
      --connect-timeout 10 \
      --max-time 30 \
      --retry 2 \
      --retry-delay 1 \
      -D "$HEADERS" \
      -o "$BODY" \
      -w '%{http_code}' \
      "${BASE_URL}${path}"
  )"
}

require_status() {
  path="$1"
  expected="$2"
  fetch "$path"
  case " $expected " in
    *" $STATUS "*) ;;
    *)
      echo "FAIL ${path}: expected HTTP ${expected}; received ${STATUS}" >&2
      exit 1
      ;;
  esac
}

require_header() {
  header="$1"
  if ! grep -iq "^${header}:" "$HEADERS"; then
    echo "FAIL: ${header} is missing from ${BASE_URL}" >&2
    exit 1
  fi
}

require_header_contains() {
  header="$1"
  expected="$2"
  if ! grep -i "^${header}:" "$HEADERS" | grep -qiF "$expected"; then
    echo "FAIL: ${header} does not contain '${expected}'" >&2
    exit 1
  fi
}

require_core_headers() {
  require_header "Content-Security-Policy"
  require_header "X-Content-Type-Options"
  require_header "Strict-Transport-Security"
  require_header "Referrer-Policy"
  require_header "Permissions-Policy"
}

require_status / "200"
require_core_headers
require_header_contains "Cache-Control" "no-store"

require_status /health "200"
require_status /lti/health/ready "200"
require_core_headers
require_header_contains "Cache-Control" "no-store"
if ! grep -Eq '"status"[[:space:]]*:[[:space:]]*"ready"' "$BODY"; then
  echo "FAIL /lti/health/ready: service did not report ready" >&2
  exit 1
fi

cache_buster="$(date +%s)"
require_status "/env-config.js?v=${cache_buster}" "200"
require_core_headers
require_header_contains "Cache-Control" "no-store"
require_header_contains "Cache-Control" "no-cache"
require_header_contains "Cache-Control" "must-revalidate"
require_header_contains "CDN-Cache-Control" "no-store"
require_header_contains "Pragma" "no-cache"

if grep -Eq 'POSTGRES_PASSWORD|BACKEND_API_SERVICE_TOKEN|BACKEND_API_JWT_SECRET|LOCAL_STORAGE_SIGNING_KEY|OPENAI_API_KEY|REDIS_PASSWORD' "$BODY"; then
  echo "FAIL /env-config.js: server-side secret key is present" >&2
  exit 1
fi

cf_cache_status="$(grep -i '^cf-cache-status:' "$HEADERS" | tail -n 1 | tr -d '\r' | cut -d: -f2- | xargs || true)"
case "$(printf '%s' "$cf_cache_status" | tr '[:lower:]' '[:upper:]')" in
  BYPASS|DYNAMIC) ;;
  *)
    echo "FAIL /env-config.js: expected Cloudflare BYPASS or DYNAMIC; received '${cf_cache_status:-missing}'" >&2
    exit 1
    ;;
esac

require_status /api/v1/auth/me "401"
require_core_headers
require_header_contains "Cache-Control" "no-store"
require_status /docs "403 404"
require_status /openapi.json "403 404"

if grep -iq 'Server: nginx/[0-9]' "$HEADERS"; then
  echo "FAIL: precise nginx version is exposed" >&2
  exit 1
fi

echo "PASS: deployed VAPT controls verified at ${BASE_URL}"
