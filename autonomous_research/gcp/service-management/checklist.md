# Service Management — research checklist

- [ ] In a pre-existing Cloud Endpoints deployment, compare fixed and managed ESP rollout modes and
      record the propagation time and data-plane logs for a harmless config revision.
- [ ] If a disposable pre-existing API Gateway becomes available, verify whether direct deletion of
      its backing Service Management managed service disrupts the gateway and how recovery behaves.
      Do not assert additional API Gateway rollout effects without a live result.
- [ ] Test consumer-resource `setIamPolicy` separately from service-resource IAM and determine
      whether any role grant produces a distinct cross-project escalation rather than generic
      service consumption.
