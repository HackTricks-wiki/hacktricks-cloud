# Batch — open leads

Last researched: 2026-09-28

## Expected-behavior validation

- [ ] With an already-approved disposable project/account, capture which Compute Engine resource
      methods and principal fields accompany a Batch-created VM. Do not create a job solely for this
      check without a cost and cleanup plan.
- [ ] Verify the exact failure timing for a custom account missing only `batch.states.report`, and
      separately confirm that omitting Logs Writer succeeds when `logsPolicy` is absent.
- [ ] Test Shared VPC attachment only where host-project grants and cleanup are already controlled.
      Do not claim `batch.jobs.create` alone can select arbitrary subnets.
- [ ] Revisit service-agent confused-deputy boundaries if Batch adds new allocation-policy fields.
      Require a demonstrated bypass of the caller's `iam.serviceAccounts.actAs` or network/resource
      authorization gate before treating it as a new technique or vulnerability.

## Safety and cleanup

- Use one minimal task and the smallest practical machine; record the job and every underlying
  Compute resource before execution.
- Delete the Batch job and verify VMs, disks, addresses, and job-scoped logs/resources after testing.
- Never print live tokens or secrets into Cloud Logging. Use a controlled sink and revoke/expire any
  captured short-lived credential.
