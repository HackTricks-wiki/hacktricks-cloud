# DocumentDB Elastic password-reset format — 2026-09-26

The embedded `docdb-elastic:UpdateCluster` administrator-password reset lacked explicit impact, stealth, and a log table. The [UpdateCluster API](https://docs.aws.amazon.com/documentdb/latest/developerguide/API_elastic_UpdateCluster.html) supports changing the administrator password. [DocumentDB CloudTrail guidance](https://docs.aws.amazon.com/documentdb/latest/developerguide/logging-with-cloudtrail.html) covers management API logging. A read-only lookup of a prior authorized test event in the training account confirmed `eventName=UpdateCluster`, `eventSource=docdb-elastic.amazonaws.com`, and `eventCategory=Management`. Its request parameters identified the cluster ARN; no password value was printed in this audit.

Added concise impact, low stealth, and an expandable log table to the enumeration page. No DocumentDB infrastructure was created and no password was changed in this audit.
