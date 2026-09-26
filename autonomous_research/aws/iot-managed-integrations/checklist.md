# IoT Managed Integrations (iotmanagedintegrations) — checklist (onboarding-gated frontier)

**Service:** "Managed integrations for AWS IoT Device Management" (API 2025-03-03, IAM prefix
`iotmanagedintegrations:`, endpoint `api.iotmanagedintegrations`). GA and ACCESSIBLE in **eu-west-1**
(list-managed-things / list-credential-lockers return {Items:[]}); NOT reachable in us-east-1.
Zero book coverage.

**Why not shipped / not live-tested (2026-09-25):** every provisioning/destination/connector primitive
requires the account to first call **`RegisterCustomEndpoint`** ("Account configuration record not found
this account, please call RegisterCustomEndpoint first"). There is **NO DeregisterCustomEndpoint /
DeleteCustomEndpoint** op — onboarding is IRREVERSIBLE account-level state. Per the teardown rule and the
cost/irreversibility exception, do NOT onboard the lab account just to test. Lab currently NOT onboarded
(GetCustomEndpoint = "No customEndPoint found"). Ship only after verifying against an already-onboarded
account (or a real engagement).

## High-confidence primitives (from AWS's authoritative botocore contract; verify before shipping)
- [ ] **`iotmanagedintegrations:CreateProvisioningProfile` → claim-cert private-key vend.** Output shape
      returns `ClaimCertificate` + `ClaimCertificatePrivateKey` (both `sensitive`). ProvisioningType
      FLEET_PROVISIONING|JITR. Possessing a claim cert + key lets an attacker run the fleet-provisioning
      flow to onboard ROGUE managed things (device impersonation / rogue-device injection / initial
      access). IMPACT IS CONDITIONAL on the provisioning template/policy the claim cert is authorized for
      (AWS fleet-provisioning claim certs are normally restricted to the provisioning API) — verify the
      end-to-end onboarding actually yields a usable device identity before claiming privesc.
      Min perm: `iotmanagedintegrations:CreateProvisioningProfile` (+ account onboarded). Persistence/
      initial-access. Cheap to verify (single Create+Delete) ONCE the account is onboarded.
- [x] **`iotmanagedintegrations:CreateDestination` + `iam:PassRole` — official contract reconciled;
      live delivery correctly deferred.** Requires `DeliveryDestinationArn` (currently Kinesis only),
      `DeliveryDestinationType=KINESIS`, and `RoleArn`. AWS's notification guide requires wildcard
      `iotmanagedintegrations:CreateDestination` plus PassRole on the exact delivery role with
      `iam:PassedToService=iotmanagedintegrations.amazonaws.com`. The role trusts that same service
      principal, should constrain `aws:SourceAccount` and `aws:SourceArn`, and needs only
      `kinesis:PutRecord` on the destination stream. `CreateNotificationConfiguration` is a separate
      permission and operation that selects the event type and actually routes notifications to the
      named destination. A caller holding only CreateDestination can therefore create a destination
      definition but cannot independently activate a new event feed. The primary conditional impact
      is future device-event exfiltration to a Kinesis stream the delivery role can write; this is not
      arbitrary execution as the role. The Service Authorization Reference now also lists PassRole as
      a CreateDestination dependency. Do not run the two-sided probe until an already-onboarded account
      is available because `RegisterCustomEndpoint` remains irreversible in the current API surface.
- [ ] **`iotmanagedintegrations:PutDefaultEncryptionConfiguration`** — sets the ACCOUNT-WIDE encryption
      config (encryptionType + kmsKeyArn). Swapping to an attacker-controlled KMS key = potential data
      access / defense evasion at account scope. Account-level change — test with extreme care (may not
      be cleanly reversible to prior state). Currently state=ENABLED default in lab.
- [x] **`GetConnectorDestination` is a reference getter, not a credential vend (reconciled
      2026-09-26).** `SecretsManager` and each general-authorization material contain only a secret
      ARN and version ID. OAuth config contains endpoints, scope, authentication scheme, and redirect
      URL, not a client secret/access token/refresh token. Minimum IAM is wildcard
      `iotmanagedintegrations:GetConnectorDestination`; a separate Secrets Manager authorization
      (`GetSecretValue`, plus `kms:Decrypt` for a customer-managed key) is always required to obtain
      the referenced value.
- [x] **Credential-locker getters are metadata only (reconciled 2026-09-26).**
      `GetCredentialLocker` returns Id/Arn/Name/CreatedAt/Tags and is scopeable to the exact
      `credential-locker/IDENTIFIER` ARN. `GetManagedThing` and list summaries can return a
      `CredentialLockerId`, but the current API has no customer operation that reads locker contents;
      more IoT read permissions do not turn the ID into plaintext. One distinct exception is
      `GetManagedThing.DeviceSpecificKey`, a model-sensitive plaintext Z-Wave activation key. It is
      not locker content or a cloud credential, and practical impact remains unverified without a
      physical/onboarded Z-Wave fixture. Details and zero-residue preflight are in
      `../_lens-sweeps/credential-reference-getters-2026-09-26.md`.
- [ ] **Account associations** (`RegisterAccountAssociation`/`ListAccountAssociations`/`GetAccountAssociation`)
      link third-party (C2C) cloud accounts — recon of connected external device clouds; possible
      hijack of the association's OAuth linkage.

## Current official sources

- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_Operations.html>
- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_RegisterCustomEndpoint.html>
- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetConnectorDestination.html>
- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_SecretsManager.html>
- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetCredentialLocker.html>
- <https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetManagedThing.html>
- <https://docs.aws.amazon.com/iot-mi/latest/devguide/managedintegrations-notifications.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_iot-managed-integrations.html>
