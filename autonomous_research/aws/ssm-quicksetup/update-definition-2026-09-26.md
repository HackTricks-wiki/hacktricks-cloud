# SSM Quick Setup `UpdateConfigurationDefinition` — reasoned exclusion 2026-09-26

## Candidate

Quick Setup uses CloudFormation and StackSets to deploy operational configurations across accounts
and Regions. `UpdateConfigurationDefinition` accepts new parameters plus a local deployment
administration-role ARN and execution-role name, so it initially resembled a stored-authority or
`iam:PassRole` privilege-escalation path.

## Boundary review

AWS's authorization reference makes `iam:PassRole` a dependent permission for
`ssm-quicksetup:UpdateConfigurationDefinition`, scoped to roles passed to CloudFormation or Quick
Setup. The API is also limited to AWS-defined configuration types rather than accepting an arbitrary
CloudFormation template. Current types cover Config recording/conformance packs, host management,
patch policies, Distributor, Resource Explorer, scheduling, OpsCenter, JIT node access, and related
operational setup.

The highest-signal parameters still do not form a clean standalone privesc primitive:

- Distributor accepts only the documented AWS-owned packages `AWSEFSTools`, `AWSCWAgent`, and
  `AWSEC2LaunchAgent`, not an attacker-controlled package.
- Patch Policy selects patch baselines and scan/install schedules, not an arbitrary command or
  document.
- Change Manager accepts `AdminPermissions` or a caller-supplied custom job-function policy, but the
  configuration creates a Change Manager invocation role. Updating the definition does not itself
  grant the updater permission to assume/pass that role or start an approved change workflow.
  Change Manager is also closed to new customers as of November 7, 2025.
- The remaining types deploy fixed operational resources. Their disruptive or governance effects are
  exactly what the named Quick Setup permission authorizes and do not add arbitrary execution.

An existing configuration might still be dangerous when combined with separate permission to use a
created Change Manager role or when a target's custom policies/trust are already weak. That is a
configuration-specific chain, not a general Quick Setup-only escalation technique.

## Read-only lab preflight

Under `ChackBotAdministratorRole` in account `228478051196`, `us-east-1`:

- `ListConfigurationManagers` returned an empty list.
- `GetServiceSettings` returned an empty settings object.
- `ListQuickSetupTypes` returned the current fixed type catalog.
- No `AWS-QuickSetup-*` local administration/execution role exists. The only matching CloudFormation
  role is the existing Organizations StackSets member service-linked role.
- Event History contains only earlier invalid/nonexistent-resource Quick Setup probes and the current
  read operations; there is no successful configuration creation.

Creating a fixture would onboard Quick Setup and produce CloudFormation/StackSet, IAM role, service
integration, and potentially organization-wide state. That residue is not justified for a candidate
whose arbitrary-template hypothesis is contradicted by the public contract. No mutation was made and
there is nothing to clean up.

## Revisit condition

Revisit only in an already-onboarded disposable account with an existing configuration manager. The
useful test is whether a principal allowed only `UpdateConfigurationDefinition` on one manager—but
denied `iam:PassRole` and use of the resulting service roles—can change parameters and cause the
stored roles to deploy a materially more privileged configuration. Also verify whether service-side
validation rejects undocumented parameter keys and non-catalog type versions.

## Sources

- <https://docs.aws.amazon.com/quick-setup/latest/APIReference/API_UpdateConfigurationDefinition.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_ssm-quicksetup.html>
- <https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ssmquicksetup-configurationmanager-configurationdefinition.html>
- <https://docs.aws.amazon.com/systems-manager/latest/userguide/quick-setup-getting-started.html>
- <https://docs.aws.amazon.com/systems-manager/latest/userguide/change-manager-organization-setup.html>
