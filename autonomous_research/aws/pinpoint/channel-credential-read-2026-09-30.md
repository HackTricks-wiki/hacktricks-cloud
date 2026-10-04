# Pinpoint push-channel stored-credential audit — 2026-09-30

## Hypothesis

The current Pinpoint SDK model exposes `Credential` in both `GCMChannelResponse` and
`BaiduChannelResponse`. The descriptions call it the Google server/Web API key or Baidu Cloud Push
API key. Existing research had treated read-operation secret-looking fields as normally redacted,
so these getters required an empirical check before either publishing a technique or relying on that
general rule.

Authorized account: `228478051196`; Region: `us-east-1`; role:
`ChackBotAdministratorRole`. Only synthetic disabled channels were attempted. No message, campaign,
journey, endpoint, phone resource, provider account, or real provider credential was used.

## Live results

| Probe | Result | Decision |
|---|---|---|
| Create disposable Pinpoint project | Succeeded | Safe empty fixture. |
| `UpdateGcmChannel` with a fake API key and `Enabled=false` | `BadRequestException: FCM returned 404 UNREGISTERED` | The service validates the key against FCM even while disabled; no stored GCM fixture was created. |
| Existing project/channel inventory | Zero applications | No real GCM credential was available for an authorized read-only test. |
| `UpdateBaiduChannel` with synthetic API/secret keys and `Enabled=false` | Succeeded | Service accepts the disabled synthetic fixture. |
| Update response `BaiduChannelResponse.Credential` | Absent/empty | The write does not echo the submitted API key. |
| `GetBaiduChannel` response `Credential` | Absent/empty | The documented/modelled credential is redacted or omitted in current runtime behavior. |
| Search getter response for submitted Baidu secret | No match | The secret key is not returned elsewhere in the response. |

The Baidu result is a strong negative: `mobiletargeting:GetBaiduChannel` is configuration metadata,
not a stored-secret getter. Do not add it to the book as credential theft.

GCM remains unproven rather than accepted. It should be tested only in an authorized account that
already has a disposable real FCM project/key, because using an arbitrary third-party key would be
out of scope and a fake key cannot reach the read boundary.

## Cleanup proof

- First project ID `83f0bdb979ea48e8885ecd1f8cf5c58b`: `GetApp` returned
  `NotFoundException`; matching-name inventory empty.
- Second project ID `50215166267146f98d86ab02452b0c48`: `GetApp` returned
  `NotFoundException` after explicit deletion.
- Final pre-existing Pinpoint inventory: zero applications.
- Cost-bearing resources and provider messages: none.

## Publication and disclosure decision

No public technique and no private vulnerability report. The Baidu candidate is closed. The GCM
candidate is deferred until a legitimate disposable FCM credential is available; documentation and
SDK fields alone are insufficient because the Baidu field proved misleading.

## Sources

- https://docs.aws.amazon.com/pinpoint/latest/apireference/apps-application-id-channels-gcm.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_pinpoint.html
- https://docs.aws.amazon.com/pinpoint/latest/developerguide/permissions-actions.html
