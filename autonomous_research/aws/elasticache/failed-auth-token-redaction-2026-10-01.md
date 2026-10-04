# ElastiCache failed AUTH-token redaction audit — 2026-10-01

## Result

A restricted IAM user was allowed `elasticache:ModifyReplicationGroup` only on one exact synthetic
replication-group ARN and submitted `ROTATE`, `ApplyImmediately=true`, and a unique generated token.
No replication group or ElastiCache service-linked role existed.

The request passed IAM and stopped at `ServiceLinkedRoleNotFoundFault` before target resolution. The
CloudTrail management write did not contain the unique token marker. In fact, it recorded null
request parameters, response elements, and resources.

## CloudTrail evidence

- event time: `2026-10-01T06:00:29Z`
- event ID: `3473b4e7-bcce-425b-b50c-18b90ea67792`
- request ID: `29456781-1407-4a80-8461-3023d41da51a`
- `readOnly:false`, `managementEvent:true`
- `errorCode:ServiceLinkedRoleNotFoundFault`
- request/response/resources: null
- unique marker present anywhere in event: false

The earlier successful live rotation separately confirmed explicit
`authToken:"HIDDEN_DUE_TO_SECURITY_REASONS"`, so both successful and this failed branch avoided
plaintext disclosure. The failed branch's total request omission is a detection caveat: it does not
identify the attempted group, strategy, or apply timing.

## Cleanup and disposition

The restricted access key, inline policy, and IAM user were deleted; final matching IAM inventory
was empty. No SLR, replication group, cluster, network resource, snapshot, object, or other
ElastiCache resource was created.

Secret-redaction hypothesis closed safe. The sparse failed-event shape alone has no successful
security impact and was not opened as a private vulnerability report. No cost or cleanup debt.
