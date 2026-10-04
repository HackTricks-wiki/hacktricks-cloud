# Policy Troubleshooter — open leads

## Exact audit delivery
- [ ] When the API is already enabled in a disposable project, enable IAM `ADMIN_READ` Data Access
      logging temporarily, send one harmless troubleshoot query and record the exact private
      `GetEffectivePolicy` method/service/resource fields. Restore the original audit config.
- [ ] In the same disposable environment, check whether the outer `iam:troubleshoot` request emits
      any `policytroubleshooter.googleapis.com` audit entry. Do not infer a category from the
      diagnostic nature of the method.

## Partial-result boundaries
- [ ] Use pre-propagated custom roles to isolate the minimum get-IAM-policy and custom-role read
      permissions for project, folder, organization and service-account targets. Record which
      explanation fields change to `Unknown`; create no infrastructure beyond temporary IAM
      identities/roles and remove all active grants after testing.
- [ ] With an approved disposable Workspace group, compare results with and without `groups.read`
      and document whether binding names remain visible while membership becomes `Unknown`.
