#!/bin/sh
set -eu

: "${IDENTITY_CLIENT_ID:?set IDENTITY_CLIENT_ID}"
: "${WEBPUBSUB_HOST:?set WEBPUBSUB_HOST}"

imds='http://169.254.169.254/metadata/identity/oauth2/token'
token_response=$(curl -fsS --connect-timeout 2 --max-time 5 \
  --retry 12 --retry-all-errors --retry-delay 2 \
  -H Metadata:true \
  "${imds}?api-version=2019-08-01&resource=https%3A%2F%2Fwebpubsub.azure.com%2F&client_id=${IDENTITY_CLIENT_ID}")
access_token=$(printf '%s' "$token_response" | jq -r .access_token)

probe() {
  label=$1
  method=$2
  hub=$3
  room=$4
  body=$5
  url="https://${WEBPUBSUB_HOST}/api/hubs/${hub}/chat/rooms/${room}?api-version=2026-02-01-preview"
  output="/tmp/${label}.json"

  if [ -n "$body" ]; then
    code=$(curl -sS -o "$output" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer ${access_token}" \
      -H 'Content-Type: application/json' \
      --data "$body")
  else
    code=$(curl -sS -o "$output" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer ${access_token}")
  fi

  printf '%s HTTP %s\n' "$label" "$code"
  jq -c . "$output" 2>/dev/null || sed -n '1,8p' "$output"
}

probe same_hub_read GET chata room-a ''
probe cross_hub_read GET chatb room-b ''
probe same_hub_write PUT chata room-a '{"title":"unauthorized mutation canary"}'
