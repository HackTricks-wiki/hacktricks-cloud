# Cloud IDS and network inspection — open validation leads

- [ ] Capture an authorized Cloud IDS `UpdateEndpoint` audit sequence with a harmless test signature ID and confirm the start/completion entries and request-field visibility. Restore the original exception list immediately.
- [ ] Capture `UpdateDnsThreatDetector` telemetry. The current REST schema exposes the method but the current Cloud NGFW audit catalog omits the entire DNS Threat Detector surface; do not claim Admin Activity until validated. Restore the original excluded-network list immediately.
- [ ] With a disposable producer and consumer, validate the exact cross-project and cross-organization `interceptDeploymentGroups.use` / `mirroringDeploymentGroups.use` grant locations and whether the endpoint creation audit entry identifies the producer resource. Delete every producer, endpoint, association, profile, group, rule, load balancer, and appliance after the test.
- [ ] Revisit endpoint-level Cloud IDS IAM only if the public API exposes `getIamPolicy`/`setIamPolicy` or a supported client can invoke them. Verify supported binding roles and inheritance before classifying it as persistence.
