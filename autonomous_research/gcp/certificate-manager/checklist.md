# Certificate Manager — research checklist

- [ ] In a pre-existing disposable load balancer, measure propagation and data-plane telemetry for
      a harmless certificate-map entry swap; restore the original entry immediately.
- [ ] Determine whether Public CA exposes any supported ACME-account invalidation mechanism short
      of project deletion. Current public API/gcloud surfaces only create EAB keys.
- [ ] Audit Certificate Manager v2 SPIFFE trust stores and managed workload certificate lifecycle
      for membership or trust-domain injection that adds capability beyond the existing trust-config
      update primitive.
- [ ] Re-check cross-project certificate-map and trust-config `use` permissions for a genuine
      confused-deputy path; do not publish simple same-authority attachment chains.
