# Service Directory research checklist

## Covered

- [x] Namespace/service/endpoint enumeration and `ResolveService` output.
- [x] Endpoint create/update poisoning, client-selection bounds, and immutable-network helper permission.
- [x] Service Directory-backed private DNS prerequisites and same-project constraint.
- [x] Namespace/service IAM inheritance and service-level persistence.
- [x] Endpoint-IAM role-catalog versus public-API mismatch.
- [x] Exact v1 audit methods, classes, LRO status, and default visibility.
- [x] Cloud DNS query-log and downstream network/application signals.
- [x] Destructive, self-grant, annotation-only, and unauthenticated no-garbage classification.
- [x] Current Google Cloud CLI syntax.

## Safe future validation

- [ ] In a disposable namespace/service, enable Service Directory Data Access logging and confirm exact `CreateEndpoint`, `UpdateEndpoint`, `ResolveService`, and list records; delete all resources and restore the audit configuration.
- [ ] Compare client behavior when a rogue endpoint is added versus an existing endpoint is repointed, including `endpoint-filter` and `max-endpoints` use.
- [ ] With a disposable same-project Service Directory DNS zone, measure A/AAAA/SRV answer selection and caching, then delete the zone and registry resources.
- [ ] Validate Shared VPC ownership/location of DNS query logs and the effect of client-side caching.
- [ ] Validate `gcloud ... add-iam-policy-binding` helper reads and exact Admin Activity output; remove the resource binding immediately.
- [ ] Recheck whether a future public API adds endpoint-level IAM methods before documenting the role-catalog permission names as exploitable.

## Guardrails

- Use only disposable namespaces, services, endpoints, zones, and IAM members.
- Capture original endpoint fields and IAM policies before mutation; preserve versions, conditions, and `etag` values.
- Remove every endpoint, zone, binding, and logging override in the same test window.
