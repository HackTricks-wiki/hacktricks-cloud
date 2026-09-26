# AWS Well-Architected Tool — attack checklist

## Share invitation ownership

- [ ] Test whether `UpdateShareInvitation` binds the invitation ID to the intended recipient. A same-account two-user fixture is impossible: `CreateWorkloadShare` rejects a user belonging to the workload owner's account. Requires a second explicitly authorized AWS account/user; do not substitute an unrelated account.
- [ ] With that fixture, test unauthorized `ACCEPT` and `REJECT` independently, followed by intended-recipient acceptance to prove the invitation was not consumed.
- [ ] Verify `ListShareInvitations` never exposes another recipient's invitation metadata.

See `share-invitation-binding-2026-09-26.md` for the completed same-account preflight and cleanup.

