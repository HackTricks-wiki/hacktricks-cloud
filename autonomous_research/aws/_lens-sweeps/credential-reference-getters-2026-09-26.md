# Credential-reference getters — assessed 2026-09-26

## Verdict

Neither `license-manager-linux-subscriptions:GetRegisteredSubscriptionProvider` nor the AWS IoT
Managed Integrations getters for connector destinations and credential lockers is a direct
credential vend. The current official API contracts return a Secrets Manager ARN/version or an
IoT Managed Integrations resource identifier, not the referenced secret value.

Where the response points to Secrets Manager, disclosure of the value is a separate authorization
decision: the caller must also be allowed to call `secretsmanager:GetSecretValue` on the referenced
secret (and `kms:Decrypt` when the secret uses a customer-managed KMS key). A credential-locker ID
is even less useful for disclosure: the current service exposes no customer API for reading locker
contents. `GetCredentialLocker` returns metadata only.

The model scan found one distinct exception in `GetManagedThing`: `DeviceSpecificKey` is returned as
a sensitive string and AWS describes it as a Z-Wave device-specific key used during activation.
That field is not credential-locker content and is not an AWS or third-party-cloud credential. Its
practical impact is conditional on a Z-Wave device and activation workflow, and the unonboarded lab
has no managed thing with which to verify it. Keep it as a niche device-onboarding lead; it does not
justify a public credential-vend technique on current evidence.

## License Manager Linux Subscriptions

### Returned data and authorization boundary

`GetRegisteredSubscriptionProvider` returns provider status/metadata and `SecretArn`. AWS defines
that field as the ARN of the Secrets Manager secret containing the registered provider access token;
for RHEL, the stored value is the Red Hat offline token. It never returns `SecretString` or
`SecretBinary`.

The minimum permission for the metadata operation is:

```json
{
  "Effect": "Allow",
  "Action": "license-manager-linux-subscriptions:GetRegisteredSubscriptionProvider",
  "Resource": "arn:aws:license-manager-linux-subscriptions:REGION:ACCOUNT:subscription-provider/PROVIDER_ID"
}
```

The current Service Authorization Reference lists the `subscription-provider` resource as required,
supports `aws:ResourceTag/${TagKey}`, and lists no dependent action. The read does not implicitly
grant access to the secret. Reading the Red Hat token requires a separate Secrets Manager allow:

```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "THE_RETURNED_SECRET_ARN"
}
```

Add `kms:Decrypt` on the exact KMS key when a customer-managed key encrypts the secret. Resource
policies and cross-account authorization rules still apply; learning the ARN does not bypass them.

### Prerequisites and lifecycle

The account must first enable Linux subscription discovery, then register a supported provider.
AWS currently supports Red Hat for this API. RHSM registration requires a Red Hat customer-account
offline token, either supplied for License Manager to store or already stored in Secrets Manager.
The service-linked role `AWSServiceRoleForAWSLicenseManagerLinuxSubscriptionsService` retrieves
secrets and uses KMS keys tagged `LicenseManagerLinuxSubscriptions=enabled`; License Manager uses the
offline token to mint temporary Red Hat access tokens when retrieving subscription data.

This is a current License Manager feature with current API and user-guide documentation and no
announced retirement. It is a provider-inventory getter layered over Secrets Manager, not a secret
read primitive.

## IoT Managed Integrations

### Connector destinations

`GetConnectorDestination` returns connector metadata plus:

- `SecretsManager`: exactly `arn` and `versionId`;
- `AuthConfig.GeneralAuthorization[*].SecretsManager`: the same two-field reference; and
- OAuth endpoint/configuration metadata such as authorization URL, token URL, scope, authentication
  scheme, and redirect URL.

It does not return an OAuth client secret, access token, refresh token, `SecretString`, or
`SecretBinary`. Minimum IAM is `iotmanagedintegrations:GetConnectorDestination` with `Resource: "*"`;
the Service Authorization Reference defines no resource type or dependent action for this getter.
The returned ARN/version becomes plaintext only through a separately authorized
`secretsmanager:GetSecretValue` request (plus KMS authorization where applicable).

### Credential lockers and managed things

`GetCredentialLocker` returns only `Id`, `Arn`, `Name`, `CreatedAt`, and tags. Minimum IAM is
`iotmanagedintegrations:GetCredentialLocker` on:

```text
arn:aws:iotmanagedintegrations:REGION:ACCOUNT:credential-locker/IDENTIFIER
```

`GetManagedThing` can return a `CredentialLockerId`. Minimum IAM is
`iotmanagedintegrations:GetManagedThing` on:

```text
arn:aws:iotmanagedintegrations:REGION:ACCOUNT:managed-thing/IDENTIFIER
```

Both resource-scoped actions support `aws:ResourceTag/${TagKey}`. No dependent IAM actions are
listed. `ListCredentialLockers` and `ListManagedThings` are wildcard list permissions and likewise
return only metadata/identifiers. There is no second customer-facing "get locker secret" operation
in the current API, so additional read permission cannot turn the locker ID into plaintext through
the control plane.

`GetManagedThing.DeviceSpecificKey` is the exception noted above. It is plaintext activation
material directly returned by `iotmanagedintegrations:GetManagedThing`, not a dereference of
`CredentialLockerId`; no second permission is modeled. The official description limits it to
Z-Wave devices and device activation. Do not generalize it into an AWS credential or claim usable
device takeover without an end-to-end fixture.

### Prerequisites and lifecycle

Managed Integrations became generally available on 2025-06-26 and remains a current AWS IoT Device
Management feature. AWS currently documents support in `ca-central-1` and `eu-west-1`. Meaningful
resources require account setup through `RegisterCustomEndpoint`; the current API has no matching
delete/deregister operation, so the lab was not onboarded merely to test these getters.

## Read-only lab preflight

Account `228478051196`, profile `ht-admin`:

- `GetServiceSettings` reported `LinuxSubscriptionsDiscovery: Disabled` with no source Regions in
  both `us-east-1` and `eu-west-1`.
- `ListRegisteredSubscriptionProviders` in both Regions therefore failed with the expected
  validation message that the account must first be onboarded. No active provider was available to
  query through the service; this error alone does not inventory any orphaned Secrets Manager secret
  that could remain after a prior deactivation.
- In `eu-west-1`, `GetCustomEndpoint` returned `ResourceNotFoundException`, while
  `ListCredentialLockers`, `ListConnectorDestinations`, and `ListManagedThings` all returned empty
  lists.
- No registration, endpoint onboarding, resource creation, secret read, or device operation was
  attempted. Cleanup was unnecessary; residue is zero.

## Primary sources

- https://docs.aws.amazon.com/license-manager-linux-subscriptions/latest/APIReference/API_GetRegisteredSubscriptionProvider.html
- https://docs.aws.amazon.com/license-manager-linux-subscriptions/latest/APIReference/API_RegisteredSubscriptionProvider.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_license-manager-linux-subscriptions.html
- https://docs.aws.amazon.com/license-manager/latest/userguide/linux-subscriptions-manage-discovery.html
- https://docs.aws.amazon.com/license-manager/latest/userguide/linux-subscriptions-role.html
- https://docs.aws.amazon.com/license-manager/latest/userguide/settings-linux-subscriptions.html
- https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetConnectorDestination.html
- https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_SecretsManager.html
- https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetCredentialLocker.html
- https://docs.aws.amazon.com/iot-mi/latest/APIReference/API_GetManagedThing.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_iot-managed-integrations.html
- https://docs.aws.amazon.com/iot-mi/latest/devguide/what-is-managedintegrations.html
- https://aws.amazon.com/about-aws/whats-new/2025/06/managed-integrations-aws-iot-device-management/
