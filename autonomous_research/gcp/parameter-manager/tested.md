# Parameter Manager — tested

Parameter Manager. Enum + post-exp pages.

## VERIFIED LIVE end-to-end (confused deputy)
- `parameterVersions.render` resolves embedded Secret Manager `__REF__` refs server-side as the
  parameter identity → a caller with ONLY `render`/`get`/`list` (no `secretmanager.versions.access`)
  reads the secret inline. Proof: SA with only render perms rendered the secret; the SAME SA got
  `IAM_PERMISSION_DENIED` on direct `secrets versions access`. Delegated reader is per-parameter (via
  `policyMember.iamPolicyUidPrincipal`, NOT the project service agent). ~30-45s IAM propagation.
  Custom-role render perm is alpha-stage but works. All infra torn down.
