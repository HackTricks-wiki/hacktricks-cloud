# Application Integration — historical security review

## 2026-09-29 bulletin delta

- Reviewed Google's September 28, 2026 security-bulletin entries GCP-2026-064, GCP-2026-065 and
  GCP-2026-066. All three are managed-service vulnerabilities that Google says are fixed, with no
  customer action required.
- GCP-2026-064 / CVE-2026-19759 was an incorrect-authorization flaw in task configuration. Before
  June 17, an authenticated user could select an internal-only task type and execute arbitrary
  internal RPCs from Google's production network under a privileged identity.
- GCP-2026-065 / CVE-2026-81867 was unsafe deserialization in the JavaScript Task. Before June 28,
  a standard authenticated user could submit a crafted script that ran arbitrary code on shared
  production servers.
- GCP-2026-066 / CVE-2026-81375 was a confused deputy in the Email Task. Before June 30, a crafted
  attachment path could read and exfiltrate arbitrary Google-internal files.
- These issues provide three reusable review invariants: enforce a server-side public task-type
  allowlist at every ingest path; canonicalize and confine attachment resolution before file I/O;
  and deserialize task/script data into inert schemas rather than host/runtime objects.
- The authorized lab has neither the Application Integration API enabled nor its Google-managed
  service identity. No API, integration, identity, IAM policy, task or local payload was created.
  Current regression testing is deferred until an already provisioned disposable fixture exists,
  so the fixed bulletins are historical pattern material rather than current attack claims.

Primary source: https://docs.cloud.google.com/support/bulletins#gcp-2026-064
