# EMR WAL CloudTrail data-event audit — 2026-09-26

The [AWS EMR CloudTrail guide](https://docs.aws.amazon.com/emr/latest/ManagementGuide/logging-using-cloudtrail.html) lists opt-in data events for `AWS::EMRWAL::Workspace`: `GetCurrentWALTime`, `ListTagsForResource`, `ListWALs`, `ListWorkspaces`, `TrimWAL`, and `CompleteWALFlush`. EMR control-plane APIs used in the book's existing privilege escalation techniques remain management events. The prior blanket claim that EMR has no data events was false but did not change the event category of those specific attack calls.

Corrected four repeated statements in EMR privilege escalation and added service-enumeration logging guidance. No live AWS calls or resources were used in this audit.

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| WAL workspace API calls under minimum permissions | Expected | Logging documented; offensive impact not assessed | Review EMR WAL IAM actions for meaningful data access or tampering |
| WAL selector missing expected `TrimWAL` event | Potential unexpected | No evidence | Test only with isolated WAL workspace and trail; clean up both |
