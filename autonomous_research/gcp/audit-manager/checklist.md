# Audit Manager — open ideas

## Hierarchical and cross-project authorization

- [ ] In an already-enabled disposable folder or organization scope, put an empty destination bucket
      in a child project. Give the corresponding Audit Manager service identity object-create but
      give the isolated caller no Storage permission. Prove absence with `testIamPermissions`, then
      compare `validateOnly=true` against a documented Storage Admin/legacy bucket owner positive
      control. A 2xx negative result is private-first; never create a real enrollment for this test.
- [ ] Split `resourcemanager.folders.setIamPolicy` or
      `resourcemanager.organizations.setIamPolicy` from `auditmanager.locations.enrollResource` to
      capture which resource reports each denial and whether both permissions appear in the
      authorization log.
- [ ] Reduce the positive Storage role into exact custom permissions one at a time. Current live
      evidence establishes `storage.buckets.getIamPolicy` as the first missing permission, while
      Google's supported contract remains Storage Admin or legacy bucket owner.

## Validation, logging and lifecycle

- [ ] Determine whether repeated or multi-destination `validateOnly` requests short-circuit on the
      first unauthorized bucket or leak eligibility for later destinations. Use only synthetic empty
      buckets owned by the lab and retain no real enrollment.
- [ ] Recheck whether Admin Activity continues to omit both destination and `validateOnly` from the
      request payload across project, folder and organization scopes. If so, document the detection
      limitation only with a defensible compensating Storage/IAM signal.
- [ ] Monitor discovery for an unenroll/delete RPC. Until one exists, do not invoke non-validation
      enrollment merely to exercise lifecycle behavior because complete cleanup cannot be guaranteed.
