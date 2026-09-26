# AWS Backup Gateway `PutHypervisorPropertyMappings` review

## Verdict — reasoned exclusion (2026-09-26)

`backup-gateway:PutHypervisorPropertyMappings(IamRoleArn)` is a constrained VMware metadata-sync
helper, not a general PassRole execution primitive. It stores up to ten mappings from existing VMware
category/tag pairs to AWS tag key/value pairs on Backup Gateway virtual-machine resources. A separate
`StartVirtualMachinesMetadataSync` request applies the mappings.

The role is not used to read VM disks, retrieve hypervisor credentials, restore backups, or invoke
arbitrary AWS actions. AWS's purpose-built managed policy grants only `ListTagsForResource`,
`TagResource`, and `UntagResource` on `arn:aws:backup-gateway:*:*:vm/*`. Passing an overprivileged role
does not expose its credentials and there is no documented input that selects arbitrary API calls.

The only plausible security effect is constrained tag manipulation: a caller who can both replace the
mapping and start metadata sync may add/remove mapped AWS tags on discovered Backup Gateway VM
resources. This could affect tag-based backup-plan selection or unusually designed ABAC, but it needs
matching VMware tags and existing tag-dependent policy. It does not itself read backup data or export
VM data, so it does not clear the bar for a distinct public privesc/post-exploitation technique.

## Exact authorization and trust boundary

The Service Authorization Reference defines:

- `backup-gateway:PutHypervisorPropertyMappings` on the exact hypervisor ARN, plus
  `iam:PassRole` on the supplied role with
  `iam:PassedToService = backup-gateway.amazonaws.com`.
- `backup-gateway:StartVirtualMachinesMetadataSync` on the same hypervisor, also with dependent
  `iam:PassRole` for `backup-gateway.amazonaws.com`, to make the stored mapping take effect.
- `aws:ResourceTag/<key>` is available for scoping the hypervisor actions; Backup Gateway defines no
  service-specific condition key for choosing mapping keys/values.

Minimum policy shape for the complete write-and-apply path:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "backup-gateway:PutHypervisorPropertyMappings",
        "backup-gateway:StartVirtualMachinesMetadataSync"
      ],
      "Resource": "arn:aws:backup-gateway:<region>:<account-id>:hypervisor/<hypervisor-id>"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::<account-id>:role/<metadata-sync-role>",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "backup-gateway.amazonaws.com"
        }
      }
    }
  ]
}
```

AWS's documented trust policy allows both service principals because Backup Gateway performs the
metadata discovery/sync while AWS Backup consumes the resulting VM metadata:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": [
        "backup.amazonaws.com",
        "backup-gateway.amazonaws.com"
      ]
    },
    "Action": "sts:AssumeRole"
  }]
}
```

The current AWS-managed service-role policy is exactly:

- `backup-gateway:ListTagsForResource` on Backup Gateway `vm/*` ARNs.
- `backup-gateway:TagResource` and `backup-gateway:UntagResource` on the same `vm/*` ARNs.

The VMware username/password belong to the hypervisor configuration and are encrypted separately by
AWS-owned or customer-managed KMS keys. `PutHypervisorPropertyMappings` neither accepts nor returns
those credentials. Its response contains only the hypervisor ARN; `GetHypervisorPropertyMappings`
returns the mapping and IAM role ARN, not secrets.

## Prerequisites, cost, and cleanup

A real fixture requires all of the following:

- A compatible VMware vCenter environment with VMware-tagged VMs.
- The Backup Gateway OVF deployed and activated, current enough to support metadata sync, connected to
  the vCenter/hypervisor, and able to reach AWS endpoints.
- An imported hypervisor configuration containing vCenter credentials and an associated online
  gateway.
- A metadata-sync role with the trust and VM-tag permissions above.

AWS Backup lists no setup charge or minimum fee; billing is for backup storage, restores, transfer,
and evaluations. The mapping call itself has no documented line-item charge. A test fixture is still
not cheap/disposable in practice because it needs customer-managed VMware infrastructure and a
deployed gateway appliance. Running actual backups would incur normal VMware backup storage charges.

There is no `DeleteHypervisorPropertyMappings` API. A mapping can be overwritten, and the console
supports removing entries before saving, but a safe test on a shared hypervisor would need to capture
and restore the exact original mapping and role. A fully disposable fixture would require deleting the
test hypervisor and gateway and removing the external gateway appliance. This review deliberately
created none of them.

## Read-only inventory and bounded probe

Authorized account `228478051196`, profile `ht-admin`, `us-east-1`:

- `ListGateways`, `ListHypervisors`, and `ListVirtualMachines` all returned empty lists.
- No IAM role currently trusts `backup-gateway.amazonaws.com`.
- No user, group, or role has the
  `AWSBackupGatewayServiceRolePolicyForVirtualMachineMetadataSync` managed policy attached.
- A syntactically valid `GetHypervisorPropertyMappings` against the synthetic ARN returned
  `ResourceNotFoundException / HypervisorNotFound`.
- One bounded `PutHypervisorPropertyMappings` against that same nonexistent ARN returned
  `ValidationException / OutdatedGateway`. The service checks gateway-version readiness before the
  missing-hypervisor boundary. Re-listing gateways and hypervisors remained empty, confirming that no
  mapping or resource was created.

The bounded put used a pre-existing role ARN solely as a syntactically valid parameter; that role does
not trust Backup Gateway and was not changed. No gateway, hypervisor, VM, IAM role/policy, KMS grant,
backup, or mapping was created. Cleanup residue is zero.

## Logging

AWS documents that CloudTrail captures all AWS Backup API calls. The bounded failed call appeared as
`eventSource=backup-gateway.amazonaws.com`, `eventName=PutHypervisorPropertyMappings`,
`eventType=AwsApiCall`, `eventCategory=Management`, `managementEvent=true`, and `readOnly=false`.
Its `requestParameters` contained the target hypervisor ARN, full supplied IAM role ARN, and all four
VMware/AWS mapping fields; the event also recorded `ValidationException` and the gateway-version error.
`responseElements` was null because the call failed.

Applying a real mapping should additionally produce `StartVirtualMachinesMetadataSync` and the
service-role `ListTagsForResource`, `TagResource`, and `UntagResource` activity required by the
discovered VM tags. Those successful-path events were not live-tested because no fixture exists; do
not infer successful role assumption from the failed readiness check. CloudWatch Logs can optionally
record gateway/hypervisor operational and connectivity errors.

## Completed checks

- [x] Inspect installed AWS CLI 2.34.45 operation/input/output models.
- [x] Confirm exact hypervisor resource scoping and both dependent PassRole relationships from the
  current Service Authorization Reference.
- [x] Retrieve the current managed metadata-sync role policy and documented trust principals.
- [x] Establish that the role only synchronizes AWS tags on Backup Gateway VM resources.
- [x] Separate encrypted hypervisor credentials and VM backup data from the mapping role.
- [x] Inventory gateways, hypervisors, VMs, trusted roles, and managed-policy attachments.
- [x] Run one bounded nonexistent-resource put and re-inventory for zero residue.
- [x] Record prerequisites, cost model, cleanup constraints, and the failed call's CloudTrail fields.

## Revisit only if an existing disposable VMware fixture is supplied

- [ ] Use an already-deployed current gateway and a synthetic VM with a unique VMware canary tag.
- [ ] Test an isolated caller with only exact-hypervisor put/start plus exact-role PassRole.
- [ ] Confirm put alone stores but does not apply the tag; then confirm start sync applies only the
  expected Backup Gateway VM tag.
- [ ] Deny unrelated actions in the passed role and prove no secret/data read or broader call occurs.
- [ ] Capture CloudTrail for put, start, role assumption, and VM tag/untag operations.
- [ ] Restore the original mapping/role byte-for-byte or delete the fully test-owned hypervisor and
  gateway, then independently verify no VM tags, IAM attachments, KMS grants, or gateway residue.

## Official sources

- <https://docs.aws.amazon.com/aws-backup/latest/APIReference/API_BGW_PutHypervisorPropertyMappings.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/API_BGW_GetHypervisorPropertyMappings.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/API_BGW_StartVirtualMachinesMetadataSync.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/backing-up-vms.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/working-with-gateways.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/configure-infrastructure-bgw.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/bgw-hypervisor-encryption-page.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_backup-gateway.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSBackupGatewayServiceRolePolicyForVirtualMachineMetadataSync.html>
- <https://docs.aws.amazon.com/aws-backup/latest/devguide/logging-using-cloudtrail.html>
- <https://aws.amazon.com/backup/pricing/>
