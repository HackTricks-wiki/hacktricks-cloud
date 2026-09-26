# Service Management — tested and verified

Last checked: 2026-09-26

## Audit-method and rollout-scope audit — CORRECTED

- Current official audit documentation maps config deployment to
  `SubmitConfigSource`/`CreateServiceConfig` and `CreateServiceRollout`, not to a generic
  `services.update` log method. All are Admin Activity and logged by default.
- Cloud Endpoints ESP/ESPv2 with managed rollout automatically adopts the newest service config.
- API Gateway does not share that update behavior: its API configs are immutable and each deployed
  gateway pins one config. Changing the definition requires creating another API Gateway config and
  explicitly updating the gateway. Removed the unsupported API Gateway auto-pull claim.
- Added categorical stealth ratings to all three retained Service Management techniques.
- The authorized lab has `servicemanagement.googleapis.com` disabled. A read-only service list
  returned `SERVICE_DISABLED`; the API was not enabled and no infrastructure was created.
