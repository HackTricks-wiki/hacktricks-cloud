# Semantic Governance — checklist

## Completed

- [x] Map stable v1/v1beta1 policy and engine resources, CLI groups, fields, role contents, and
      enforcement-chain prerequisites.
- [x] Retain policy update/delete as a bounded defense-evasion technique with explicit non-privesc
      impact and Agent Gateway/tool authorization prerequisites.
- [x] Capture exact update/delete Admin Activity methods, permission checks, permission type, and
      default visibility without creating a policy.
- [x] Prove that engine `.update` does not authorize deprovision and record the hidden,
      non-catalog-grantable `.deprovision` permission instead of publishing a false technique.
- [x] Enumerate engine, policy, authorization-policy, authorization-extension, runtime-log, and
      metric evidence needed by defenders.
- [x] Delete every disposable identity, key, binding, role, and local credential/config artifact.

## Safe live-validation frontier

- [ ] In an already provisioned, explicitly disposable Agent Gateway fixture, create a synthetic
      agent/tool policy, prove a denied tool request, weaken and restore the constraint under an
      update-only caller, then prove the verdict change. Capture runtime evaluation logs/metrics and
      delete the policy. Do not provision an engine solely for this test while deprovision remains
      authorization-broken.
- [ ] Test blind update with only `.update` (no get/list), omitted versus stale `etag`, field-mask
      behavior, agent/tool rescoping, and v1/v1beta1 parity. Treat cross-project/cross-region target
      acceptance, deleted-target reuse, or stale-enforcement behavior as private-first findings.
- [ ] Compare policy mutation with Agent Gateway `AuthzPolicy`/`AuthzExtension` detachment and
      `failOpen` behavior. Keep these as separate Network Security/Service Extensions permission
      boundaries rather than attributing them to Semantic Governance policy permissions.
- [ ] Recheck the IAM catalog and predefined roles for
      `aiplatform.semanticGovernancePolicyEngine.deprovision`. If it becomes grantable, validate only
      a non-force call on an already disposable inactive fixture and preserve complete teardown.
- [ ] Reconcile feature-specific VPC-SC support wording with release notes and live perimeter
      behavior. Never infer that the broad `aiplatform.googleapis.com` service status guarantees
      every Semantic Governance data path.
