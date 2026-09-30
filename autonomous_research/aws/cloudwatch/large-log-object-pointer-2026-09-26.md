# CloudWatch Logs Large Log Object pointer authorization — 2026-09-26

## Result

**No authorization vulnerability found.** `GetLogObject` securely resolved each opaque Large Log Object (LLO) pointer back to its source log group before evaluating IAM. A role allowed to read only group A was explicitly denied when it supplied a valid pointer from group B, and a role with no CloudWatch Logs permissions was denied on group A.

An explicit `logs:Unmask` deny also blocked `GetLogObject(..., unmask=true)`. Mutated, cross-region, and deleted-group pointers did not return content.

Do not add an attack to the public book from this result.

## Hypothesis

`GetLogObject` accepts only `logObjectPointer` and `unmask`; it does not accept a log-group identifier. The IAM action is nevertheless `logs:GetLogRecord`, scoped to a log-group ARN. This requires the service to resolve pointer → source group before IAM authorization. Two possible failures were tested:

1. treat the pointer as a bearer capability and skip source-group IAM evaluation;
2. stream raw protected content when the caller lacks or is explicitly denied `logs:Unmask`.

## Fixture

Final disposable prefix: `ht-llo-1af6fe1dfc` in `us-east-1`.

- Groups: `/ht-llo-1af6fe1dfc-a` and `/ht-llo-1af6fe1dfc-b`
- Stream in each group: `s`
- Retention: one day
- Data protection: `EmailAddress`, with empty audit destination and `MaskConfig`
- OTLP records: one per group, 1,300,407-byte request bodies, distinct fill and email marker
- Ingestion request IDs: `655d1b53-0a11-446e-9961-327b7ac80588` and `4442499f-a415-461f-9344-e0ba9db08cb6`

Both SigV4-signed `POST https://logs.us-east-1.amazonaws.com/v1/logs` requests returned HTTP 200. CloudWatch truncated the `body` field into an LLO and added `@ptr.$['body']` to the expanded log record.

The correct pointer-resolution flow was:

1. Logs Insights returns generic `@ptr`, a `GetLogRecord` pointer.
2. `GetLogRecord` returns the expanded record containing `@ptr.$['body']`.
3. The value of `@ptr.$['body']` is the input for `GetLogObject`.

Passing the generic Insights `@ptr` directly to `GetLogObject` correctly returned `InvalidParameterException: Invalid log object pointer format.`

## Principals

`ScopedA`:

- allow `logs:GetLogRecord` on both exact ARN forms for group A;
- explicit deny `logs:GetLogRecord` on both exact ARN forms for group B;
- explicit deny `logs:Unmask` on `*`.

`UnmaskA`:

- allow `logs:GetLogRecord` and `logs:Unmask` on both exact ARN forms for group A.

`ZeroReader`:

- no inline or managed permissions.

## Final matrix

| Call | Result |
| --- | --- |
| Admin, pointer A, `unmask=true` | Success; 1,300,033 bytes; exact A marker present, B absent |
| `UnmaskA`, pointer A, `unmask=true` | Success; identical byte count/hash and marker result |
| `ScopedA`, pointer A, `unmask=true` | `AccessDeniedException` on `logs:Unmask` for group A |
| `ScopedA`, pointer B, `unmask=false` | `AccessDeniedException` on `logs:GetLogRecord` for group B, explicit deny |
| `ZeroReader`, pointer A | `AccessDeniedException` on `logs:GetLogRecord` for group A |
| Admin, one-character-mutated pointer A | `InvalidParameterException` |
| Admin in `us-west-2`, pointer A | `ResourceNotFoundException: LogGroup doesn't exist` |
| Admin, pointer B after deleting group B | `ResourceNotFoundException: LogGroup doesn't exist` |

Pointers and returned content were never printed or retained. The ledger keeps pointer SHA-256 values only. The authorized admin and `UnmaskA` results had identical SHA-256 values.

## Non-security behavior worth retesting

For a data-protected LLO, both admin and `ScopedA` calls with `unmask=false` returned:

```text
ResourceNotFoundException: The requested log object could not be found.
```

The same pointer immediately succeeded with `unmask=true` for principals allowed `logs:Unmask`. Documentation describes `unmask=false` as returning masked/redacted content, so this appears to be a functionality/documentation mismatch. It does not expose data or create an attacker advantage and is not a security report by itself.

The stream API also produced transient `LimitExceededException: Rate exceeded` when calls were sent in quick succession. A two-second inter-call delay and bounded four-second retry resolved it.

## Failed fixture iterations

1. `fields *` is not valid Logs Insights QL; ingestion succeeded, the query failed, and cleanup ran.
2. A valid query returned only the generic `@ptr`; the first parser looked only for `@ptr.` and timed out until interrupted. `finally` cleanup ran.
3. IAM rejected an empty inline policy for `ZeroReader`. The role should simply have no policy. Cleanup ran.
4. Generic `@ptr` was passed directly to `GetLogObject`, producing only invalid-format errors. The correct two-step expansion was then implemented.

No failed iteration reached an authorization anomaly, and every attempt removed its groups and roles.

## Cleanup verification

Group B was deliberately deleted before its lifecycle-pointer test. Final cleanup then:

1. deleted any remaining data-protection policy;
2. deleted group A and any remaining group B;
3. deleted all inline role policies and roles;
4. independently listed the prefix across Logs and IAM.

Final inventory returned no matching log groups or roles.

## References

- https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_GetLogObject.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_HTTP_Endpoints_OTLP.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/permissions-reference-cwl.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_logs.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html
