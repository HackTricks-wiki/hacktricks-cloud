# Resource Groups `StartTagSyncTask` role — reasoned exclusion 2026-09-26

## Candidate

`StartTagSyncTask` accepts a group, selector tag key/value, and IAM role ARN. The service continually
finds resources matching the selector and uses the role to add or remove their AppRegistry application
membership, initially suggesting a service-role pivot or tag-based authorization path.

## Result

This does not clear the book's usefulness bar as a distinct attack technique:

- The caller needs `resource-groups:StartTagSyncTask`, dependent
  `resource-groups:CreateGroup`, and `iam:PassRole` for the supplied role.
- The role is assumed by `resource-groups.amazonaws.com` and needs grouping plus each target service's
  tag/untag actions.
- The input tag selects resources; it is not the tag written to them. The task only applies or removes
  the AWS-defined `awsApplication` tag that represents membership in the selected application group.
- The task cannot choose arbitrary resource tags, invoke code, return role credentials, or perform
  operations other than grouping and tag/untag allowed by the passed role.

It can still create cost-allocation/inventory noise or disrupt workflows that incorrectly trust
AppRegistry membership, but those are environment-specific misconfigurations rather than a general
AWS privilege-escalation primitive.

## Read-only lab evidence

Account `228478051196`, `us-east-1` has zero Resource Groups and zero active tag-sync tasks. Event
History contains one earlier negative probe: the service rejected `StartTagSyncTask` at the
`iam:PassRole` gate before group lookup when the test identity carried an explicit PassRole deny.
No resource was created in this review and there is nothing to clean up.

## Revisit condition

Revisit only for a concrete application whose authorization or automation treats `awsApplication`
membership as a privilege boundary. In that case, test the consuming policy or automation directly;
do not describe tag sync itself as generic role execution.

## Sources

- <https://docs.aws.amazon.com/servicecatalog/latest/arguide/app-tag-sync.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_resource-groups.html>
- <https://docs.aws.amazon.com/ARG/latest/APIReference/API_StartTagSyncTask.html>
