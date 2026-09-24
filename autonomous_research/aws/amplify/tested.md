# AWS Amplify — tested

## UpdateApp role-repoint privesc (iamServiceRoleArn / computeRoleArn) — authz VERIFIED (cont.67) [net-new]

- **Technique:** amplify:UpdateApp + iam:PassRole repoints the app's build/service role
  (--iam-service-role-arn) or SSR runtime role (--compute-role-arn) onto a chosen more-privileged,
  amplify.amazonaws.com-trusting role; then a build (buildSpec/env-var RCE) runs as the new SERVICE
  role and an SSR request runs as the new COMPUTE role. Distinct from the page's pre-existing env-var/
  buildSpec RCE which runs as the EXISTING role (no PassRole).
- **Authz VERIFIED:** attacker = amplify:UpdateApp + iam:PassRole on target -> update-app on bogus app
  id `d0000000000000` with --iam-service-role-arn AND (separately) --compute-role-arn both returned
  NotFoundException (App not found), NOT AccessDenied -> IAM gate passed for both role fields.
- **Min perms:** amplify:UpdateApp + iam:PassRole (role trusting amplify.amazonaws.com). Trigger via
  StartJob / auto-build / webhook (build) or an SSR request (compute).
- **Teardown:** target + attacker probe roles deleted, verified NoSuchEntity. No infra left.
- **Wiki:** aws-amplify-privesc/README.md new subsection under the UpdateApp technique, ref [17].
