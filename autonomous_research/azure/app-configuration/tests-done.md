# App Configuration — Tests Done

Wiki: `az-app-configuration-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `ListKeys/action` → standalone shared-key read/write and configuration poisoning | `Microsoft.AppConfiguration/configurationStores/ListKeys/action` | **WORKS** — pre-existing lab verification on the wiki |
| 2 | Immutable snapshot as loot persistence after the live key is deleted | Entra: `keyValues/read` + `snapshots/write` + `snapshots/read`; HMAC: read-write store key | **WORKS — lab-verified 2026-09-26 with HMAC** |

**Lab record (test #2, 2026-09-26 — snapshot loot persistence):** Created Free-tier store
`htrcappcfg9fa6ef` in disposable RG `htrc-appcfg-9fa6ef`. With a read-write connection string, wrote only
the fake canary `prod/db-password=HT_FAKE_ROTATED_SECRET_9fa6ef`, created snapshot
`pre-rotation-9fa6ef`, waited for `status=ready`, then deleted the live key. A live-key query returned
`0` items, while `az appconfig kv list --snapshot pre-rotation-9fa6ef` returned the deleted value intact.
This proves that deleting live configuration does not evict snapshot-held copies. Rotation was not part
of this lab test; snapshot immutability means rotation cannot rewrite the captured historical value.

**Logs:** the subscription Activity Log showed `configurationStores/write` and
`configurationStores/listKeys/action`, but no snapshot create/read or key-value delete operation. Those
are App Configuration data-plane requests and require the store's resource diagnostics, which are off by
default. **Teardown:** the resource group was deleted, the soft-deleted store was purged, and both
`az group exists` and `az appconfig list-deleted` confirmed zero residue.
