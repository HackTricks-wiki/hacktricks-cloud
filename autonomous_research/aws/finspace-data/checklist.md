# finspace-data credential vend — assessed 2026-09-26

## Verdict

Reasoned exclusion, not a public technique. Both operations return plaintext AWS-shaped temporary
credentials, but they belong to the deprecated FinSpace Dataset Browser plane and AWS will end all
FinSpace support on 2026-10-07. New customers have been closed since 2025-10-07. The installed AWS
CLI 2.34.45 service model marks both operations deprecated with `This method will be discontinued.`
Some retained Dataset Browser subpages still show an older 2025-03-26 discontinuation banner; that
conflicts with AWS's newer service-wide end-of-support page, which explicitly lets existing
pre-2025-10-07 customers continue until 2026-10-07. The current model therefore establishes only
backward-compatible deprecated availability, not availability to a new account.

`GetProgrammaticAccessCredentials` is still a genuine IAM-to-FinSpace authorization bridge: a role
with the IAM action can mint the credentials of the pre-associated FinSpace application user. It is
not an arbitrary-user or general AWS credential mint. The role ARN must already be registered on
that user, the user must already have FinSpace application permissions, and the documented use of
the resulting credentials is the FinSpace Data API. This can matter when the mapped FinSpace user is
a superuser or has sensitive dataset entitlements, but it is a preconfigured legacy access path,
not a broadly reachable AWS privilege escalation.

`GetExternalDataViewAccessDetails` is one step further inside the FinSpace authorization plane. It
is called with the first operation's FinSpace credentials, has no separate IAM action in the Service
Authorization Reference, and enforces the user's existing `Read Dataset Data` group permission. It
returns another access-key/secret/session-token tuple plus the managed S3 bucket/key for one existing
external data view. The user guide says these S3 credentials last 60 minutes. This makes authorized
data portable for direct S3 access, but does not grant a dataset the FinSpace user could not already
read.

## Exact boundary and prerequisites

Minimum IAM policy for the only IAM-authorized operation:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "finspace-api:GetProgrammaticAccessCredentials",
    "Resource": "arn:aws:finspace-api:REGION:ACCOUNT_ID:/credentials/programmatic"
  }]
}
```

The Service Authorization Reference lists no dependent actions and no FinSpace-specific condition
keys. The resource ARN does not contain the requested environment ID, so IAM alone cannot narrow the
allow to one environment within the same account and Region. Service-side prerequisites provide the
actual binding:

1. A legacy FinSpace Dataset Browser environment and its environment ID.
2. An enabled FinSpace user with programmatic access.
3. The exact same-account IAM **role** ARN stored as that user's `apiAccessPrincipalArn`.
4. The FinSpace user is a superuser or belongs to a permission group with the application permission
   `Get Temporary API Credentials`.

The request can ask for 1–60 minutes and the response returns `accessKeyId`, `secretAccessKey`,
`sessionToken`, and the effective `durationInMinutes`. AWS's general description says FinSpace API
credentials are user-unique and valid for 60 minutes; it does not document the omitted-parameter
default separately.

For the second operation, prerequisites are the FinSpace credentials above, an existing dataset and
external data view, and membership in a FinSpace group holding `Read Dataset Data` on that dataset.
The response contains plaintext `accessKeyId`, `secretAccessKey`, `sessionToken`, an epoch
`expiration`, and the precise S3 `bucket` and `key`. It is an internal FinSpace permission check, not
another `finspace-api:*` IAM permission.

## Logging

AWS says CloudTrail captures all FinSpace management and Data API calls. Expected records for these
calls are read-only management events with `eventSource=finspace-api.amazonaws.com` and the API name.
FinSpace Data API examples identify a FinSpace user by `userIdentity.principalId`; do not assume a
normal IAM ARN will always be present. The lab's pre-existing 2026-09-24 bounded probe confirms
`GetProgrammaticAccessCredentials` was recorded as `AwsApiCall`, `Management`, `readOnly=true`, with
the environment ID under both `requestParameters` and `additionalEventData`; it failed
`AccessDenied`, and no response secret was present. `GetExternalDataViewAccessDetails` was not live
verified.

Actual reads from the managed S3 location are separate FinSpace data events. AWS's example uses
`eventName=GetObject`, a principal session name containing the FinSpace user and dataset IDs, and an
`AWS::FinSpace::Environment` resource. Those object reads require CloudTrail data-event logging and
are not covered by Event History's default management-event view.

## Lab preflight and residue

- Account: `228478051196`, profile `ht-admin`.
- `ListEnvironments` and `ListKxEnvironments` returned `[]` in the two SCP-allowed Regions,
  `us-east-1` and `eu-west-1`.
- The organization SCP explicitly denied FinSpace inventory calls in the other advertised Regions.
- CloudTrail Event History contained no successful credential vend. The one historical bounded
  fake-environment call failed `AccessDenied`.
- No environment, user, permission group, dataset, data view, IAM resource, credential, or other
  state was created. Cleanup was unnecessary; residue is zero.

## Primary sources

- End of support: https://docs.aws.amazon.com/finspace/latest/userguide/amazon-finspace-end-of-support.html
- Temporary credentials and user/role binding: https://docs.aws.amazon.com/finspace/latest/userguide/temporary-credentials.html
- Using the Dataset Browser API: https://docs.aws.amazon.com/finspace/latest/data-api/fs-using-the-finspace-api.html
- `GetProgrammaticAccessCredentials`: https://docs.aws.amazon.com/finspace/latest/data-api/API_GetProgrammaticAccessCredentials.html
- `GetExternalDataViewAccessDetails`: https://docs.aws.amazon.com/finspace/latest/data-api/API_GetExternalDataViewAccessDetails.html
- IAM action/resource contract: https://docs.aws.amazon.com/service-authorization/latest/reference/list_finspace-data.html
- Creating an external data view (60-minute S3 credential lifetime): https://docs.aws.amazon.com/finspace/latest/userguide/create-data-view.html
- CloudTrail behavior: https://docs.aws.amazon.com/finspace/latest/userguide/logging-cloudtrail-events.html
