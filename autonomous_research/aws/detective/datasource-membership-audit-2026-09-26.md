# Detective package and membership audit — 2026-09-26

## Findings

The public page had two important correctness gaps:

1. Its `UpdateDatasourcePackages` command supplied the option with no value and could not run.
2. It said member removal deleted existing graph data. AWS explicitly says existing data remains and
   only future ingestion stops.

The remaining member-removal and graph-destruction primitives are useful defense evasion, but lacked
minimum permissions, prerequisites, and stealth classifications.

## Live package-state test

Authorized account `228478051196`, `us-east-1`, profile `ht-admin`:

- Preflight found no Detective graph and no test-role name collision.
- Created one disposable Detective behavior graph. New-graph defaults showed
  `DETECTIVE_CORE`, `EKS_AUDIT`, and `ASFF_SECURITYHUB_FINDING` all `STARTED`.
- Created a disposable role whose only service permission was
  `detective:UpdateDatasourcePackages` on that exact graph.
- The restricted role submitted `DatasourcePackages=[DETECTIVE_CORE]` without any Detective read
  permission.
- The call succeeded. Administrator verification showed both optional packages changed to `STOPPED`
  at the same timestamp while `DETECTIVE_CORE` remained `STARTED`.

This establishes that the request list behaves as the desired active package set, despite the current
API description saying that the operation "starts" a package. Omitting an optional package stops it;
the mandatory core package must remain in the list. `ListDatasourcePackages` is useful recon but is not
an authorization dependency when the graph ARN and desired set are known.

## Logging boundary

Event History later captured the successful restricted-role call as a default CloudTrail management
write under `detective.amazonaws.com`, with `readOnly=false`, the graph ARN, and
`DatasourcePackages=[DETECTIVE_CORE]` in `requestParameters`; `responseElements` was null. Package state
and ingestion loss must therefore be detected by correlating the request list with expected state or by
separately reconciling `ListDatasourcePackages`.

The public page now avoids claiming that CloudTrail contains a returned full state.

## Membership and deletion corrections

- `DeleteMembers` can be called only by the graph administrator. It stops ingestion for the selected
  members; existing graph data remains.
- `DisassociateMembership` is available only to an invited enabled member, not an Organizations member.
  Existing data also remains.
- Removed organization accounts can be enabled again by the Detective administrator, so this is not
  durable persistence against an auto-reconciling organization.
- `DeleteGraph` disables and queues the graph for deletion. It is the destructive history-erasure path,
  not member removal.
- `DisableOrganizationAdminAccount` is Regional, requires the Organizations management account, and
  deletes the organization graph. It does not itself deregister the Organizations delegated admin.

## Cleanup verification

The disposable graph was deleted and a subsequent `ListGraphs` returned an empty list. The inline IAM
policy and disposable role were deleted, and `GetRole` confirmed the role absent. No other AWS resource
was created for this test. The graph was live for less than two minutes and the test generated no
application workload.

## Official sources

- <https://docs.aws.amazon.com/detective/latest/APIReference/API_UpdateDatasourcePackages.html>
- <https://docs.aws.amazon.com/detective/latest/APIReference/API_ListDatasourcePackages.html>
- <https://docs.aws.amazon.com/detective/latest/userguide/source-data-types-EKS.html>
- <https://docs.aws.amazon.com/detective/latest/userguide/source-data-types-asff.html>
- <https://docs.aws.amazon.com/detective/latest/APIReference/API_DeleteMembers.html>
- <https://docs.aws.amazon.com/detective/latest/APIReference/API_DisassociateMembership.html>
- <https://docs.aws.amazon.com/detective/latest/userguide/accounts-orgs-members-disassociate.html>
- <https://docs.aws.amazon.com/detective/latest/userguide/member-remove-self-from-graph.html>
- <https://docs.aws.amazon.com/detective/latest/APIReference/API_DeleteGraph.html>
- <https://docs.aws.amazon.com/detective/latest/APIReference/API_DisableOrganizationAdminAccount.html>
