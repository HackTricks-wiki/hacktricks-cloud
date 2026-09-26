# Amazon Location API-key boundaries — 2026-09-26

## Scope and fixture

Tested v2 Geo Maps API keys in `us-east-1` against the default provider. The strict test principal had only:

- `geo:CreateKey`, `geo:UpdateKey`, and `geo:DeleteKey` on one exact prospective API-key ARN.
- `geo-maps:GetTile` on `arn:aws:geo-maps:us-east-1::provider/default`.

It had no Places, Routes, static-map, or other Location permission. Every key and IAM role was deleted after its test cycle. No map resource, VPC, trail, or compute was created.

## Verified expected attacks

### Durable service-level bearer key

The restricted role minted a no-expiry key, used it without SigV4, and the key continued returning map tiles after the complete creator IAM role was deleted. `geo:CreateKey` alone failed: AWS additionally required the issuer to hold the exact data action on the delegated resource. An attempted `UpdateKey` expansion to `geo-places:Geocode` was denied because the issuer lacked that action.

This is useful Location-level persistence but not privilege escalation: the caller can preserve only its existing Location read scope. It was published in the persistence page.

### Harvested keys and referrer restrictions

After a forced restriction update to `AllowReferers=["https://allowed.example/*"]`:

- exact allowed header from `curl`: 200;
- missing header: 403 immediately and two seconds later;
- suffix confusion, user-info, uppercase scheme/host, trailing dot, Origin-only: 403;
- duplicate Referer headers: AWS used the first header (`bad,good` denied; `good,bad` succeeded);
- a comma-combined bad/good value was denied.

Sending the exact allowed string from a custom client is documented/expected, not a bypass. The public unauthenticated-access page now states this precisely.

## Secure boundary results

| Case | Result |
| --- | --- |
| Correct `GetTile` / `us-east-1` tuple | 200 |
| Same key against `us-west-2` | 403 |
| Same key against Places `Geocode` | Denied |
| Same key against `GetStaticMap` | Denied |
| Random key | 403 |
| `key=valid&key=invalid` | 403 |
| `key=invalid&key=valid` | 200 — deterministic last-value selection |
| Two identical valid values | 200 |
| `key=valid&key=` | 403 |
| percent-decoded name `k%65y=valid` | 200 — logical equivalent |
| case-changed name `Key=valid` | 403 |
| `x-api-key` header instead of query | 403 |

Last-value selection and decoded-equivalent parameter names are parser characterization, not vulnerabilities: the selected value itself still had to authorize the full request. A future two-key differential should combine keys where neither key alone satisfies action/resource/referrer but a parser desynchronization could accidentally compose them.

## Update, deletion, and revocation behavior

- Tightening a recently used key without `ForceUpdate=true` failed with the documented warning.
- With force update, the new referrer restriction applied immediately.
- Ordinary cleanup of a recently used active key failed; `ForceDelete=true` is required.
- A never-updated key rejected a fresh request immediately after force deletion.
- In three exact create/use/force-update/use/force-delete repetitions, one fresh request immediately after deletion returned 200 and the next request two seconds later returned 403.
- An earlier equivalent cycle continued for at least seven seconds. No persistence beyond that was retained because the bearer was deliberately discarded after deletion.

This is a short distributed invalidation caveat, not currently an AWS vulnerability: the docs promise irreversible deletion but give no propagation SLA, and no durable boundary bypass was found. Responders should verify revocation from the data plane instead of relying only on `ListKeys` becoming empty.

## Logging

- `CreateKey`, `UpdateKey`, and `DeleteKey` are management events under `geo.amazonaws.com` and are in default Event History.
- `GetTile` and `GetStaticMap` are optional `AWS::GeoMaps::Provider` data events and are off by default.
- Places and Routes v2 have their own optional provider data-event resource types.
- AWS explicitly publishes no CloudTrail events for the free unauthenticated `GetStyleDescriptor`, `GetGlyphs`, and `GetSprites` APIs.
- CloudWatch exposes volume metrics including `ApiKeyName`/operation dimensions.

After propagation, Event History confirmed:

- `CreateKey` logs `KeyName`, `NoExpiry`, complete `AllowActions` and `AllowResources`; `responseElements.Key` is `***`.
- `UpdateKey` logs complete actions/resources and `ForceUpdate:true`, but each `AllowReferers` value is `***`.
- `DeleteKey` logs the key name and `forceDelete:"true"`.
- Denied delegation attempts disclose the missing action/resource in the error response, including the failed `geo-places:Geocode` expansion.
- All are `readOnly:false`, `managementEvent:true`, `eventCategory:Management`.

## Cleanup verification

Final `ListKeys` filtered by `HTLocation*` returned an empty array. `HTLocationKeyResearch0926` did not exist. No other service resource was created.
