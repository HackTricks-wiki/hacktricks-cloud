# Organization-wide Sign-In RCP path, 2026-09-26

## Expected behavior

AWS [explicitly documents a Sign-In RCP](https://docs.aws.amazon.com/signin/latest/userguide/console-access-control.html) that denies console sign-in outside a network perimeter for member accounts across an organization. RCPs [do not apply](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html) to the management account. The necessary policy covers `signin:Authenticate`, `signin:AuthorizeOAuth2Access`, and `signin:CreateOAuth2Token`. A management-account principal needs `organizations:CreatePolicy` and `organizations:AttachPolicy`; an organization with RCP or Sign-In console authorization disabled needs `organizations:EnablePolicyType` and/or `signin:PutConsoleAuthorizationConfiguration` respectively. AWS docs describe all operations and sign-in denial CloudTrail records.

## Lab boundary

The current assumed role is administrator of organization member account `228478051196`, not management account `418720621023`. The management account is out of reach; no RCP was created or attached, and no console authorization was enabled. The public technique is grounded in direct AWS documentation. It must be tested for exact effective behavior only in a disposable organization with a tested recovery path.

## Limits and negative branches

- RCPs do not affect management-account sign-in.
- SigV4 API access remains available.
- An RCP attached to a narrow OU affects only accounts beneath that target, not every member account.
- Attaching an RCP is ineffective if its policy type is disabled. Console authorization may also need activation.
- The existing account-level Sign-In policy entry is a distinct, narrower path.
