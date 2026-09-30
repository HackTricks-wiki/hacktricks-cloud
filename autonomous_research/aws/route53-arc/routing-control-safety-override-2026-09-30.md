# Route 53 ARC routing-control and safety-rule audit — 2026-09-30

## Result

Public technique #105 documents `route53-recovery-cluster:UpdateRoutingControlState` and `UpdateRoutingControlStates` as traffic-control primitives. Both APIs accept `SafetyRulesToOverride`; the same write action authorizes ordinary changes and break-glass override requests. The current IAM control is the Boolean `route53-recovery-cluster:AllowSafetyRulesOverrides` condition key. AWS's current policy example explicitly says `false` permits data-plane operation without overrides and `true` permits overrides.

The technique is high value because routing controls drive Route 53 health checks for whole cells. Abuse can drain an active cell, enable a less-trusted cell, or override an assertion that normally keeps at least one cell active. It is not an IAM privilege-escalation primitive.

## Live account work

Read-only preflight found zero clusters and zero control panels. A minimal unconnected fixture was then attempted in `us-west-2` under the documented $2.50/cluster-hour price. No Route 53 health check, hosted zone, DNS record, application endpoint, VPC, compute resource, or production routing target was created.

Live-confirmed behavior:

- Cluster, default panel, two routing controls, and an `ATLEAST 1` assertion-rule lifecycle all worked.
- `UpdateRoutingControlStates` successfully initialized both isolated controls to `On` through the cluster's `us-west-2` data-plane endpoint.
- Resource creation and especially safety-rule propagation were multi-minute asynchronous operations.
- The configuration plane is `us-west-2`; a cluster supplies five regional data-plane endpoints.

Not live-confirmed:

- The restricted operator never ran. In both full fixture attempts the safety rule remained `PENDING` longer than the five-minute harness bound, so execution stopped before IAM policy creation and before any safety-rule override request.
- Ordinary rule rejection, unconstrained-policy override, and the `AllowSafetyRulesOverrides=false` denial remain current official API/IAM behavior rather than an observed result in this account.
- `cloudtrail:LookupEvents` is SCP-denied in `us-west-2`; the allowed `us-east-1` history had no ARC events. AWS documentation states that all ARC actions are CloudTrail management events and that Event History must be viewed in `us-west-2`, so precise live request serialization was not claimed independently.

## Harness failures and cleanup evidence

All failures were local lifecycle/field-handling issues, not AWS security defects:

1. The first cluster run inherited an invalid local `AWS_DEFAULT_OUTPUT=asd`; the trap deleted the childless cluster and final exact counts were zero.
2. The next run queried `Rule.*.Arn` even though the create response field is `SafetyRuleArn`. It waited on `None`, created no operator role, and entered cleanup. After the resources reached `DEPLOYED`, the exact rule, two controls, and cluster were deleted in dependency order. Final exact counts were zero.
3. The corrected run obtained the exact rule ARN, but the rule stayed `PENDING` beyond the bounded wait. It created no operator role and made no override call. After deployment converged, the exact rule, both controls, and cluster were deleted in dependency order.

Final independent inventory:

- `route53-recovery-control-config list-clusters`: zero names starting `ht-arc-`
- IAM roles: zero names starting `ht-arc-operator-`
- Each exact safety-rule and routing-control ARN returned absent before its parent cluster was deleted
- No Route 53 health check or DNS resource was ever created

No unexpected AWS behavior was found and no private vulnerability report was created.

## Defensive boundary

Do not grant state-update actions without the condition if ordinary operators must not bypass safety rules. Use:

```json
"Condition": {
  "Bool": {
    "route53-recovery-cluster:AllowSafetyRulesOverrides": "false"
  }
}
```

The service error for a blocked state update discloses the blocking safety-rule ARN, so hiding configuration-list permissions is not a substitute for this condition.

## Sources

- https://docs.aws.amazon.com/r53recovery/latest/dg/routing-control.about.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/routing-control.override-safety-rule.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/security_iam_id-based-policy-examples-routing.html
- https://docs.aws.amazon.com/routing-control/latest/APIReference/API_UpdateRoutingControlState.html
- https://docs.aws.amazon.com/routing-control/latest/APIReference/API_UpdateRoutingControlStates.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_route53-recovery-cluster.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/cloudtrail-routing.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/routing-control.failover-different-accounts.html
- https://aws.amazon.com/application-recovery-controller/pricing/
