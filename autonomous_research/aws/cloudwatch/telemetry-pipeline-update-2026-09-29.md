# CloudWatch Observability Admin telemetry pipelines — 2026-09-29 audit

## Scope and hypotheses

This audit examined whether an existing telemetry pipeline can be repurposed to erase or falsify
telemetry before it is stored, the exact cross-service authorization required for a metrics-pipeline
update, and whether the mutation is visible in default CloudTrail management history.

Testing used account `228478051196` in `us-east-1`. Pipeline identifiers and temporary principal
identifiers are omitted from this ledger.

## Preflight

- `ListTelemetryPipelines` returned no pipelines in `us-east-1` or `eu-west-1`.
- Official API documentation says the name, ARN, and source type are immutable, but processors can
  be added, removed, or modified. Several source-specific role, queue, secret-reference, endpoint,
  and sink fields are also updatable.
- The CloudWatch guide documents that `drop_events` removes matching log entries and that vended
  CloudWatch Logs-source processors mutate events in the original log group unless
  `include_original` preserves the raw message.

## No-state processor tests

`TestTelemetryPipeline` accepts a processor-only configuration and synthetic records; it creates no
pipeline or other resource.

| Test | Input | Result |
| --- | --- | --- |
| `drop_events` with `when: "true"` | JSON event named `security-canary`, severity `CRITICAL` | HTTP success with an empty result object: no output record survived |
| `delete_entries` plus overwriting `add_entries` | `login_failure`, severity `CRITICAL`, with `user` and `source_ip` | Output retained only `event` and `severity`, changed to `INFO` |

`ValidateTelemetryPipelineConfiguration` requires a complete source/processor/sink body, unlike the
test API. Both the benign and destructive full metrics configurations validated successfully with
an empty error list.

## Live create/update result

A disposable CloudWatch Metrics pipeline selected an impossible synthetic service-name/metric-name
pair, so it processed no real metrics. It became `ACTIVE`. `UpdateTelemetryPipeline` then replaced
its benign add-attribute processor with destructive delete/overwrite processors while preserving
the immutable source and sink. `GetTelemetryPipeline` returned `ACTIVE` with the replacement body.

The processor test, API update, and documented log-pipeline behavior together establish the
expected attack: a principal with update control can erase or rewrite matching telemetry before it
reaches the sink. This is an intended feature with dangerous authorization consequences, not a
service defect.

## Least-privilege authorization matrix

A second zero-match metrics pipeline and a disposable IAM user isolated the dependency:

| Caller policy | Result |
| --- | --- |
| `observabilityadmin:UpdateTelemetryPipeline` on the exact pipeline ARN only | Denied; the subsidiary `monitoring.amazonaws.com` `PutPipelineRule` event showed `AccessDenied` |
| Same grant plus `cloudwatch:PutPipelineRule` on `arn:aws:cloudwatch:us-east-1:228478051196:dataset/default` | Update succeeded |

No `iam:PassRole` was needed for the CloudWatch Metrics source. AWS documents different contextual
dependencies for other sources: `logs:PutPipelineRule` for CloudWatch Logs and `iam:PassRole` for
configurations that reference a source role.

Two fixture-only false starts were resolved and cleaned:

- An initial YAML string contained literal `\\n` sequences and correctly failed validation; no
  resource was created.
- The administrator session could create roles but was not allowed to call `sts:AssumeRole`, so that
  identity fixture stopped before mutation. A first IAM-user call hit normal new-key propagation
  (`UnrecognizedClientException`); the final matrix waited for `GetCallerIdentity` before testing
  authorization and produced the conclusive denial above.

## Third-party credential-relay canary

A separate disposable Palo Alto Networks source tested whether the API-pull pipeline would send a
canary Secrets Manager username/password to an operator-controlled HTTPS endpoint. The complete
configuration used the documented `paloaltonetworks_nextgenerationfirewall` source, OCSF mapping,
Secrets Manager extension with a dedicated source role, and a CloudWatch Logs sink. Validation
returned zero errors and the pipeline reached `ACTIVE`.

The capture endpoint recorded only whether an Authorization header existed and its SHA-256 digest;
it was deliberately incapable of logging the canary value. No request reached the endpoint. The
pipeline existed from 10:25:52 to 10:27:39 local time and was active for roughly 75 seconds before
the supervising shell was interrupted, so this is an **inconclusive negative**, not evidence that
credential relay is impossible. A repeat needs a detached cleanup guard and an observation window
longer than the source's polling/retry interval. Do not publish this hypothesis unless that repeat
observes the expected canary hash.

The API accepted an arbitrary HTTPS hostname syntactically, which only establishes configuration
acceptance. It does not establish that credentials are transmitted or that an `UpdateTelemetryPipeline`
caller can repoint an existing source without the relevant `iam:PassRole` dependency.

## Telemetry

- `CreateTelemetryPipeline`, `UpdateTelemetryPipeline`, `DeleteTelemetryPipeline`,
  `GetTelemetryPipeline`, `ListTelemetryPipelines`, `ValidateTelemetryPipelineConfiguration`, and
  `TestTelemetryPipeline` appeared as default management events under
  `observabilityadmin.amazonaws.com`.
- The update event recorded the exact pipeline ARN and complete replacement configuration body.
- Metrics create/update/delete also generated `PutPipelineRule` / `DeletePipelineRule` management
  events under `monitoring.amazonaws.com` with `invokedBy: observabilityadmin.amazonaws.com`.
  Successful rule events included the pipeline ARN, selection criteria, `dataset/default`, and full
  rule configuration. The missing dependency generated a separate denied `PutPipelineRule` event.
- `TestTelemetryPipeline` logged both the processor configuration and the synthetic record body.
  Never place real credentials in a processor test.

## Cleanup and cost

All disposable pipelines reached deletion and `ListTelemetryPipelines` returned empty. Every
temporary IAM role, user, inline policy, access key, API Gateway endpoint, Lambda function, canary
secret, CloudWatch Logs resource policy, and log group was deleted; prefix-filtered inventories
returned empty. The metrics selection criteria matched no data and the API-pull canary endpoint
received no request, so the tests incurred only negligible control-plane and serverless activity.

No unexpected security defect survived validation, so no private 0-day report was created. The
vendor-endpoint/Secrets Manager credential-relay hypothesis remains queued for a longer canary
observation and an update-specific least-privilege test.

## Sources

- https://docs.aws.amazon.com/cloudwatch/latest/observabilityadmin/API_CreateTelemetryPipeline.html
- https://docs.aws.amazon.com/cloudwatch/latest/observabilityadmin/API_UpdateTelemetryPipeline.html
- https://docs.aws.amazon.com/cloudwatch/latest/observabilityadmin/API_TestTelemetryPipeline.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/pipeline-processors.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/pipeline-sinks.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/pipeline-iam-reference.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_observabilityadmin.html
