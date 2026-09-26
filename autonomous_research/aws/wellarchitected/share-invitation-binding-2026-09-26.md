# Well-Architected `UpdateShareInvitation` recipient binding — 2026-09-26

## Status

**Fixture-blocked; not a security result.** The proposed same-account isolation test cannot create a valid workload invitation. `CreateWorkloadShare` returned:

```text
ValidationException: [Validation] The shared with user cannot belong to the sharer's account.
```

Request ID: `160844f0-3878-4db3-89f3-aa08f37d591e`.

No invitation was created and `UpdateShareInvitation` was not exercised. The recipient-binding hypothesis remains open only for a second AWS account whose use is explicitly authorized.

## Why the hypothesis remains relevant

`UpdateShareInvitation` accepts only a 128-bit invitation ID and an `ACCEPT`/`REJECT` action. The Service Authorization Reference lists no resource type for the action, so recipient policies must use `Resource: "*"`; the Well-Architected service must bind the opaque invitation to its intended account/user.

A future authorized two-account matrix should verify that a principal in account B cannot accept or reject an invitation intended for a different principal/account C even when B knows the invitation ID. The secure result is `AccessDeniedException` or indistinguishable `ResourceNotFoundException`, followed by successful acceptance by the intended recipient.

## Attempted disposable fixture

- One synthetic workload in `us-east-1`.
- Two synthetic IAM users in the owner account, each with only:
  - `wellarchitected:ListShareInvitations`
  - `wellarchitected:UpdateShareInvitation`
- One memory-only access key per user.
- Intended share target: the exact ARN of user U1.

The service rejected the share because U1 was in the owner's account. This constraint is stronger and more explicit than the public guide's general wording about sharing with users, and it prevents using two local principals as an ownership oracle.

## Cleanup

The `finally` handler deleted the workload, both access keys, both inline policies, and both IAM users. Independent post-test inventory returned:

- no workload whose name starts with `ht-wa-invite-`;
- no IAM user whose name starts with `ht-wa-invite-`.

## References

- https://docs.aws.amazon.com/wellarchitected/latest/APIReference/API_UpdateShareInvitation.html
- https://docs.aws.amazon.com/wellarchitected/latest/APIReference/API_CreateWorkloadShare.html
- https://docs.aws.amazon.com/wellarchitected/latest/APIReference/API_ListShareInvitations.html
- https://docs.aws.amazon.com/wellarchitected/latest/userguide/workloads-sharing.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_wellarchitected.html

