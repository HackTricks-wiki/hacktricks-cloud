# Container Apps / Jobs — Tests Done

Wiki: `az-container-instances-apps-jobs-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Override a Job execution template to consume a known secret / available MI | `Microsoft.App/jobs/start/action` | **CANT-TEST 2026-09-26** — vendor-confirmed behavior; lab managed environment never left `Waiting`, so no Job was created |

**Lab record (test #1, 2026-09-26 — provisioning wall):** Created tagged disposable RG
`htrc-cajob-3203f4` and requested a consumption-only Container Apps managed environment with Azure Monitor
logging (no dedicated workload profile and no Log Analytics workspace). The resource remained in
`provisioningState=Waiting` for ten minutes and later emitted a failed `managedEnvironments/write`; the Job,
secret, identity, and execution were therefore never created. Resource-group deletion was accepted, the
environment entered `ScheduledForDelete`, and the resource group later disappeared; a final inventory check
confirmed cleanup. The public technique remains grounded in Microsoft's explicit Jobs documentation and
Start REST schema; the end-to-end lab reproduction stays open in `checklist.md`.
