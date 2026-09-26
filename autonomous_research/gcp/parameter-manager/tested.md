# Parameter Manager — tested

Parameter Manager. Enum + post-exp pages.

## VERIFIED LIVE end-to-end (confused deputy)
- `parameterVersions.render` resolves embedded Secret Manager `__REF__` refs server-side as the
  parameter identity → a caller with ONLY `render`/`get`/`list` (no `secretmanager.versions.access`)
  reads the secret inline. Proof: SA with only render perms rendered the secret; the SAME SA got
  `IAM_PERMISSION_DENIED` on direct `secrets versions access`. Delegated reader is per-parameter (via
  `policyMember.iamPolicyUidPrincipal`, NOT the project service agent). ~30-45s IAM propagation.
  Custom-role render perm is alpha-stage but works. All infra torn down.

## 2026-09-26 — visibility and new-feature check
- Rechecked the live-verified render disclosure against the current [Parameter Manager audit reference](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/audit-logging): `RenderParameterVersion` and `GetParameterVersion` are `DATA_READ` (off by default), while version create/update and parameter update are `ADMIN_WRITE` (always logged). Added explicit stealth ratings to both post-exploitation techniques. No new lab resource used.
- Reviewed the July 2026 parameter-template preview and September 2026 tag support. Template rendering with `__REF__()` follows the existing delegated-render family already mentioned in the enum page; tag-based IAM conditions follow the existing tag-binding permission family. No distinct technique warranted without a new permission boundary.
