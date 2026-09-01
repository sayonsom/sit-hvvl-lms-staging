#!/bin/sh

set -eu

ENV_JS="/usr/share/nginx/html/env-config.js"
PROXY_CONF="/etc/nginx/conf.d/backend-proxy.conf"
LTI_PROXY_CONF="/etc/nginx/conf.d/lti-proxy.conf"
DEBUG_ROUTES_CONF="/etc/nginx/conf.d/lti-debug-routes.conf"
SECURITY_HEADERS_CONF="/etc/nginx/snippets/security-headers.conf"
NO_STORE_HEADERS_CONF="/etc/nginx/snippets/no-store-headers.conf"

escape_js() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

escape_nginx_header() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

# --- Nginx backend proxy configuration ---
BACKEND_API_URL="${BACKEND_API_URL:-http://backend-api:8080/api/v1}"
LTI_BACKEND_URL="${LTI_BACKEND_URL:-http://lti-backend:8000}"

# Extract upstream origin (scheme + host[:port])
UPSTREAM="$(echo "$BACKEND_API_URL" | sed -E 's|^(https?://[^/]+).*|\1|')"
# Extract just the hostname (without port) for the Host header
HOST="$(echo "$BACKEND_API_URL" | sed -E 's|^https?://([^/:]+).*|\1|')"
LTI_UPSTREAM="$(echo "$LTI_BACKEND_URL" | sed -E 's|^(https?://[^/]+).*|\1|')"
LTI_HOST="$(echo "$LTI_BACKEND_URL" | sed -E 's|^https?://([^/:]+).*|\1|')"

mkdir -p /etc/nginx/conf.d /etc/nginx/snippets

# --- Nginx security headers ---
# Set exact frame ancestors per environment. Do not use wildcard LMS origins here.
CSP_FRAME_ANCESTORS="$(escape_nginx_header "${CSP_FRAME_ANCESTORS:-'self' https://hvlabonline-uat.singaporetech.edu.sg}")"
CSP_CONNECT_SRC="$(escape_nginx_header "${CSP_CONNECT_SRC:-'self' https://maps.googleapis.com https://api.mapbox.com https://events.mapbox.com}")"
CSP_FRAME_SRC="$(escape_nginx_header "${CSP_FRAME_SRC:-https://www.youtube.com https://www.youtube-nocookie.com https://docs.google.com}")"
CSP_WORKER_SRC="$(escape_nginx_header "${CSP_WORKER_SRC:-'self' blob:}")"
CSP_VALUE="default-src 'self'; script-src 'self'; worker-src ${CSP_WORKER_SRC}; style-src 'self'; font-src 'self' data:; img-src 'self' data: blob: https:; connect-src ${CSP_CONNECT_SRC}; frame-src ${CSP_FRAME_SRC}; object-src 'none'; base-uri 'self'; frame-ancestors ${CSP_FRAME_ANCESTORS}"
CSP_VALUE="$(escape_nginx_header "$CSP_VALUE")"

cat > "$SECURITY_HEADERS_CONF" <<NGINX
add_header X-Content-Type-Options "nosniff" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
add_header Content-Security-Policy "$CSP_VALUE" always;
NGINX

cat > "$NO_STORE_HEADERS_CONF" <<'NGINX'
add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, private, max-age=0, s-maxage=0" always;
add_header CDN-Cache-Control "no-store" always;
add_header Cloudflare-CDN-Cache-Control "no-store" always;
add_header Surrogate-Control "no-store" always;
add_header Pragma "no-cache" always;
add_header Expires "0" always;
NGINX

# Generate different proxy config for HTTPS vs HTTP upstreams
case "$UPSTREAM" in
  https://*)
    cat > "$PROXY_CONF" <<NGINX
location ^~ /api/v1/ {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $UPSTREAM;
    proxy_hide_header Cache-Control;
    proxy_hide_header Expires;
    proxy_ssl_server_name on;
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
    proxy_set_header Host $HOST;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
NGINX
    ;;
  *)
    cat > "$PROXY_CONF" <<NGINX
location ^~ /api/v1/ {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $UPSTREAM;
    proxy_hide_header Cache-Control;
    proxy_hide_header Expires;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
NGINX
    ;;
esac

if [ "${ENABLE_LTI_PROXY:-true}" = "true" ]; then
  case "$LTI_UPSTREAM" in
    https://*)
      cat > "$LTI_PROXY_CONF" <<NGINX
location ^~ /lti/ {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $LTI_UPSTREAM;
    proxy_hide_header Cache-Control;
    proxy_hide_header Expires;
    proxy_ssl_server_name on;
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
    proxy_set_header Host $LTI_HOST;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
NGINX
      ;;
    *)
      cat > "$LTI_PROXY_CONF" <<NGINX
location ^~ /lti/ {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $LTI_UPSTREAM;
    proxy_hide_header Cache-Control;
    proxy_hide_header Expires;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
NGINX
      ;;
  esac
else
  cat > "$LTI_PROXY_CONF" <<'NGINX'
location ^~ /lti/ {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    return 404;
}
NGINX
fi

if [ "${ENABLE_DEBUG_ROUTES:-false}" = "true" ]; then
  cat > "$DEBUG_ROUTES_CONF" <<NGINX
location ^~ /docs {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $LTI_UPSTREAM;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}

location = /openapi.json {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    proxy_pass $LTI_UPSTREAM/openapi.json;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
NGINX
else
  cat > "$DEBUG_ROUTES_CONF" <<'NGINX'
location ^~ /docs {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    return 404;
}

location = /openapi.json {
    include /etc/nginx/snippets/security-headers.conf;
    include /etc/nginx/snippets/no-store-headers.conf;
    return 404;
}
NGINX
fi

echo "Backend proxy: $UPSTREAM (host: $HOST)"
echo "LTI proxy: ${ENABLE_LTI_PROXY:-true} -> $LTI_UPSTREAM (host: $LTI_HOST)"

# --- Runtime JS environment config ---
API_URL="$(escape_js "${REACT_APP_API_URL:-/api/v1}")"
LTI_API_URL="$(escape_js "${REACT_APP_LTI_API_URL:-}")"
MAPS_API="$(escape_js "${REACT_APP_MAPS_API:-}")"
AAD_CLIENT_ID="$(escape_js "${REACT_APP_AAD_CLIENT_ID:-}")"
AAD_TENANT_ID="$(escape_js "${REACT_APP_AAD_TENANT_ID:-}")"
AAD_AUTHORITY="$(escape_js "${REACT_APP_AAD_AUTHORITY:-}")"
AAD_REDIRECT_URI="$(escape_js "${REACT_APP_AAD_REDIRECT_URI:-}")"
AAD_SCOPES="$(escape_js "${REACT_APP_AAD_SCOPES:-}")"
AAD_ALLOWED_GROUP_IDS="$(escape_js "${REACT_APP_AAD_ALLOWED_GROUP_IDS:-}")"
AAD_ALLOWED_ROLES="$(escape_js "${REACT_APP_AAD_ALLOWED_ROLES:-}")"
AAD_ALLOWED_EMAIL_DOMAIN="$(escape_js "${REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN:-}")"
AAD_ALLOWED_EMAILS="$(escape_js "${REACT_APP_AAD_ALLOWED_EMAILS:-}")"

cat > "$ENV_JS" <<EOF
window.__ENV = window.__ENV || {};
window.__ENV.REACT_APP_API_URL = "${API_URL}";
window.__ENV.REACT_APP_LTI_API_URL = "${LTI_API_URL}";
window.__ENV.REACT_APP_MAPS_API = "${MAPS_API}";
window.__ENV.REACT_APP_AAD_CLIENT_ID = "${AAD_CLIENT_ID}";
window.__ENV.REACT_APP_AAD_TENANT_ID = "${AAD_TENANT_ID}";
window.__ENV.REACT_APP_AAD_AUTHORITY = "${AAD_AUTHORITY}";
window.__ENV.REACT_APP_AAD_REDIRECT_URI = "${AAD_REDIRECT_URI}";
window.__ENV.REACT_APP_AAD_SCOPES = "${AAD_SCOPES}";
window.__ENV.REACT_APP_AAD_ALLOWED_GROUP_IDS = "${AAD_ALLOWED_GROUP_IDS}";
window.__ENV.REACT_APP_AAD_ALLOWED_ROLES = "${AAD_ALLOWED_ROLES}";
window.__ENV.REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN = "${AAD_ALLOWED_EMAIL_DOMAIN}";
window.__ENV.REACT_APP_AAD_ALLOWED_EMAILS = "${AAD_ALLOWED_EMAILS}";
EOF

chmod 644 "$ENV_JS"

exec "$@"
