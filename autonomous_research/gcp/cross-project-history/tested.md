# Historical cross-project and cross-tenant vulnerabilities — checked

## 2026-09-28 — official bulletin reconciliation

- Reconciled the historical page against current first-party Google Cloud security bulletins and
  added nine fixed 2026 issue families: SecOps SOAR internal-header escalation; GKE Multi-Cloud
  target-project authorization; Integration Connectors service-account attachment; BigQuery Data
  Transfer JDBC tenant-runtime escape; BigQuery/Dataform/Colab repository takeover; Developer
  Connect and Cloud Build service-agent-only secret authorization; Cloud Logging dangling sink
  destinations; App Engine cross-tenant request-log disclosure; and Apigee sandbox metadata-token
  crossing.
- Corrected the stale introduction that implied only the bucket-squatting cases had CVEs. Recent
  managed-service bulletins include CVE-2026-15587, CVE-2026-4644, CVE-2026-12717,
  CVE-2026-14934, CVE-2026-8934 and CVE-2025-13292.
- Kept every entry explicitly historical and fixed. No exploitability inference was made beyond the
  corresponding Google bulletin, and no patched issue was promoted into a current privesc or
  post-exploitation technique.
- This was a documentation-only reconciliation. It created no cloud resource, enabled no API and
  changed no IAM or service configuration.
- Independent bulletin review corrected the new section's over-narrow "authorization failures"
  label because several entries are input-validation, sandboxing or privilege-management flaws.
  It also bounded the blanket "fixed" statement: Google remediated the managed Apigee service,
  while Apigee Hybrid customers still must verify the bulletin's Pub/Sub pipeline and minimum
  remediated-version requirements.
