# Apigee — checked

## 2026-09-26 — service enumeration and CVE-2025-13292 status correction

- Added `gcp-apigee-enum.md` covering organizations/environments, environment-group hostnames and attachments, proxy bundles/revisions/deployments, shared flows/flow hooks, target servers/references/endpoint attachments, KVM values, API products, developer apps/keys, keystores, debug masks/sessions and resource-level IAM.
- Validated the stable `gcloud apigee` surface locally. A read-only `gcloud apigee organizations list` returned no accessible Apigee organization for the lab identity, so tenant-specific REST calls were documentation-validated and not live-fired. No Apigee resource or GCP state was created.
- Rechecked the existing `GatewayToHeaven` page against Google bulletin GCP-2026-010. The chain is CVE-2025-13292, fixed for managed Apigee in `1-16-0-apigee-3`; Google says managed customers need no action. Hybrid requires the Pub/Sub analytics pipeline and the bulletin's patched release floor. Replaced five current-looking sub-techniques with one explicitly historical/unpatched-Hybrid entry carrying impact, stealth, logs and remediation.

## Current lab constraint

The authorized project is not paired with an accessible Apigee organization. Do not provision a paid Apigee organization solely for these tests; re-run live minimum-permission checks only if an existing disposable organization becomes available.
