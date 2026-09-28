# Cloud Deploy privilege-escalation checklist

## Documentation-validated

- [x] Current execution-environment schema, default execution account, and legacy syntax distinction.
- [x] Release-time render-account `actAs` and rollout-time deploy-account `actAs` checks.
- [x] Pipeline predeploy task as arbitrary container command in the configured Cloud Build execution environment.
- [x] Existing-pipeline attacker source/image/manifest deployment and bounded runtime-identity impact.
- [x] Resource-level IAM on delivery pipelines, targets, custom target types, and deploy policies.
- [x] Raw API permissions versus current `gcloud apply` allow-missing PATCH behavior, LRO polling, release-helper reads, and local source staging.
- [x] Exact Cloud Deploy v1, generic IAM, Cloud Build, Cloud Storage, and downstream audit boundaries.
- [x] Required nested `task` hook schema and conditional CustomTargetType create/update path.
- [x] Current release helper reads, rollout read/list, operation polling, and staging bucket/object permissions.
- [x] Cloud Run deployer `actAs` and GKE RBAC/admission/Workload Identity downstream boundaries.
- [x] Condition-safe IAM helper and raw policy version-3/etag read-modify-write behavior.
- [x] Approval and deploy-policy override treated as conditional gates, not standalone escalation.
- [x] Rollback folded into deployment/persistence; automation removed from privilege escalation.

## Open research leads

- [ ] In a disposable authorized lab, capture the exact failed authorization resources when release render and rollout deploy use different service accounts and the caller has `actAs` on only one.
- [ ] Verify which credentials and metadata endpoints are exposed inside each current task type in default and private Cloud Build pools, without assuming all Cloud Build execution contexts expose identical token surfaces.
- [ ] Capture principal attribution and operation linkage across Cloud Deploy `CreateRelease`/`CreateRollout`, Cloud Build `CreateBuild`, and GKE or Cloud Run deployment audit entries.
- [ ] Test resource-level conditional IAM bindings for pipeline-scoped rollout creation, especially `clouddeploy.googleapis.com/rolloutTarget`, and document which helper reads are avoidable with raw requests.
- [ ] Check whether organization policies, Binary Authorization, Cloud Run deployment validation, or Kubernetes admission rules consistently block attacker image substitution before workload identity is reached.
