# AppStream existing image-builder streaming URL — 2026-09-30

## Outcome

Documented `appstream:CreateImageBuilderStreamingURL` as a standalone existing-builder access and
conditional machine-role escalation primitive. It does not require builder creation/update,
Describe access, or caller-side PassRole.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- The API accepts only an image-builder name and optional URL validity from 1 to 604800 seconds.
- The builder must exist and be running.
- Non-domain-joined Windows builders offer the local Administrator account. Linux builders
  automatically sign in as `ImageBuilderAdmin` with root privileges.
- Domain-joined Windows builders may require a domain account with local-administrator rights.
- If `AccessEndpoints` restrict streaming, the client must have reachability through an allowed
  AppStream interface endpoint.
- If the builder already has `IamRoleArn`, AppStream publishes its rotating credentials through the
  `appstream_machine_role` profile. The URL caller neither passes nor changes that role.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`. Existing AppStream inventory contained zero
image builders.

An inline STS session policy allowed only `appstream:CreateImageBuilderStreamingURL` on:

```text
arn:aws:appstream:us-east-1:228478051196:image-builder/ht-appstream-nonexistent-image-builder
```

Results:

- the exact builder and maximum validity reached `ResourceNotFoundException`;
- another builder name was denied on its distinct image-builder ARN;
- `DescribeImageBuilders` on the allowed name was denied;
- the session policy contained no `CreateImageBuilder`, update action, or `iam:PassRole`.

No builder, image, URL, session, IAM role, network resource, or other asset was created. Cleanup was
vacuous.

## Impact boundaries

On a compatible running builder, the bearer URL provides local administrator/root access to the
golden-image workspace. This exposes image contents, installed software, configuration, cached data,
private-network access, and any attached machine-role credentials. Domain credentials and streaming
access endpoints can block direct access in the constrained cases described above.

## Telemetry

CloudTrail recorded the service-authorized failed request as a management write with
`readOnly:false`. It retained `name` and `validity=604800`, replaced
`responseElements.streamingURL` with `HIDDEN_DUE_TO_SECURITY_REASONS`, and represented the specific
builder-not-found failure as generic `UnknownError`. The denied alternate builder had
`requestParameters:null`.

Detect on the management write, requested builder and unusually long validity, then correlate the
creator with builder connection state and subsequent machine-role API calls. The account had no
real builder, so successful session behavior and downstream role activity remain deliberately
unclaimed.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateImageBuilderStreamingURL.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/managing-image-builders-connect-streaming-URL.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/service-name-info-in-cloudtrail.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_ImageBuilder.html
