# AWS Incident Manager (ssm-incidents) — open ideas

- [x] Counter-IR recon + timeline sabotage + response-plan hijack + replication-set nuke — DONE
  (page created; GetIncidentRecord authz-verified, rest from-model). See tested.md.
- [ ] End-to-end validation of response-plan SSM-Automation-on-incident-start execution — requires
  onboarding a replication set (account-wide config) + a fired incident. Heavier; deferred unless a
  dedicated test account is used. The PassRole->automation angle itself is covered by SSM privesc.
- [ ] PutResourcePolicy on a response plan (cross-account share) — add to the cross-account
  resource-policy matrix? Check whether ssm-incidents response-plan is already a matrix resource type.
