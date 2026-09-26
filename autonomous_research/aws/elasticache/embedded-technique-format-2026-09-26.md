# ElastiCache embedded technique format — 2026-09-26

The [ElastiCache CloudTrail guide](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/logging-using-cloudtrail.html) confirms management API logging. Reviewed the three post-exploitation techniques embedded in `aws-elasticache.md` against the [ModifyUser API](https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_ModifyUser.html) and existing export references. Added missing impact/log/stealth fields for password replacement and stealth ratings for the two snapshot exports. The export calls already had impact and expandable log tables.

| Technique | Result | Book action |
| --- | --- | --- |
| `ModifyUser` password replacement | Existing conditional data-plane foothold; management write is visible | Added impact, stealth, log table |
| `CopySnapshot` S3 export | Existing exfil technique | Added stealth rating |
| `ExportServerlessCacheSnapshot` S3 export | Existing exfil technique | Added stealth rating |

No cache resources were created in this audit.
