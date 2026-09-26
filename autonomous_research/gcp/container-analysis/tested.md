# Container Analysis — tested

Container Analysis / Artifact Analysis. New-service page: privesc 1 / post 3 / persist 3.

## VERIFIED LIVE
- Forged ATTESTATION occurrence accepted with HTTP 200 (no signature check at write) → supply-chain
  attestation forgery. `notes.setIamPolicy` self-grant confirmed. Audit: only `SetIamPolicy` in Admin
  Activity; `CreateNote`/`CreateOccurrence`/list = Data Access (silent). Teardown done.
