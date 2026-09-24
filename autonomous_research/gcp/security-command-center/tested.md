# Security Command Center — tested

Security Command Center (SCC). Covered (config-tamper post-ex, Security Posture tamper persistence).

## CRITICAL correction applied (do NOT regress)
- `SetMute`, `SetFindingState`, `UpdateFinding`, `BulkMuteFindings`, `Create/Update/DeleteNotificationConfig`
  are **DATA_WRITE (off by default), NOT ADMIN_WRITE** — inverted the stealth story (muting + severing
  the Pub/Sub SIEM feed = no audit trail by default). Mute-config CRUD, BigQuery-export CRUD, source
  `SetIamPolicy` are correctly ADMIN_WRITE. `sources.setIamPolicy` also in `securitycenter.sourcesAdmin`.

## Standing item (REST-only)
- `integratedvulnerabilityscannersettings` / `rapidvulnerabilitydetectionsettings` — REST-only, deferred.
