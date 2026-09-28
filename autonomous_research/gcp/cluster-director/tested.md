# Cluster Director security research ledger

## 2026-09-29 — retained login-node startup script

- Reviewed official Cluster Director overview, v1/v1beta REST schema (current v1 discovery revision
  `20260918`), modify semantics, audit matrix, installed Google Cloud SDK 586.0.0 CLI behavior,
  predefined Admin/Editor/Viewer roles and the service-agent role.
- The current Cluster schema exposes login-node and node-set startup scripts plus Slurm
  prolog/epilog hooks, but no service-account field. The modify guide's statement that a service
  account is modifiable is not represented in current discovery or CLI flags; no identity-replacement
  claim was made.
- Built a bounded regional fixture with one `n2-standard-2` login node, no compute nodes, no
  accelerator and no managed file system. Cluster Director created an isolated VPC plus service
  plumbing and attached the pre-existing Compute default service account with cloud-platform scope.
- Created an isolated caller whose custom role contained exactly
  `hypercomputecluster.clusters.update`, plus Service Usage Consumer. A raw stable-v1 PATCH with
  update mask `orchestrator.slurm.loginNodes.startupScript` first failed on the retained account's
  `iam.serviceAccounts.actAs`. This demonstrates that `clusters.update` alone cannot exploit the
  retained identity.
- After granting `roles/iam.serviceAccountUser` only on that existing account, the identical PATCH
  succeeded. The caller still received HTTP 403 for direct Cloud Storage listing and for
  `iamcredentials.generateAccessToken`, proving that actAs did not become token-creator authority.
- The service stopped/restarted the same login VM. The corrected startup hook ran as root and wrote
  a synthetic marker through the VM identity; the object identified
  `480556499979-compute@developer.gserviceaccount.com`. This verifies the expected privilege
  transition and service-level persistence primitive.
- One preliminary payload attempt failed because a harness quoting error collapsed intended
  newlines. Serial output showed the custom hook was reached as root and failed before Storage.
  The corrected six-line payload succeeded; no product-security inference is based on the harness
  failure.
- `UpdateCluster` emitted paired start/completion Admin Activity records. The start record contained
  the full unredacted startup script, exact update mask, caller and granted update permission.
  Compute `instances.update` records accompanied reconciliation. The synthetic object write did not
  appear because Storage Data Access was not enabled in the project.
- Security conclusion: expected functionality, not a vulnerability. Both update authority and
  caller `actAs` are required; the latter is rechecked even for a partial update that retains the
  existing identity. The technique is still useful because Service Account User does not itself
  mint a token, while the managed restart converts it into execution as that account.
- Restored a benign startup script before deletion. Then deleted the Cluster and verified zero
  matches across the API, Cloud Asset, VMs, disks, templates, instance groups, networks, subnets,
  firewalls, routers, addresses, network attachments, DNS zones and buckets. Removed the marker,
  bucket, caller/key/config, role and bindings, service-agent binding/account, and returned the API
  to its disabled baseline. Filestore remained at its pre-test enabled state.

## Rejected or bounded claims

- Do not claim `hypercomputecluster.clusters.update` alone executes as a retained service account;
  live authorization explicitly denied the partial update on missing `iam.serviceAccounts.actAs`.
- Do not claim the caller can choose or replace the VM identity through the current Cluster API;
  no such field exists in the current v1/v1beta schemas or update CLI.
- Do not claim direct token minting. The live caller with update plus actAs was denied
  `iam.serviceAccounts.getAccessToken`; execution consumed the VM metadata credential in place.
- Do not describe the path as stealthy. Admin Activity preserved the full malicious script, and the
  login fleet restart plus downstream Compute writes are conspicuous.
