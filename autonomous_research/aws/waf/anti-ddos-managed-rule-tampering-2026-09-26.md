# AWS WAF Anti-DDoS managed rule group tampering — assessed 2026-09-26

## Decision

Add a focused subsection to the public WAF post-exploitation page. Generic `UpdateWebACL` and Web ACL
disassociation were already covered, but `AWSManagedRulesAntiDDoSRuleSet` adds distinct configuration
levers that were absent: disabling its client-side challenge subsystem, lowering two independent
sensitivity settings, broadening challenge-exempt URI expressions, and limiting the traffic used to
build its DDoS baseline.

This remains AWS WAF tampering. Starting 2026-03-26, the managed group is the default HTTP-flood
solution for new Shield Advanced customers and supersedes legacy Layer 7 Auto Mitigation, but none of
these changes calls a Shield API or disables Shield Standard/infrastructure-layer mitigation.

## Current rule contract

The current official and live read-only contracts agree:

- Vendor/name: `AWS` / `AWSManagedRulesAntiDDoSRuleSet`; capacity 50 WCUs.
- `ChallengeAllDuringEvent`: default Challenge.
- `ChallengeDDoSRequests`: default Challenge.
- `DDoSRequests`: default Block.
- `SensitivityToBlock`: `LOW|MEDIUM|HIGH`, default `LOW`.
- `ClientSideActionConfig.Challenge.UsageOfAction`: required `ENABLED|DISABLED`.
- Challenge `Sensitivity`: `LOW|MEDIUM|HIGH`, default `HIGH`.
- When challenge usage is disabled, neither Challenge rule runs and the group emits no
  `challengeable-request` label. `DDoSRequests` remains active.
- URI regex exemptions prevent both Challenge rules from evaluating matching paths, regardless of
  per-rule action override. The block rule remains available.

## Useful tampering paths

All in-place paths use `wafv2:UpdateWebACL` and the caller must submit the complete mutable Web ACL
configuration with a valid optimistic-lock token:

1. Remove the managed-rule-group reference. This eliminates its baseline evaluation, event/request
   labels, challenges, and blocking.
2. Set the containing rule's `OverrideAction` to Count. This is the cleanest one-field global action
   downgrade: the group still evaluates and labels traffic, but its Block/Challenge results become
   non-terminating Count results.
3. Use `RuleActionOverrides` or deprecated `ExcludedRules` for
   `ChallengeAllDuringEvent`, `ChallengeDDoSRequests`, and/or `DDoSRequests`. Excluded rules mean
   Count. AWS specifically permits only Allow or Count overrides for the two Challenge rules and
   discourages Allow.
4. Set challenge `UsageOfAction=DISABLED`. This disables both Challenge rules without disabling the
   block rule, and suppresses `challengeable-request` labels.
5. Lower either configured sensitivity to `LOW`. This narrows action to the high-suspicion label;
   it is only a downgrade where the victim configured Medium or High.
6. Add an exemption regex that matches sensitive or all paths. Challenge protection disappears for
   those paths, while `DDoSRequests` may still block them.
7. Add a restrictive `ScopeDownStatement`, place the group after terminating rules, or add an earlier
   Allow rule. AWS explicitly warns that scope-down limits the observed traffic and can degrade the
   baseline and event detection.
8. Replace or remove the resource's Web ACL association. This removes all controls in that ACL and is
   broader/louder than altering only Anti-DDoS.

`OnSourceDDoSProtectionConfig` is an adjacent Web ACL setting, not part of this managed rule group.
Changing an ALB ACL from `ALWAYS_ON` to the default `ACTIVE_UNDER_DDOS` reduces continuous
low-reputation-source handling but does not disable its under-attack protection; do not conflate that
with removing Anti-DDoS AMR.

## Minimum IAM

For all in-place managed-group changes:

```json
{
  "Effect": "Allow",
  "Action": "wafv2:UpdateWebACL",
  "Resource": "arn:aws:wafv2:REGION:ACCOUNT:regional/webacl/NAME/ID"
}
```

Use `arn:aws:wafv2:us-east-1:ACCOUNT:global/webacl/NAME/ID` for CloudFront scope. The machine-readable
Service Authorization Reference marks `webacl` as the required resource and also lists optional
referenced `ipset`, `managedruleset`, `regexpatternset`, and `rulegroup` resources. It lists no
dependent action for `UpdateWebACL`. Authorization on those customer-resource ARNs is additionally
needed when the submitted rule tree triggers their checks; the AWS-managed Anti-DDoS reference does
not require an attacker-owned rule-group ARN. `GetWebACL` on the exact ARN is reconnaissance only if
the full configuration and lock token are not already known.

Firewall Manager policy-managed first/last groups are a different boundary: member accounts can
manage their own middle rules but cannot remove the policy-controlled group through `UpdateWebACL`.
Tampering with that deployment requires permission such as `fms:PutPolicy` in the Firewall Manager
administrator account and should be treated as Firewall Manager policy tampering.

For association replacement/removal:

- ALB replacement: `wafv2:AssociateWebACL` on the exact weaker ACL plus
  `elasticloadbalancing:CreateWebACLAssociation` on the exact ALB.
- Current ALB disassociation: `wafv2:DisassociateWebACL` on `*` plus
  `elasticloadbalancing:DeleteWebACLAssociation` on the exact ALB. AWS also documents the legacy
  `elasticloadbalancing:SetWebACL`-only permission setting.
- API Gateway disassociation: `apigateway:SetWebACL` on the exact stage; AWS says the WAF
  `DisassociateWebACL` permission is not required for this exception.
- AppSync, Cognito, App Runner, Amplify, Verified Access, and AgentCore require the WAF action plus
  their documented target-service action. This dependency is not represented as a second caller API
  event merely because IAM checks it.
- CloudFront: the WAF association APIs do not apply. `cloudfront:UpdateDistribution` on the exact
  distribution submits an empty or weaker Web ACL ID; `GetDistributionConfig` is optional discovery
  when the current configuration/ETag are already known.

## Logging and detection

- `GetWebACL` is a CloudTrail management read if used.
- `UpdateWebACL` is a default-logged management write. Every in-place mutation above appears under
  that single event name; there are no separate `ExcludeRule`, sensitivity, or challenge-mode events.
- AWS documents cross-account `UpdateWebACL` success and access-denied events in both caller and
  resource-owner accounts where resource-policy access is involved.
- WAF traffic logs show Count overrides under `ruleGroupList`, with `action` set to Count and
  `overriddenAction` showing the configured action that was replaced.
- Missing `awswaf:managed:aws:anti-ddos:*` labels and CloudWatch label/rule metrics are a secondary
  signal for removal, scope narrowing, challenge disablement, or overly broad URI exemptions.
- Association changes log `AssociateWebACL`/`DisassociateWebACL`; CloudFront logs
  `UpdateDistribution` instead. Configuration/baseline comparison is required to distinguish a
  legitimate tuning update from malicious weakening.

## Read-only lab result and residue

Profile `ht-admin`, account `228478051196`:

- `ListWebACLs` returned empty for Regional scope in `us-east-1` and `eu-west-1`, and for CloudFront
  scope in `us-east-1`.
- `DescribeManagedRuleGroup` succeeded in all three scope/Region checks and returned the three rules,
  actions, capacity, and Anti-DDoS labels above.
- `shield:DescribeSubscription` returned `ResourceNotFoundException`; the account has no Shield
  Advanced subscription.
- No Web ACL was created because adding this managed group is explicitly billable and no pre-existing
  fixture existed. No association, rule, configuration, subscription, or other resource was changed.
  Cleanup was unnecessary and residue is zero.

## Primary sources

- <https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-anti-ddos.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/waf-anti-ddos-rg-using.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/waf-anti-ddos-deploying.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/ddos-automatic-app-layer-response.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_AWSManagedRulesAntiDDoSRuleSet.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_ClientSideAction.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_ManagedRuleGroupStatement.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_UpdateWebACL.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_DisassociateWebACL.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/security_iam_service-with-iam.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/understanding-waf-entries.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/waf-policies-rule-groups.html>
- <https://servicereference.us-east-1.amazonaws.com/v1/wafv2/wafv2.json>
