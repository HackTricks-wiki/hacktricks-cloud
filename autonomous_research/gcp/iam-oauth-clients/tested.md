# iam.oauthClients (Workforce Identity Federation OAuth clients) — SHIPPED

## Result: SHIPPED (persistence)
Added to `gcp-persistence/gcp-workload-identity-federation-persistence.md` as
"Workforce Identity Federation — project-level OAuth-client backdoor".

## What was live-tested (lab gcp-labs-eqd4ny8d)
- `gcloud iam oauth-clients create` (confidential-client, allowed-scopes=cloud-platform+openid,
  allowed-grant-types=authorization-code+refresh-token, allowed-redirect-uris=attacker URL)
  -> created, state ACTIVE immediately.
- `gcloud iam oauth-clients credentials create` -> minted; `credentials describe` returns the
  plaintext `clientSecret` to any holder (so oauthClientCredentials.get = secret theft path).
- `projects get-iam-policy <lab> | grep -ic oauthclient` -> 0. The client is NOT a member in the
  project IAM allow policy => invisible to a getIamPolicy review.
- Role `roles/iam.oauthClientAdmin` carries all oauthClients.* + oauthClientCredentials.* (verified
  via `gcloud iam roles describe`). It is project-level and innocuous-looking.

## What was NOT lab-reproducible (documented from Google docs)
- End-to-end token exchange: needs an external IdP + a workforce pool + a workforce user to
  authorize the client via the attacker redirect URI. Documented honestly as per-docs, with an
  explicit precondition (org must use Workforce Identity Federation).

## Teardown
- Deleted the oauthClient (`... oauth-clients delete`, credential removed with parent). Credential
  standalone-delete requires disable-first (noted); parent delete handled it. No active client
  remains (`list` shows none). Soft-delete tombstone auto-purges (30d), consistent with other IAM
  federation resources.

## Why it clears the "real useful attack" bar
Distinct, undocumented IAM resource; project-level persistence surface invisible to IAM allow-policy
review; direct analogue of the already-documented IAP clientauthconfig OAuth-client backdoor and the
org-level workforce pool/provider backdoor on the same page. Honest preconditions stated.
