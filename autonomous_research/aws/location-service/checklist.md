# Amazon Location Service — open research checklist

- [ ] Run a two-key differential parser matrix where neither key alone satisfies the complete action/resource/referrer tuple; duplicate-key selection alone is not a finding.
- [ ] Test legacy v1 map-name path canonicalization (`..`, encoded slash/backslash, double encoding) with two maps whose response hashes differ.
- [ ] Characterize `AllowAndroidApps` and `AllowAppleApps` headers/tokens with an actual mobile SDK and a hostile custom client.
- [ ] Repeat update/delete invalidation timing from multiple Regions/networks; escalate only if stale authorization is durable or violates a documented revocation guarantee.
- [ ] Enable a disposable `AWS::GeoMaps::Provider` data-event selector and record API-key identity/redaction fields, restoring the original selector exactly afterward.
