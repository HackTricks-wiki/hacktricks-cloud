# Secure Source Manager — open ideas

- [x] On a disposable SSM instance, verify webhook create/update and authenticated-delivery telemetry; neither hook mutation produced an SSM audit entry, while delivery emitted IAM Credentials `GenerateIdToken` Data Access. Remove the hook, repository, instance and receiver immediately afterward.
- [ ] On a disposable SSM instance that can be deleted within the cost limit, verify whether branch-rule mutations, PR approve/merge, and `linkDeveloperConnect` produce Cloud Audit entries. Preserve actual `protoPayload.methodName` and required audit configuration. Remove the instance and every repository immediately afterward.
- [ ] Test whether nested or branch-specific CODEOWNERS files can bypass a root veto under the newly GA Code Owners feature. Publish only if a distinct security boundary fails; otherwise record the rejection here.
