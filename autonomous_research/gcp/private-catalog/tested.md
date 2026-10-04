# Service Catalog / Private Catalog — tested

## 2026-09-28 privilege-escalation audit

Documentation/schema-only audit; no catalog, version, association, deployment, or IAM policy was accessed or changed.

- Corrected the resource model: deployable legacy content is `Version.originalAsset`; Product updates are display metadata, not the template body.
- Retained only poisoning an existing attached/shared version. New unattached products and association widening require independent permissions and are not the minimum chain.
- Corrected role mapping: producer Editor/Admin/OrgAdmin contain product update; Manager does not.
- Corrected actuation identity: Deployment Manager uses the consumer project's Google APIs Service Agent, while Terraform solutions use a Cloud Build identity. Neither automatically has Owner.
- Bounded the chain by explicit consumer deployment, asset validation, selected project, and the actual actuation identity's permissions.
