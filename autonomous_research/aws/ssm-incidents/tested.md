# AWS Systems Manager Incident Manager (ssm-incidents) — tested

## Counter-IR (recon + timeline sabotage + response-plan hijack + replication-set nuke)

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1. Service IS callable
  (list-response-plans -> [] ; not onboarded = no replication set, so no records to read end-to-end).
- **Authz VERIFIED (least-priv):** role with ONLY GetIncidentRecord/DeleteIncidentRecord/
  UpdateTimelineEvent/ListTimelineEvents, assumed, GetIncidentRecord on a bogus incident ARN ->
  ResourceNotFoundException (NOT AccessDenied) => IAM gate passes. Role torn down (NoSuchEntity).
- **Technique (parallel to security-ir, from model):**
  - Recon: GetIncidentRecord/ListIncidentRecords/ListTimelineEvents/ListRelatedItems/
    ListIncidentFindings/GetResponsePlan -> defenders' impact assessment, timeline, suspected root
    cause (findings link the causing deployment), runbooks/tickets.
  - Sabotage: UpdateIncidentRecord (status RESOLVED + impact 5), Delete/Update/CreateTimelineEvent
    (erase/rewrite/inject), DeleteIncidentRecord, UpdateRelatedItems (unlink evidence).
  - Persistence/hijack: Create/UpdateResponsePlan `actions` = SSM Automation doc + roleArn that
    auto-runs on EVERY future incident (event-triggered RCE-as-role; needs PassRole + SSM-Automation
    trust); redirect `chatChannel` to attacker SNS; swap `engagements` so real on-call isn't paged.
  - Anti-forensics: UpdateDeletionProtection false + DeleteReplicationSet -> destroys ALL Incident
    Manager data in the account.
- **Disposition:** NEW page aws-services/aws-systems-manager-incident-manager-enum.md, SUMMARY-wired
  after Security Incident Response Enum. GetIncidentRecord labeled verified; rest from-model (honest
  NOTE block). Impact + Logs per section. No infra created (not onboarded) -> nothing to tear down
  beyond the probe role (done).
