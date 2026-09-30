# AWS Transfer Family research ledger

Research date: 2026-09-26/27. Region: `us-east-1`. Authorized profile: `ht-admin`, resolving to the expected `ChackBotAdministratorRole` assumed-role session. No other account/profile was used.

## Scope and publication decisions

Reviewed current server, service-managed user, custom IdP, SFTP/AS2 connector, workflow, certificate/profile, host-key, and web-app surfaces. The public pages contain only verified or high-confidence documented behavior:

- `src/pentesting-cloud/aws-security/aws-services/aws-transfer-family-enum.md`
- `src/pentesting-cloud/aws-security/aws-privilege-escalation/aws-transfer-family-privesc/README.md`
- `src/pentesting-cloud/aws-security/aws-post-exploitation/aws-transfer-family-post-exploitation/README.md`

No unexpected AWS vulnerability was identified. Nothing was written to `/home/tester/cloud_bb/aws`.

## Live validation results

All fixtures used a unique `ht-transfer-audit-<timestamp>-<random>` prefix and research tag. Before the first run, `ListServers`, `ListConnectors`, `ListProfiles`, `ListCertificates`, `ListWorkflows`, and `ListWebApps` were empty.

Validated:

1. A custom Lambda IdP and `TestIdentityProvider`:
   - no password returned the role ARN, physical home, and SSH public key;
   - wrong password returned `{}` and an authentication-failure message;
   - correct password returned the role and home mapping.
2. `ImportSshPublicKey` added an alternate key to a service-managed user, and the key authenticated over SFTP and listed an existing object through the user's role.
3. A managed COPY workflow attached with an execution role ran on upload and copied the uploaded object to the configured prefix.
4. An SFTP connector using a Secrets Manager private key and a delegated access role reached `TestConnection=OK`.
5. `StartDirectoryListing` returned a listing ID.
6. S3-to-SFTP and SFTP-to-S3 `StartFileTransfer` calls returned transfer IDs and `ListFileTransferResults` reported `COMPLETED`.
7. `StartRemoteMove` and `StartRemoteDelete` returned distinct `MoveId` and `DeleteId` values.
8. CloudTrail Event History contained connector-scoped `StartDirectoryListing`, `StartFileTransfer`, `ListFileTransferResults`, `StartRemoteMove`, and `StartRemoteDelete` management events. `StartRemoteDelete` appeared after a short Event History delivery delay.

Implementation details discovered during validation:

- Connector S3 paths use `/bucket/key` or `/bucket/prefix`, not `s3://...`.
- Directory output/local directory prefixes with a trailing slash were rejected in this test.
- SFTP connectors reject ED25519 host keys and EdDSA user private keys even though Transfer servers accept ED25519 keys. RSA worked.
- A physical home plus absolute connector paths addressed the storage root rather than the user's landing directory. A `LOGICAL` mapping from `/` to the desired S3 prefix made absolute connector move/delete paths behave as intended.
- `StartRemoteMove` returns `MoveId`; `StartRemoteDelete` returns `DeleteId`.
- The custom connector logging role used during validation did not cause `/aws/transfer/<connector-id>` to appear. The public page therefore treats connector CloudWatch logs as configuration-dependent and EventBridge outcomes as automatic.

## Exact authorization conclusions

Authoritative source: [AWS Transfer Family service authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_transfer.html).

| Capability | Caller-side minimum |
| --- | --- |
| Add a key to a known service-managed user | `transfer:ImportSshPublicKey` on the user ARN; no `iam:PassRole` |
| Invoke a known custom IdP test | `transfer:TestIdentityProvider` on the synthetic user ARN; no direct backend invoke permission |
| Execute an existing connector | The exact connector-scoped `transfer:Start*` action; no caller `PassRole`, secret read, or direct S3 permission |
| Read a connector's remote credential | `secretsmanager:GetSecretValue`, plus `kms:Decrypt` for a customer KMS key |
| Create user/access/agreement/connector/server/web app with roles | Matching create action plus `iam:PassRole`; `TagResource` when tagging |
| Attach a workflow execution role | `transfer:UpdateServer` plus `iam:PassRole` on the execution role |
| Create a workflow definition | `transfer:CreateWorkflow`; no role is passed at this step |
| Update access/agreement/connector/server/user/web app role-bearing configuration | Matching update action; AWS lists `iam:PassRole` as dependent |
| Replace AS2 partner profile certificate | `transfer:ImportCertificate` plus `transfer:UpdateProfile`; no role pass |

## Negative findings / limits

- Describe APIs do not return private host keys or certificate private keys.
- `DescribeConnector` returns the secret identifier, not its value.
- Importing a host key alone grants no user/storage access. The oldest key of a given type is active and client trust still matters.
- Transfer web-app creation is not anonymous or direct S3 access. Identity Center assignment and S3 Access Grants are separate required controls, and web-app S3 buckets must be same-account.
- Transfer resources have no general cross-account resource policy for direct API invocation. Cross-account data access occurs through delegated roles, S3/secret resource policies, or the external protocol peer.
- AS2 messages do not trigger managed workflows attached to a server.

## Telemetry conclusions

- All Transfer APIs are CloudTrail management events, including failed requests.
- A start event proves request acceptance, not asynchronous completion.
- SFTP connector outcomes are automatically sent to the default EventBridge bus. File-transfer results can also be queried for up to seven days.
- Server/connector CloudWatch logs depend on valid logging configuration.
- S3 object activity needs CloudTrail S3 data events; it is not included in management Event History by default.
- Web-app sign-in appears under `signin.amazonaws.com`; Access Grants vending appears under S3/S3 Control with `onBehalfOf` identity context.
- API Gateway execution logging for custom password IdPs can capture passwords and is itself a credential-exposure risk.

## Cleanup proof

The disposable script uses a cleanup trap and explicit generated-prefix guards. After the successful run, independent list calls returned zero:

- Transfer servers, connectors, workflows, profiles, certificates, and web apps;
- IAM roles beginning `ht-transfer-audit-`;
- Lambda functions and Lambda log groups beginning `ht-transfer-audit-`;
- Secrets Manager secrets beginning `aws/transfer/ht-transfer-audit-`;
- S3 buckets beginning `ht-transfer-audit-`;
- generated Transfer log groups.

The only retained AWS-side evidence is normal immutable audit/event history. Locally retained files are the safe reproduction script, Lambda fixture source, and a non-sensitive test object.

## Reproduction

`live_validate.sh` hard-codes `us-east-1`, JSON output, the authorized profile allowlist, the expected assumed-admin role, unique resource prefixes, and cleanup. Use `CONNECTOR_ONLY=1` to skip the already validated custom-IdP/workflow phase.

The script creates billable Transfer endpoints briefly. Run it only in an authorized research account and always independently verify the generated prefix after completion.
