#!/bin/sh
set -eu

: "${SUB_ID:?}"
: "${RG_NAME:?}"
: "${MI_CLIENT_ID:?}"

api_version="2024-11-01"
domain_name="nonexistent-domain-26926.com"
collection="https://management.azure.com/subscriptions/${SUB_ID}/resourceGroups/${RG_NAME}/providers/Microsoft.DomainRegistration/domains"
resource="${collection}/${domain_name}"

get_token() {
  curl -fsS -H Metadata:true \
    "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2019-08-01&resource=https%3A%2F%2Fmanagement.azure.com%2F&client_id=${MI_CLIENT_ID}" \
    | jq -r .access_token
}

probe() {
  label="$1"
  method="$2"
  url="$3"
  body="${4-}"
  token="$(get_token)"
  if [ "$#" -ge 4 ]; then
    response="$(curl -sS -X "$method" -H "Authorization: Bearer ${token}" -H 'Content-Type: application/json' -d "$body" -w '\nHTSTATUS:%{http_code}' "$url")"
  else
    response="$(curl -sS -X "$method" -H "Authorization: Bearer ${token}" -w '\nHTSTATUS:%{http_code}' "$url")"
  fi
  status="${response##*HTSTATUS:}"
  payload="${response%HTSTATUS:*}"
  printf 'probe=%s method=%s status=%s payload=%s\n' "$label" "$method" "$status" "$payload"
  PROBE_STATUS="$status"
}

# Wait for the one-action custom role to reach the RP. A successful empty list is
# the positive authorization control and avoids interpreting propagation as denial.
attempt=1
while [ "$attempt" -le 30 ]; do
  probe list_domains GET "${collection}?api-version=${api_version}"
  if [ "$PROBE_STATUS" = "200" ]; then
    break
  fi
  attempt=$((attempt + 1))
  sleep 10
done

if [ "$PROBE_STATUS" != "200" ]; then
  printf 'result=INCONCLUSIVE reason=read-role-did-not-propagate\n'
  exit 2
fi

probe get_missing_domain GET "${resource}?api-version=${api_version}"
probe transfer_out_missing_domain PUT "${resource}/transferOut?api-version=${api_version}" ''
if [ "${EXPECT_TRANSFER_AUTHORIZED-0}" = "1" ]; then
  transfer_attempt=1
  while [ "$PROBE_STATUS" = "403" ] && [ "$transfer_attempt" -lt 30 ]; do
    sleep 10
    transfer_attempt=$((transfer_attempt + 1))
    probe transfer_out_missing_domain_retry PUT "${resource}/transferOut?api-version=${api_version}" ''
  done
fi
probe write_missing_domain_control PUT "${resource}?api-version=${api_version}" '{}'
probe renew_missing_domain_control POST "${resource}/renew?api-version=${api_version}" ''
