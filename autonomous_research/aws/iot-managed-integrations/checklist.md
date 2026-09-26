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
- [ ] **`iotmanagedintegrations:CreateDestination` + `iam:PassRole`.** Requires DeliveryDestinationArn
      (KINESIS only), DeliveryDestinationType, RoleArn. Repoint device event/notification delivery to an
      attacker-owned Kinesis stream using a passed role => device-event exfiltration + PassRole. Verify
      the PassRole gate with the bogus-resource two-sided probe (once onboarded). Delivery-role value is
      limited unless the role is independently useful; primary value is event exfil.
- [ ] **`iotmanagedintegrations:PutDefaultEncryptionConfiguration`** — sets the ACCOUNT-WIDE encryption
      config (encryptionType + kmsKeyArn). Swapping to an attacker-controlled KMS key = potential data
      access / defense evasion at account scope. Account-level change — test with extreme care (may not
      be cleanly reversible to prior state). Currently state=ENABLED default in lab.
- [ ] **`GetConnectorDestination`** returns AuthConfig / SecretsManager / OAuthCompleteRedirectUrl for
      C2C connectors. Check whether AuthConfig leaks OAuth client secrets/tokens in the response or only
      SecretsManager references (given the confirmed AWS redaction pattern, likely references only).
- [ ] **Credential lockers** (`CreateCredentialLocker`/`GetCredentialLocker`/`ListCredentialLockers`) —
      store device credentials. GetCredentialLocker output = metadata only (Id/Arn/Name/Tags), no secret
      => likely NOT a disclosure vector, but confirm.
- [ ] **Account associations** (`RegisterAccountAssociation`/`ListAccountAssociations`/`GetAccountAssociation`)
      link third-party (C2C) cloud accounts — recon of connected external device clouds; possible
      hijack of the association's OAuth linkage.
