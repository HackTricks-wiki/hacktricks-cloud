# AWS Signer — tested

## VERIFIED live (lab 228478051196, us-east-1) — 2026-09-25
### signer:AddProfilePermission cross-account trusted-profile share  [enriched matrix row 53]
- put-signing-profile platformId=AWSLambda-SHA384-ECDSA (AWS-managed key, no ACM signingMaterial) -> profile created.
- add-profile-permission --action signer:StartSigningJob --principal 123456789012 -> ResourceNotFoundException "Principal not found" (validates account existence, like SES delegate).
- add-profile-permission --principal 228478051196 (real acct) -> ACCEPTED, revisionId returned. list-profile-permissions shows stored {action:signer:StartSigningJob, principal, statementId} in the profile resource policy.
- => a real external attacker account is accepted; nonexistent rejected. Cross-account hook = StartSigningJob --profile-owner <victim-acct> so grantee signs under victim's TRUSTED profile (defeats profile-pinning consumers, unlike ECR repoint-to-attacker-profile which needs consumers not to pin).
- Teardown: remove-profile-permission (needs revisionId) + cancel-signing-profile -> status Canceled (terminal; no hard-delete for signing profiles, expected). No active ht_signer profiles remain.
- Min-perms attacker(owner side): signer:AddProfilePermission. Grantee side: signer:StartSigningJob/SignPayload on the shared profile.

## Distinction from existing coverage
- ECR post-exploitation page: managed-signing repoint to attacker's OWN profile (needs consumers not to pin). This is complementary: abuse the VICTIM's trusted profile directly.
- Cross-account matrix row 53 pre-existed as a terse line; upgraded to Verified with profileOwner mechanism + principal-existence gate.
