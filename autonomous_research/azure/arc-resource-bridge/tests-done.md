# Azure Arc Resource Bridge — Tests Done

| # | Hypothesis / check | Method | Status |
|---|--------------------|--------|--------|
| 1 | Credential-export Actions exist and expose security-sensitive fields | Microsoft provider-permission catalog, CLI reference, and SDK response models | **SOURCE-VALIDATED 2026-09-26** |
| 2 | Deployment/onboarding built-in roles include the export Actions | Live `az role definition list` against the lab tenant | **PASS 2026-09-26** |
| 3 | Exact Action invocation and returned effective privileges | Disposable Arc Resource Bridge | **BLOCKED BY LAB TOPOLOGY** — no appliance or on-premises substrate exists |

## Source and tenant validation (2026-09-26)

Microsoft's current permission catalog defines:

- `Microsoft.ResourceConnector/appliances/listKeys/action` — get appliance cluster customer-user
  keys.
- `Microsoft.ResourceConnector/appliances/listClusterUserCredential/action` — get an appliance
  cluster-user credential.

The stable `2022-10-27` SDK models show that `listKeys` can return kubeconfigs, a map containing
customer SSH public/private keys and a certificate, and artifact-upload profiles. The SDK method
documentation clarifies that an empty `artifactType` returns no artifact endpoint; supported values
and endpoint capability remain untested. The
`listClusterUserCredential` result can return kubeconfigs plus `hybridConnectionConfig`, described
as a rendezvous endpoint and notification-service Listener access token. The CLI documentation
states that the default `get-credentials` mode retrieves customer credentials to files, while
`--partner true` prints private-cloud RP/service credentials to stdout.

Read-only role-definition queries in subscription `azure-labs-owCfs7hi` found:

- Azure Arc VMware Private Clouds Onboarding (`67d33e57-3129-45e6-bb0b-7cc522f762fa`):
  `listClusterUserCredential` only.
- Azure Stack HCI Administrator (`bda0d508-adf1-4af0-9c28-88919fc3ae06`): both Actions.
- Azure Stack HCI Device Management Role (`865ae368-6a45-4bd1-8fbf-0d5151f56fc1`): both Actions.
- Azure Resource Bridge Deployment Role (`7b1f81f9-4196-4058-8aae-762e593270df`): both Actions.

## Lab limitation and cleanup

The subscription contained no `Microsoft.ResourceConnector/appliances` resources and the provider
was `NotRegistered`. A valid bridge requires an on-premises VMware, SCVMM, or Azure Local substrate;
none was available. No provider was registered, no extension installed, no role assignment made,
and no Azure resource created, so there was nothing to clean up. Live authorization, returned RBAC,
credential lifetime, cross-bridge isolation, and telemetry remain explicitly untested.
The higher-level CLI wrapper's preliminary/helper permissions also remain untested, so only the raw
REST Action is treated as the proposed exact minimum.

No zero-day finding exists from this pass. The unresolved vulnerability hypotheses remain in
`checklist.md` and must not be reported without a reproducible live failure.

Official references:

- <https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/hybrid-multicloud#microsoftresourceconnector>
- <https://learn.microsoft.com/en-us/cli/azure/arcappliance?view=azure-cli-latest#az-arcappliance-get-credentials>
- <https://learn.microsoft.com/en-us/java/api/com.azure.resourcemanager.resourceconnector.models.appliancelistkeysresults?view=azure-java-stable>
- <https://learn.microsoft.com/en-us/java/api/com.azure.resourcemanager.resourceconnector.models.appliancelistcredentialresults?view=azure-java-stable>
- <https://learn.microsoft.com/en-us/dotnet/api/azure.resourcemanager.resourceconnector.resourceconnectorapplianceresource?view=azure-dotnet-preview>
