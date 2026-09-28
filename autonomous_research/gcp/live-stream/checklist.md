# Live Stream API — open validation leads

- [ ] On a disposable RTMP distribution, confirm whether `channels.list` returns the same plaintext
  `streamKey` as `channels.get` and whether any field mask or response redaction differs by method.
- [ ] Test RTMP and SRT input connection admission under absent, matching, and non-matching
  `securityRules.ipRanges`, recording `inputAccept`/`inputError` only after explicitly enabling
  channel activity logs.
- [ ] With generated non-sensitive media, validate the minimum `assets.create` + `events.create`
  slate chain against an existing running channel and capture the service-agent Storage principals.
- [ ] Determine whether an asset can be referenced across projects or locations; do not publish a
  cross-project claim without a successful disposable test or explicit primary documentation.

All live checks require a strict cost timer because running channels are billed. Stop and delete the
channel/input/assets/events immediately, remove bucket grants, and delete generated output.
