# BigQuery Engine for Apache Flink — open leads

## Identity boundaries

- [ ] In a project where the preview API is already enabled/allowlisted, create a low-privilege
      deployment identity and deployment. Grant a second principal only
      `managedflink.jobs.create` plus staging-object write, with no
      `iam.serviceAccounts.actAs`. Submit a harmless marker job to the existing deployment and
      determine whether the API rechecks `actAs`. Delete the job, deployment, artifacts, test IAM
      bindings and identities immediately after the result is captured.
- [ ] Repeat the on-demand form with the default workload identity and a custom workload identity
      to isolate the exact attachment check and error/audit behavior. Do not infer equivalence with
      the deployment-attached path.
- [ ] Determine what the product calls its “Managed Flink Default Workload Identity,” where its IAM
      policy is managed, and whether a job developer can influence or replace it indirectly.

## Runtime credential and secret exposure

- [ ] From a harmless job, inventory only approved credential interfaces: ADC/client-library
      identity, environment variables, filesystem mounts and metadata/DNS reachability. Do not
      assume the Compute Engine metadata endpoint exists; record any audience/scope restrictions.
- [ ] Create a deployment with a disposable Secret Manager version in `secretsPaths`, submit a job
      as a developer-only principal and determine whether every job in that deployment can read the
      shared secret. If yes, assess whether deployment read access exposes enough path metadata to
      turn `jobs.create` into a secret-read oracle. Delete the secret version and all Flink objects.
- [ ] Test whether a cross-project deployment workload identity or cross-project staging object is
      accepted and which caller/service-agent grants are enforced. Look for confused-deputy
      behavior; keep both projects owned by the test account.

## Artifact and update boundaries

- [ ] Test when `jobGraphUri`, `artifactUris` and `jarUris` are fetched and whether mutable object
      replacement after validation but before worker fetch creates a TOCTOU path. Use harmless
      distinguishable marker artifacts and remove every object/version afterward.
- [ ] Confirm that `managedflink.jobs.update` is limited to parallelism/autotuning and cannot swap
      graph/artifact URIs or move a job to another deployment through raw field masks.
- [ ] Exercise `managedflink.sessions.create/update` with minimum permissions and determine whether
      a session permits arbitrary code submission, which identity it inherits, and whether it
      exposes secrets or network access beyond jobs.

## Telemetry

- [ ] Before creating test resources, temporarily enable only the relevant Data Access categories
      in a disposable allowlisted project. Capture exact service name, `methodName`, log ID,
      resource type/name, long-running-operation legs and caller attribution for deployment/job/
      session get/list/create/update/delete. Restore the original audit configuration.
- [ ] Correlate caller-side Cloud Storage artifact writes, service-agent artifact reads, workload
      target-service calls and Managed Flink control-plane events. Check whether job graph or
      artifact URIs and workload identity appear in the audit request/response.
