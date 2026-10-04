# OS Config research ledger

## 2026-09-28 documentation and local-source audit

Scope was documentation, current local Google Cloud CLI help, current predefined-role metadata, and Google-maintained agent source. No API, VM, policy, patch job, bucket, IAM binding, or external resource was created or changed.

### Evidence checked

- Current VM Manager setup, patch, GA OS-policy, legacy guest-policy, policy-orchestrator, troubleshooting, and audit-log documentation.
- Current v1/v1beta/v2 REST method/resource contracts and current GA/Beta `gcloud compute os-config` help from Cloud SDK 586.0.0.
- Current predefined roles for Patch Job Executor, PatchDeployment Admin, OSPolicyAssignment Admin/Editor, GuestPolicy Admin/Editor, PolicyOrchestrator Admin, and OS Config Admin.
- Google-maintained Linux systemd unit and Windows installer for the default agent service identity.

### Verified authority boundaries

| Surface | Result |
| --- | --- |
| Patch job | `osconfig.patchJobs.exec` submits one project-scoped job; current documentation caps a job at 500 VMs. A remotely supplied step is a versioned Cloud Storage object, not inline content. Patch operation also depends on the project OS Config service agent retaining `roles/osconfig.serviceAgent`. |
| Patch artifact | A private object must be readable by the attached VM service account, including a compatible OAuth scope. Therefore `patchJobs.exec` alone is not arbitrary payload injection unless a controlled local/readable artifact already exists. |
| Patch deployment | Create/update persists the same patch configuration on a schedule. The narrow GA PatchDeployment Admin role contains those permissions. The role's `patchDeployments.execute` permission currently has no public v1 method or GA CLI command, so it was not treated as a separately usable primitive. |
| GA OS policy assignment | `osconfig.osPolicyAssignments.create` or `.update` can embed inline `exec` validate/enforce scripts. Assignments are zonal, not project-global. Create/update/delete are LROs. |
| Legacy guest policy | Beta create/update accepts an inline `scriptRun` software recipe at project scope. A given recipe name runs once. The documented rerun flow renames the recipe and recreates the policy; `UPDATED` recipes can use higher-version `updateSteps`. |
| Policy orchestrator | v2 orchestrators expand parent selectors into project-zone pairs and upsert GA assignments. Folder/org CLI selectors use numeric IDs, and those calls require a quota project. |
| Orchestrator identities | Functional orchestration requires OS Config, OS Config rollout, and Progressive Rollout service agents created and granted their documented roles at the orchestrator parent. Once that setup exists, the caller does not need child-project grants or `iam.serviceAccounts.actAs`. |
| Guest identity | The VM's attached service account signs OS Config requests without needing a workload IAM role. Code in the guest can request its credentials, but Google API access remains bounded by IAM and VM OAuth scopes. |
| Agent OS identity | The standard Linux service has no `User=` override, so systemd runs it as root. Google's Windows installer creates the service without alternate credentials, which uses LocalSystem. Custom service configuration can change this, so the book now says agent-identity execution with standard-image root/LocalSystem behavior. |

### Audit and runtime telemetry

- Stable v1 patch job/deployment writes are non-LRO Data Access `DATA_WRITE`; Data Access logs are off by default.
- Stable v1 OS policy create/update methods are Data Access `DATA_WRITE` LROs; Data Access logs are off by default. Explicit CLI examples use `--async` to avoid adding operation polling to the minimum permission path.
- v1beta legacy guest-policy create/update is non-LRO Data Access `DATA_WRITE`, off by default.
- Stable v2 project/folder/organization orchestrator create/update methods are Data Access `DATA_WRITE` LROs, off by default; the narrow orchestrator roles remain Beta.
- The official catalog explicitly excludes agent notification, task progress/completion, registration, inventory reporting, and legacy effective-policy lookup methods from Cloud Audit Logs.
- Absence of those Audit Logs does not make execution invisible. Patch/assignment/orchestrator resources, revisions, instance status/compliance, system logs, serial logs, configured `OSConfigAgent` Cloud Logging, source-object reads, and downstream service calls can remain.

### Retained techniques

1. Patch job or scheduled patch-deployment pre/post executable, contingent on a readable controlled artifact or controlled local executable.
2. GA zonal OS policy assignment with inline `exec` content.
3. Beta project-level legacy guest policy with an inline software-recipe script.
4. v2 policy orchestrator that fans the GA assignment into selected project-zone pairs after the documented service-agent/quota setup.

All four are direct privileged guest execution boundaries and clear the usefulness bar. The first three use distinct permissions, resource scopes, and payload contracts; the fourth crosses project boundaries through managed identities.

### Rejected or corrected claims

- **Any patch-job executor automatically has root RCE:** corrected. A Cloud Storage step needs a specific generation readable by the VM identity; a local step needs a pre-existing controlled path.
- **OS Config always executes as root/SYSTEM:** bounded to the actual installed service identity. Root/LocalSystem is the standard Google package behavior, not an immutable API guarantee for custom images.
- **One GA OS policy assignment reaches the whole project:** false. Assignments are zonal; multiple assignments or an orchestrator are needed across zones.
- **PolicyOrchestrator Admin alone always yields organization-wide execution:** false. Scope selectors, a quota project, APIs, three preconfigured parent service agents, child rollout success, active agents, and assignment filters are prerequisites.
- **Orchestrator include-project arguments accept `projects/NUMBER`:** false for the CLI. It expects comma-separated numeric project IDs.
- **Orchestrator child propagation and agent execution generate no telemetry:** false. Relevant Data Access logs are off by default and several agent RPCs are explicitly unaudited, but Cloud Logging/resource/compliance/guest/downstream evidence remains.
- **`osconfig.patchDeployments.execute` is a current force-run API:** unsupported by the current public v1 REST and GA CLI despite the permission remaining in predefined roles.
- **Inventory/vulnerability viewing is privilege escalation:** rejected as reconnaissance. It can improve target selection but does not cross an authorization boundary.
- **Project feature-setting update alone is root execution:** rejected. Enabling full VM Manager features still requires a separate patch/policy write permission and active target agents.
- **Generic OS Config service-agent role abuse belongs here as a direct OS Config primitive:** rejected. Misgranting service-agent roles is dangerous, but their generic `actAs`/Compute permissions require a separate downstream action and are covered better by IAM/Compute techniques.

### Related-page decision

The enum page was expanded because it had omitted legacy guest policies, assignment reports/revisions, project feature mode, orchestrators, quota/service-agent prerequisites, and the patch-artifact identity boundary. No separate post-exploitation or persistence page was created: inventory is enumeration, while recurring deployments/policies are secondary persistence properties of the retained direct execution primitives rather than additional distinct techniques.

### Independent review

An independent pass rechecked the current VM Manager audit catalog, setup and service-agent documentation, orchestrator prerequisites, current CLI help, and the Google-maintained agent service definitions. It confirmed the four permission boundaries and method names. The pass removed an unnecessary generic claim about the number of audit entries produced by an LRO; the catalog guarantees the method classification and LRO status, while exact emitted-entry behavior should be established from project logs rather than inferred.
