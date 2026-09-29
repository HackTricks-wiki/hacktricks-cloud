# AWS Amplify — tested

## CreateWebhook credential-less build trigger — live VERIFIED (2026-09-29) [net-new]

- An app-ARN-only `amplify:CreateWebHook` policy was denied against the branch ARN. The corrected caller held only that action on the exact branch and successfully minted a webhook URL.
- The access key, policy, and IAM user were deleted before the URL was invoked. An unsigned JSON POST returned HTTP 202 and changed the branch job count from zero to one.
- CloudTrail recorded `CreateWebhook` with app, branch, description, webhook ARN/ID, and a redacted `webhookUrl: "***"`. No caller `StartJob` event accompanied the external trigger.
- All three fixtures (authorization-boundary, local-output-error, and conclusive run) were cleaned. Independent inventories found no prefixed app, CodeCommit repository, IAM role, or IAM user.
- Published as Amplify branch-level persistence; it becomes code-execution persistence only when paired with an already poisoned build path.

## UpdateBranch environment-variable build RCE — live VERIFIED (2026-09-29) [net-new]

- A disposable CodeCommit-connected static app contained a benign repository `amplify.yml` whose build phase invoked Node.js and a dormant local hook file.
- A disposable IAM caller held only `amplify:UpdateBranch` on the exact branch ARN and `amplify:StartJob` on that branch's `jobs/*` ARN. It had no Amplify read access, `iam:PassRole`, or SSM access.
- `UpdateBranch` set `NODE_OPTIONS=--require=./hook.js`; `StartJob RELEASE` succeeded. The build log contained the hook marker and the deployed marker artifact proved execution.
- The hook called `ssm:GetParameter` through the app's existing service role and published only a SHA-256 digest. It matched the locally expected canary digest. CloudTrail attributed the read to `assumed-role/<fixture-role>/BuildSession`, proving existing-role access rather than caller access.
- `UpdateBranch` and `StartJob` were default management events. The former recorded the app/branch but redacted `environmentVariables` and `buildSpec` in both request and response as `***`.
- Negative boundary: a prior run replaced the branch `buildSpec`; `GetBranch` returned all 463 stored bytes, but a successful build ran none of those commands. The positive environment-variable run used a repository-controlled `amplify.yml`; direct branch-buildSpec RCE is therefore not claimed.
- Cleanup independently confirmed no prefixed Amplify app, CodeCommit repository, IAM user/role, or SSM parameter remained. The first negative-boundary fixture was also fully removed.
- Public technique added to `aws-amplify-privesc/README.md` with prerequisites, impact, stealth, and logs.

## UpdateApp role-repoint privesc (iamServiceRoleArn / computeRoleArn) — authz VERIFIED (cont.67) [net-new]

- **Technique:** amplify:UpdateApp + iam:PassRole repoints the app's build/service role (--iam-service-role-arn) or SSR runtime role (--compute-role-arn) onto a chosen more-privileged, amplify.amazonaws.com-trusting role; then a build (buildSpec/env-var RCE) runs as the new SERVICE role and an SSR request runs as the new COMPUTE role. Distinct from the page's pre-existing env-var/ buildSpec RCE which runs as the EXISTING role (no PassRole).
- **Authz VERIFIED:** attacker = amplify:UpdateApp + iam:PassRole on target -> update-app on bogus app id `d0000000000000` with --iam-service-role-arn AND (separately) --compute-role-arn both returned NotFoundException (App not found), NOT AccessDenied -> IAM gate passed for both role fields.
- **Min perms:** amplify:UpdateApp + iam:PassRole (role trusting amplify.amazonaws.com). Trigger via StartJob / auto-build / webhook (build) or an SSR request (compute).
- **Teardown:** target + attacker probe roles deleted, verified NoSuchEntity. No infra left.
- **Wiki:** aws-amplify-privesc/README.md new subsection under the UpdateApp technique, ref [17].
