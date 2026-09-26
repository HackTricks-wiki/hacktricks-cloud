# Secure Source Manager — open ideas

- [ ] On a disposable SSM instance that can be deleted within the cost limit, verify whether branch-rule mutations, webhook create/update, PR approve/merge, and `linkDeveloperConnect` produce Cloud Audit entries. Preserve actual `protoPayload.methodName` and required audit configuration. Remove the instance and every repository/hook immediately afterward.
- [ ] Test whether nested or branch-specific CODEOWNERS files can bypass a root veto under the newly GA Code Owners feature. Publish only if a distinct security boundary fails; otherwise record the rejection here.
