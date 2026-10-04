# Cloud Runtime Configurator research checklist

## Completed 2026-09-28

- [x] Separate config policy self-grant from variable reads, writes, waiter signaling, config
      creation, and downstream workload behavior.
- [x] Recheck current predefined roles and custom-role support levels.
- [x] Reconcile the documented config IAM methods with the stale HTTP-404 claim.
- [x] Move variable-value disclosure to post-exploitation with exact known-path and enumeration
      permissions.
- [x] Check the current public REST discovery surface for variable/waiter IAM methods.
- [x] Recheck the official Cloud Audit Logs supported-service catalog.
- [x] Run a current config/policy/variable/waiter fixture and remove it completely.
- [x] Record the Deployment Manager support and shutdown dates without assuming that every new-
      customer restriction applies identically to the separate Runtime Config API.

## Safe future validation leads

- [ ] In a disposable whole project, validate the self-grant with a principal holding a custom role
      containing only `runtimeconfig.configs.setIamPolicy`. Project custom-role deletion is
      recoverable rather than immediate, so whole-project deletion is the required cleanup boundary.
- [ ] In that disposable project, enable an `allServices` Data Access audit configuration and repeat
      config/variable GETs. Capture any newly emitted method before changing the current “no
      documented/observed audit entry” wording; restore IAM and delete the project afterward.
- [ ] Probe variable/waiter IAM endpoints only if Google adds them to the public discovery/reference.
      Permission names alone are not evidence that a callable resource-level policy exists.
- [ ] Recheck whether the Runtime Config API and existing resources remain callable as the adjacent
      June 30, 2027 Deployment Manager shutdown approaches. Remove the pages when the Runtime Config
      attack surface is actually unavailable rather than inferring its retirement from the separate
      Deployment Manager/V2 notice.
- [ ] If a real workload uses a Runtime Config value as executable code, URL, database endpoint, or
      credential source, document that consumer's exact validation and identity boundary. Do not
      promote generic variable write into privesc from speculation alone.

## Independent cross-review completed 2026-09-28

- [x] Verify the one config-IAM privesc H3 and one variable-read post-exploitation H3 classification.
- [x] Recheck config IAM resource scope, predefined roles, and `TESTING` custom-role support.
- [x] Validate the policy-preserving `jq` merge and complete-policy replacement boundary.
- [x] Separate the documented Deployment Manager/V2 shutdown date from the independently callable
      Runtime Config API, for which the cited notice gives no separate shutdown date.
- [x] Remove unsupported blanket deny-policy and principal-access-boundary claims.
- [x] Recheck the audit-catalog omission and preserve the bounded live-observation wording.
- [x] Independently confirm the live fixture is absent without changing cloud state.
- [x] Reject a separate persistence page as duplication of the same config IAM binding, with no
      distinct durable mechanism or additional defensive value.
