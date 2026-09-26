# CodeArtifact — attack checklist

## Completed

- [x] Authorization token cannot cross to a sibling repository outside the caller's `ReadFromRepository` scope.
- [x] Existing tokens honor a newly attached explicit IAM deny after normal IAM propagation.
- [x] Newly minted tokens after that deny have the same effective repository authorization.
- [x] Invalid/mutated and absent tokens fail authentication.

## Future high-signal variations

- [ ] Cross-account domain/repository resource-policy intersection: verify a token cannot use a repository grant unless the external identity also has its required identity-based allow.
- [ ] Repository policy removal/revocation on an already-issued external-account token.
- [ ] Package-asset and publish actions: verify token authorization remains action/resource-specific for `GetPackageVersionAsset`, `PublishPackageVersion`, and `PutPackageMetadata` rather than only repository-level ping.
- [ ] Service bearer-token Region binding and dual-stack endpoint behavior.

Only promote a result if it crosses a documented domain/repository/action boundary or survives a settled explicit deny. Expected token lifetime beyond an assumed-role session is documented behavior when duration is nonzero, not a vulnerability.

