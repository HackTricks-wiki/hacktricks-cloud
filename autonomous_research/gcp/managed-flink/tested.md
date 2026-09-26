# BigQuery Engine for Apache Flink — tested/reviewed

## 2026-09-26 — resource, identity and telemetry contract review

- Queried the current official REST discovery document. `JobSpec` carries `jobGraphUri`,
  `jarUris`, `artifactUris`, pipeline options and (for on-demand jobs) workload identity/network/
  secret configuration. `DeploymentSpec` carries only workload identity, network configuration,
  shared secret paths and limits. It has no executable-code field.
- Confirmed that `Job.deploymentId` attaches a job to an existing deployment, while an empty value
  creates an ephemeral on-demand cluster. The job-level `workloadIdentity` description explicitly
  says it is only used for on-demand jobs.
- Confirmed in the installed Cloud SDK and current official help that `jobs create` accepts JAR,
  Python and SQL inputs plus `--deployment` or `--workload-identity`. The implementation rejects
  using those two flags together, consistent with a deployment-attached job inheriting the
  deployment identity.
- Confirmed current role contents: `roles/managedflink.developer` has full job/session access but
  only read access to deployments; `roles/managedflink.admin` has `managedflink.*`; the service
  agent role contains `storage.objects.get` for staged artifacts.
- Removed the book's false claim that a deployment itself carries attacker code and auto-restarts
  it. Replaced it with the defensible persistence object: an unbounded streaming job attached to a
  deployment. Also removed the unsupported guarantee that raw Compute metadata-server token
  access exists in the managed runtime.
- Google currently publishes no Managed Flink audit-logging method table. Removed guessed
  `google.cloud.managedflink.v1.*.CreateJob/CreateDeployment` method names and Admin Activity
  classifications rather than presenting inferred telemetry as fact.
- `managedflink.googleapis.com` is `DISABLED` in `gcp-labs-eqd4ny8d`; the product help also warns
  that access can be invitation-only. Did not enable it, create a deployment/job, upload an
  artifact, or change IAM. No test resource requires cleanup.

## Book-quality decision

- Retained `managedflink.jobs.create` as post-exploitation because arbitrary JAR/Python execution
  under the effective workload identity follows directly from the public command and schema.
- Retained a long-running streaming job as persistence, but explicitly removed the guarantee of
  self-healing/indefinite restart.
- Did **not** add a privilege-escalation page. Identity inheritance is proven, but whether the API
  rechecks `iam.serviceAccounts.actAs` when adding a job to an existing deployment is not public
  and could not be tested in this project.
