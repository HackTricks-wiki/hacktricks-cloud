# MemoryDB technique format audit — 2026-09-26

Reviewed the two post-exploitation techniques embedded in `aws-memorydb-enum.md` against the [MemoryDB CloudTrail guide](https://docs.aws.amazon.com/memorydb/latest/devguide/logging-using-cloudtrail.html) and the [UpdateUser](https://docs.aws.amazon.com/memorydb/latest/APIReference/API_UpdateUser.html) / [CopySnapshot](https://docs.aws.amazon.com/memorydb/latest/APIReference/API_CopySnapshot.html) API references. `UpdateUser` changes passwords and/or the access string; `CopySnapshot` accepts a `TargetBucket` for export. MemoryDB API calls appear in CloudTrail management events; Redis/Valkey commands are separate engine traffic.

| Candidate | Result | Book action |
| --- | --- | --- |
| `UpdateUser` password replacement | Existing technique; access remains bounded by its ACL, and the control-plane write is visible | Added explicit impact, stealth, and expandable log table |
| `CopySnapshot` S3 export | Existing technique; destination bucket is an obvious management-event field | Added explicit stealth rating |

No new MemoryDB infrastructure was launched for this format pass. The prior book's minimum-permission and service-linked-role observations were not retested here.
