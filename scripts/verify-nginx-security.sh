#!/bin/sh

set -eu

IMAGE="${IMAGE:-sit-hvvl-lms:security-candidate}"
PORT="${PORT:-18080}"
CONTAINER_ID=""

cleanup() {
  if [ -n "$CONTAINER_ID" ]; then
    docker rm -f "$CONTAINER_ID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

docker build -t "$IMAGE" .

CONTAINER_ID="$(
  docker run -d \
    -p "${PORT}:80" \
    -e ENABLE_DEBUG_ROUTES=false \
    -e ENABLE_LTI_PROXY=false \
    -e BACKEND_API_URL=http://127.0.0.1:65534/api/v1 \
    -e LTI_BACKEND_URL=http://127.0.0.1:65533 \
    -e CSP_FRAME_ANCESTORS="'self' http://localhost:${PORT}" \
    "$IMAGE"
)"

for _ in $(seq 1 30); do
  if curl -fsS "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "http://localhost:${PORT}/health" >/dev/null 2>&1; then
  echo "Nginx candidate did not become healthy" >&2
  docker logs "$CONTAINER_ID" >&2 || true
  exit 1
fi

require_header() {
  path="$1"
  header="$2"
  tmp="$(mktemp)"
  curl -sS -o /dev/null -D "$tmp" "http://localhost:${PORT}${path}"
  if ! grep -iq "^${header}:" "$tmp"; then
    echo "Missing ${header} on ${path}" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
}

require_header_contains() {
  path="$1"
  header="$2"
  expected="$3"
  tmp="$(mktemp)"
  curl -sS -o /dev/null -D "$tmp" "http://localhost:${PORT}${path}"
  if ! grep -i "^${header}:" "$tmp" | grep -qiF "$expected"; then
    echo "Expected ${header} on ${path} to contain: ${expected}" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
}

require_status_closed() {
  path="$1"
  tmp="$(mktemp)"
  curl -sS -o /dev/null -D "$tmp" "http://localhost:${PORT}${path}"
  if ! grep -Eq "^HTTP/[0-9.]+ (403|404)" "$tmp"; then
    echo "Expected ${path} to return 403 or 404" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
}

for path in / /env-config.js /manifest.json /health /api/v1/auth/me /lti/health/ready /docs /openapi.json; do
  require_header "$path" "Content-Security-Policy"
  require_header "$path" "X-Content-Type-Options"
  require_header "$path" "Strict-Transport-Security"
  require_header "$path" "Referrer-Policy"
  require_header "$path" "Permissions-Policy"
  require_header "$path" "Cross-Origin-Opener-Policy"
  require_header "$path" "Cross-Origin-Resource-Policy"
done

for path in / /env-config.js /manifest.json /health /api/v1/auth/me /lti/health/ready /docs /openapi.json; do
  require_header_contains "$path" "Cache-Control" "no-store"
done

require_header_contains /env-config.js "Cache-Control" "no-cache"
require_header_contains /env-config.js "Cache-Control" "must-revalidate"
require_header_contains /env-config.js "CDN-Cache-Control" "no-store"
require_header_contains /env-config.js "Cloudflare-CDN-Cache-Control" "no-store"
require_header_contains /env-config.js "Surrogate-Control" "no-store"
require_header_contains /env-config.js "Pragma" "no-cache"

if curl -fsS "http://localhost:${PORT}/env-config.js" | grep -Eq 'POSTGRES_PASSWORD|BACKEND_API_SERVICE_TOKEN|BACKEND_API_JWT_SECRET|LOCAL_STORAGE_SIGNING_KEY|OPENAI_API_KEY|REDIS_PASSWORD'; then
  echo "Runtime browser configuration contains a server-side secret key" >&2
  exit 1
fi

require_status_closed /docs
require_status_closed /openapi.json

if curl -sS -o /dev/null -D - "http://localhost:${PORT}/" | grep -iq "Server: nginx/"; then
  echo "Precise nginx version is exposed" >&2
  exit 1
fi

echo "Nginx security header smoke check passed on http://localhost:${PORT}"
