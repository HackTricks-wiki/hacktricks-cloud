# Embedded AWS technique format sweep — 2026-09-26

A heading scan of `aws-services/` identified offensive techniques embedded inside enumeration pages that escaped the earlier dedicated privesc/post-exploitation/persistence retrofit. Many apparent gaps are only reference headings to dedicated pages; the entries below contain actual steps and had missing required fields.

| Page / technique | Gap filled | Evidence or limit |
| --- | --- | --- |
| AppFabric ingestion destination | Stealth | Existing control-plane log table shows destination in `CreateIngestionDestination` |
| Connect Customer Profiles event stream | Stealth | Existing `CreateEventStream` log table identifies destination Kinesis ARN |
| Amazon Connect storage config | Explicit impact and stealth | Existing log table identifies `StorageConfig` destination |
| Deadline queue/fleet role vending | Stealth for both privesc variants | Existing live minimum-permission test and log tables retained |
| Private CA Connector for SCEP challenge read/create | Stealth; corrected `GetChallengePassword` Event History default | [AWS SCEP CloudTrail guide](https://docs.aws.amazon.com/privateca/latest/userguide/logging-using-cloudtrail-c4scep.html) lists both as management events; custom trails may omit read management events |
| Device Farm project variables, live session endpoint, artifacts | Impact/stealth/log tables as applicable | [AWS Device Farm CloudTrail guide](https://docs.aws.amazon.com/devicefarm/latest/developerguide/logging-using-cloudtrail.html) covers API calls. Endpoint use remains conditional on endpoint authorization; artifact URL retrieval was previously confirmed by HTTP 200. |

No new cloud infrastructure was launched for this format sweep. Continue scanning actual embedded techniques while excluding reference-only headings.
