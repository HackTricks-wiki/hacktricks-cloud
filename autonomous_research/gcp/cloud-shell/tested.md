# Cloud Shell security research ledger

## 2026-09-28 — post-exploitation documentation audit

No Cloud Shell session, API, SSH key, proxy, container, IAM policy or other cloud/local test asset
was created or changed. This pass used current official Cloud Shell architecture, authorization,
configuration and API references plus the gcloud token command reference.

### Retained technique

- A process with command execution in an already-authorized Cloud Shell session can call
  `gcloud auth print-access-token` and reuse the session user's short-lived access token. The owner
  must previously have accepted the normal authorization prompt; a new session is not silently
  authorized by this command. Later API authorization and logging occur as that user.

### Removed or rejected claims

- **Metadata equals the logged-in user token:** false boundary. Cloud Shell passes the interactive
  user's OAuth credential through its authorize flow. Any VM metadata service-account identity is a
  separate principal and matters only if it independently has useful permissions.
- **Current Docker socket gives Google-host escape:** unsupported and low value. Current docs say the
  per-user shell is a container on a per-session VM, Docker is preinstalled, and the user already has
  root on that allocated VM. The historical host-socket commands are not a current platform escape.
- **Run an open Squid/ngrok proxy:** generic software execution after shell compromise, with no
  additional sensitive-information or cloud-authorization boundary. It is deliberately omitted.

### Telemetry boundary

The local token-print command has no documented Cloud Audit Log method. Cloud Shell documents
anonymous preinstalled-command usage metrics that exclude personally identifiable arguments; this
is not caller-attributed audit evidence. Downstream API calls keep the user's identity and follow
each destination service's logging contract. Endpoint/session telemetry remains environment-specific.

## 2026-09-28 — reciprocal review

- Reconfirmed that the normal Cloud Shell authorization is user-approved and lasts only for the
  current ephemeral-VM session; restart or a new session requires reauthorization.
- Revalidated the command and impact boundary: `gcloud auth print-access-token` exposes a
  short-lived token for the already-authorized active identity, not a password, browser cookie,
  refresh token, metadata identity, or permission beyond that user's scopes and IAM grants.
- Rechecked telemetry wording. Token printing is local with no published Cloud Audit method;
  destination API use follows that service's audit contract, while anonymized Cloud Shell terminal
  metrics explicitly exclude arguments. No documentation correction or cloud mutation was needed.
