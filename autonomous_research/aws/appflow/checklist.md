# AppFlow — checklist (potential, non-duplicate)
- [ ] RegisterConnector/CreateConnectorProfile with attacker CustomConnector endpoint -> capture data flowing through a custom connector (needs custom connector Lambda). Low-med value.
- [ ] CreateFlow with SaaS source + EventBridge destination -> pump SaaS data onto an attacker-readable event bus (if EventBridge cross-account rule exists). Chain w/ EventBridge.
- [ ] metadataCatalogConfig (Glue Data Catalog) on CreateFlow -> register exfil schema into Glue; recon value.
- [x] UpdateFlow repoint of source/dest -> BLOCKED for S3 (validator). Recorded in tested.md.
