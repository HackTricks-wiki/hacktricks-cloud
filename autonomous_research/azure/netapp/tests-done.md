# NetApp Files — Gap-analysis (2026-09-25)

Wiki: `az-netapp-files-post-exploitation.md` — **comprehensively covered**: export-policy mount
hijack, snapshot restore-to-new-volume, replication-out exfil (`authorizeReplication`+`breakReplication`),
`volumes/revert` rollback, snapshot/backup destruction, CMK-lockout (`changeKeyVault`/`migrateEncryption`),
SMB disruption (`resetCifsPassword`/`resetSmbPassword`).

Undocumented ops found in provider, judged **niche / low-priority**:
- `capacityPools/volumes/buckets/generateCredentials/action` + `generateAkvCredentials/action` —
  mints credentials for an ANF **object-storage bucket** (S3-compatible) = data-plane access to bucket
  contents (a listKeys-class primitive). BUT the ANF buckets/object-storage feature is a limited
  **preview** requiring registration — not available on the lab sub, so not lab-verifiable now, and
  low adoption. Revisit if the feature GAs.
- `capacityPools/caches/listPeeringPassphrases/action` — cross-cluster peering passphrase (ANF
  cache/FlexCache peering); niche, tied to the cache preview.

Conclusion: NetApp needs no wiki change now. ANF-buckets generateCredentials is the only real primitive
class missing and is blocked on preview availability.
