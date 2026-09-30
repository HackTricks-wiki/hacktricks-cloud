# VPC Service Controls — open validation leads

- [ ] Capture the audit sequence for `dry-run update`, `dry-run enforce`, and `dry-run drop` in a disposable access policy. Confirm the `UpdateServicePerimeter` start/completion entries and the exact `metadata.dryRun` behavior for a harmless denied request. Restore or delete all test policy objects immediately.
- [ ] Validate `vpcAccessibleServices` separately against restricted/private VIP traffic from a disposable VM. Do not claim that adding `iamcredentials.googleapis.com` creates token-minting capability: IAM authorization and the target service account remain independent prerequisites.
- [ ] Keep post-exploitation coverage on each protected service page. Add a VPC-SC-specific post technique only if a future method directly discloses data, creates execution, or produces a distinct foothold without first weakening the perimeter.
