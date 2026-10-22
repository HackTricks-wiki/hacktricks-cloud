"""Privilege-escalation catalog loader and strict schema validator.

The registries in this module are the single source of truth for which target
kinds, selector keys, scopes, requirement fields and placeholders the evaluator
implements. The validator rejects anything the evaluator would not understand,
so an unknown selector key can never silently widen or narrow a target set.
"""
from __future__ import annotations

import functools
from collections import OrderedDict
from copy import deepcopy
import sys
from threading import RLock
import re
from pathlib import Path

import yaml

# LibYAML's safe constructor preserves the schema while avoiding the large
# temporary parser graphs of the Python implementation. Keep a safe fallback.
SAFE_YAML_LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


# Parsed documents are private; every consumer validates a fresh deep copy.
# The key includes exact freshly read contents and the selected safe parser.
# Path/mtime caches cannot safely establish catalog contents or provenance.
_PARSED_YAML_MAX_DOCUMENTS = 512
_PARSED_YAML_MAX_SOURCE_BYTES = 4 * 1024 * 1024
_PARSED_YAML_MAX_GRAPH_BYTES = 16 * 1024 * 1024
_PARSED_YAML_CACHE = OrderedDict()
_PARSED_YAML_SOURCE_BYTES = 0
_PARSED_YAML_GRAPH_BYTES = 0
_PARSED_YAML_LOCK = RLock()


def _graph_bytes(value):
    """Bound retained object graphs, including aliases/cycles, once per miss."""
    seen = set()
    def visit(item):
        identity = id(item)
        if identity in seen:
            return 0
        seen.add(identity)
        total = sys.getsizeof(item)
        if isinstance(item, dict):
            total += sum(visit(k) + visit(v) for k, v in item.items())
        elif isinstance(item, (list, tuple, set, frozenset)):
            total += sum(visit(v) for v in item)
        return total
    return visit(value)


def _clear_parsed_yaml_cache():
    global _PARSED_YAML_SOURCE_BYTES, _PARSED_YAML_GRAPH_BYTES
    with _PARSED_YAML_LOCK:
        _PARSED_YAML_CACHE.clear()
        _PARSED_YAML_SOURCE_BYTES = _PARSED_YAML_GRAPH_BYTES = 0


def _parsed_yaml_cache_info():
    with _PARSED_YAML_LOCK:
        return {"documents": len(_PARSED_YAML_CACHE),
                "source_bytes": _PARSED_YAML_SOURCE_BYTES,
                "graph_bytes": _PARSED_YAML_GRAPH_BYTES}


def _catalog_document(text):
    """Return caller-owned data and an optional uncommitted parsed candidate.

    Invalid YAML is never cached. The loader commits a candidate only after
    its complete per-file schema validation succeeds. Independent strict
    loading and versioned catalog verification remain unchanged.
    """
    key = (SAFE_YAML_LOADER, text)
    with _PARSED_YAML_LOCK:
        cached = _PARSED_YAML_CACHE.get(key)
        if cached is not None:
            _PARSED_YAML_CACHE.move_to_end(key)
    if cached is not None:
        return deepcopy(cached[0]), None
    parsed = yaml.load(text, Loader=SAFE_YAML_LOADER)
    return deepcopy(parsed), (key, parsed)


def _remember_catalog_document(candidate):
    global _PARSED_YAML_SOURCE_BYTES, _PARSED_YAML_GRAPH_BYTES
    if candidate is None:
        return
    key, parsed = candidate
    source_bytes = len(key[1].encode("utf-8"))
    if source_bytes > _PARSED_YAML_MAX_SOURCE_BYTES:
        return
    graph_bytes = _graph_bytes(parsed)
    if graph_bytes > _PARSED_YAML_MAX_GRAPH_BYTES:
        return
    with _PARSED_YAML_LOCK:
        if key in _PARSED_YAML_CACHE:
            _PARSED_YAML_CACHE.move_to_end(key)
            return
        while _PARSED_YAML_CACHE and (
                len(_PARSED_YAML_CACHE) >= _PARSED_YAML_MAX_DOCUMENTS or
                _PARSED_YAML_SOURCE_BYTES + source_bytes > _PARSED_YAML_MAX_SOURCE_BYTES or
                _PARSED_YAML_GRAPH_BYTES + graph_bytes > _PARSED_YAML_MAX_GRAPH_BYTES):
            _, (_, old_source, old_graph) = _PARSED_YAML_CACHE.popitem(last=False)
            _PARSED_YAML_SOURCE_BYTES -= old_source
            _PARSED_YAML_GRAPH_BYTES -= old_graph
        if _PARSED_YAML_MAX_DOCUMENTS < 1:
            return
        _PARSED_YAML_CACHE[key] = (parsed, source_bytes, graph_bytes)
        _PARSED_YAML_SOURCE_BYTES += source_bytes
        _PARSED_YAML_GRAPH_BYTES += graph_bytes


PROVIDERS = ("aws", "gcp", "azure", "k8s")
CATALOG_DIR = Path(__file__).resolve().parent / "catalog"
HACKTRICKS_CLOUD = Path("/Users/carlospolop/git/hacktricks-cloud")

# kind -> (provider, node class). "principal" kinds are real identities that can
# act as sources; "entity" kinds are collapsed control objects (account admin,
# scope owner, cluster-admin, a directory role) that are terminal privileges.
TARGET_KINDS = {
    "aws_role": ("aws", "principal"),
    "aws_user": ("aws", "principal"),
    "aws_group": ("aws", "principal"),
    "aws_identity_center_user": ("aws", "principal"),
    "aws_identity_center_permission_set": ("aws", "entity"),
    "aws_account_admin": ("aws", "entity"),
    "aws_directory_domain_admin": ("aws", "entity"),
    "aws_service_plane_admin": ("aws", "entity"),
    "aws_verified_authority": ("aws", "entity"),
    "aws_challenge_foothold": ("aws", "principal"),
    "gcp_service_account": ("gcp", "principal"),
    "gcp_user": ("gcp", "principal"),
    "gcp_group": ("gcp", "principal"),
    "gcp_workspace_user": ("gcp", "principal"),
    "gcp_external_principal": ("gcp", "principal"),
    "gcp_scope_owner": ("gcp", "entity"),
    "gcp_verified_authority": ("gcp", "entity"),
    "gcp_challenge_foothold": ("gcp", "principal"),
    "azure_managed_identity": ("azure", "principal"),
    "azure_service_principal": ("azure", "principal"),
    "azure_user": ("azure", "principal"),
    "azure_external_principal": ("azure", "principal"),
    "azure_storage_local_user": ("azure", "principal"),
    "azure_challenge_foothold": ("azure", "principal"),
    "azure_verified_authority": ("azure", "entity"),
    "azure_scope_owner": ("azure", "entity"),
    "azure_dataplane_admin": ("azure", "entity"),
    "entra_role": ("azure", "entity"),
    "entra_group": ("azure", "principal"),
    "k8s_service_account": ("k8s", "principal"),
    "k8s_user": ("k8s", "principal"),
    "k8s_group": ("k8s", "principal"),
    "k8s_node": ("k8s", "principal"),
    "k8s_cluster_admin": ("k8s", "entity"),
    "k8s_verified_authority": ("k8s", "entity"),
    "k8s_admission_control": ("k8s", "entity"),
    "k8s_remote_cluster": ("k8s", "principal"),
    "cloud_identity": ("k8s", "principal"),
}
# aws_service_plane_admin: administrator of a managed service's own application plane (Amazon Connect instance,
# Managed Grafana workspace, QuickSight account, Supply Chain instance, Amplify Studio backend). Not an IAM principal
# and never AWS-admin-equivalent. Values of selector service_plane (IAM service prefixes):
SERVICE_PLANES = ("amplifybackend", "connect", "grafana", "quicksight", "scn")
# k8s_admission_control: one entity per cluster meaning "admission enforcement can be lifted"; the entry names the
# lifted blockers in target.removes_blockers. k8s_remote_cluster: a credential to ANOTHER cluster held in a Secret.
# Kinds that more than one provider's catalog may target (AKS cluster-admin from Azure RBAC, ...).
EXTRA_KIND_PROVIDERS = {"k8s_cluster_admin": ("azure", "gcp", "aws"),
                        "k8s_service_account": ("gcp", "azure")}
ADMIN_KINDS = ("aws_account_admin", "gcp_scope_owner", "azure_scope_owner", "k8s_cluster_admin", "entra_role")


def kind_allowed(kind, provider):
    return kind in TARGET_KINDS and (TARGET_KINDS[kind][0] == provider or provider in EXTRA_KIND_PROVIDERS.get(kind, ()))


# selector key -> (providers, value kind, description). Value kinds: bool_true,
# bool, string, string_or_list, namespace, action, any.
SELECTOR_KEYS = {
    # ---- generic ---------------------------------------------------------
    "azure_storage_local_credential": (("azure",), "string", "Azure Storage SFTP local user credential; reset_password, write_credential, or create_credential. Requires exact account settings and verified container rights."),
    "azure_challenge_fact": (("azure",), "string", "Exact reviewed Azure technique/source/target/scope evidence; never a definite path."),
    "azure_external_principal_evidence": (("azure",), "bool_true", "Unique complete reviewed evidence binds a declared ARM action to one named adjacent-plane principal, usable credential or grant, prior denial, and a newly allowed target action."),
    "azure_external_plane": (("azure",), "string", "Exact adjacent authorization plane of a reviewed Azure external-principal gain."),
    "k8s_challenge_fact": (("k8s",), "string", "Exact reviewed Kubernetes technique/source/target/scope evidence."),
    "k8s_helm_values_rbac": (("k8s",), "bool_true", "Reviewed exact ConfigMap-to-Helm-to-RoleBinding permission grant for the lab documented by the source."),
    "k8s_verified_pivot": (("k8s",), "string", "Unique fresh reviewed evidence binds the exact source action and object to one accepted remote principal or newly granted Kubernetes permission."),
    "k8s_bound_role_gain": (("k8s",), "bool_true", "Collected Role rules contain a concrete permission the source lacks; the source can bind that exact Role in the target namespace."),
    "k8s_existing_rolebinding_gain": (("k8s",), "bool_true", "An existing RoleBinding targets the exact Role, the source can modify that binding and bind the Role, and the Role grants a new permission."),
    "k8s_clusterrolebinding_gain": (("k8s",), "bool_true", "A collected ClusterRole grants a new cluster-wide permission and the source can bind that exact role."),
    "k8s_existing_clusterrolebinding_gain": (("k8s",), "bool_true", "An existing ClusterRoleBinding targets the exact ClusterRole and the source can modify that binding to gain a new cluster-wide permission."),
    "k8s_aggregated_rolebinding_namespace": (("k8s",), "bool_true", "The source is bound in the target namespace to a ClusterRole whose aggregationRule selects new ClusterRoles."),
    "attached_to_service": (("aws", "gcp", "azure"), "string_or_list",
        "Identity is attached to a collected resource of that service (Lambda Role, EC2 instance profile, "
        "GCE/GKE service account, Azure resource identity incl. full ARM types). Uncollected attachment "
        "inventories fall back to trust/all identities with unknown confidence."),
    "same_as_source": (("aws", "gcp", "azure", "k8s"), "bool_true",
        "Target is the source itself (self-escalation); for entity kinds the source's own scope."),
    "resource_permission_covers_target": (("aws", "gcp", "azure", "k8s"), "action",
        "The source must also hold this action on the target resource ({target.arn}/{target.email}/{target.scope}/{target.namespace})."),
    "any_principal_in_scope": (("gcp", "azure", "k8s", "aws"), "bool_true",
        "Entity target covering every principal of the scope where the requirement holds (scope owner / cluster-admin / account admin)."),
    "azure_root_scope_only": (("azure",), "bool_true",
        "Restrict an Azure root-scope authorization target to the tenant root (/)."),
    # ---- AWS -------------------------------------------------------------
    "aws_challenge_fact": (("aws",), "string",
        "Exact externally verified technique/source/target evidence from aws_privesc_challenge_evidence. "
        "Missing or incomplete evidence is unresolved; a different source or target never matches."),
    "aws_s3_policy_self_grant": (("aws",), "bool_true", "Reviewed exact S3 bucket-policy self-grant for the caller and a bounded object prefix."),
    "aws_sqs_policy_self_grant": (("aws",), "bool_true", "Same-account IAM user can grant itself ReceiveMessage on an exact unencrypted queue through SetQueueAttributes."),
    "aws_sns_policy_self_grant": (("aws",), "bool_true", "Same-account IAM user can grant itself Subscribe on an exact topic through SetTopicAttributes."),
    "aws_dynamodb_policy_self_grant": (("aws",), "bool_true", "Same-account IAM user can grant itself GetItem on an exact AWS-owned-key table through PutResourcePolicy."),
    "aws_s3_access_grants_self_grant": (("aws",), "bool_true", "Reviewed exact S3 Access Grants session with new READ permission on a bounded prefix."),
    "aws_secretsmanager_policy_self_grant": (("aws",), "bool_true", "Reviewed GetSecretValue self-grant for the exact IAM user and secret."),
    "aws_efs_policy_self_grant": (("aws",), "bool_true", "Reviewed ClientMount self-grant for the exact EFS file system."),
    "aws_cases_tag_self_grant": (("aws",), "bool_true", "Reviewed Cases domain tag change unlocking PutCaseEventConfiguration for the source."),
    "aws_sitewise_portal_self_grant": (("aws",), "bool_true", "Reviewed SiteWise Monitor portal ADMINISTRATOR grant to the source identity."),
    "trust_allows_service": (("aws",), "string_or_list",
        "Role trust policy has an Allow for sts:AssumeRole* whose Principal.Service includes the value."),
    "trust_allows_principal_of_source": (("aws",), "bool_true",
        "Role trust policy allows the source principal ARN, the source account (root/ID) or '*'."),
    "trust_allows_federated": (("aws",), "string_or_list",
        "Role trust policy allows Principal.Federated equal to the value (e.g. cognito-identity.amazonaws.com)."),
    "trust_allows_saml_provider_covered_by": (("aws",), "action",
        "Role trusts a SAML provider ({target.saml_provider_arn}) on which the source holds the action."),
    "has_instance_profile": (("aws",), "bool",
        "Role is in at least one instance profile (InstanceProfileList)."),
    "has_login_profile": (("aws",), "bool",
        "IAM user has (true) / lacks (false) a console password (LoginProfile detail)."),
    "name_prefix": (("aws",), "string",
        "Role name (and instance-profile name) starts with the value."),
    "source_kind": (("aws",), "string_or_list",
        "Technique only applies when the source principal is of this kind."),
    "source_group_covered_by": (("aws",), "action",
        "Source is a member of an IAM group ({source.group_arn}) on which it holds the action."),
    "source_attached_policy_covered_by": (("aws",), "action",
        "A customer-managed policy attached to the source ({source.attached_policy_arn}) is covered by the action."),
    "via_assumable_role_covered_by": (("aws",), "action",
        "The source can assume a role on which it also holds the action (two-step self-escalation)."),
    "via_assumable_role_attached_policy_covered_by": (("aws",), "action",
        "An assumable same-account role becomes admin after the source creates a default version of an attached customer policy."),
    "via_resource_type": (("aws",), "string_or_list",
        "Target role is attached to an existing resource of that type ({target.resource_arn}); lambda_function, "
        "ec2_instance, codebuild_project, glue_job, redshift_cluster, rds_db_instance, sagemaker_notebook_instance and "
        "redshift_serverless_workgroup are collected, other types are unknown when the role trusts the type's service "
        "(imagebuilder_pipeline: ec2.amazonaws.com)."),
    "via_artifact_type": (("aws",), "string_or_list",
        "Target role's workload consumes an artifact ({target.artifact_arn}) of that type; artifact consumers are not collected (unknown)."),
    "attached_resource_covered_by": (("aws",), "action",
        "The resource carrying the target role ({target.attached_resource_arn}) is covered by the action."),
    "consumer_input_writable_via": (("aws",), "action",
        "The source can write an input ({target.consumer_input_arn}) consumed by the target workload with the action."),
    "cognito_user_pool_covered_by": (("aws",), "action",
        "Target role is mapped by an identity pool to a user pool covered by the action; dropped when the account's "
        "cognito_user_pool inventory is collected and empty, otherwise unknown (identity-pool roles not collected)."),
    "cognito_developer_authenticated_role": (("aws",), "bool_true",
        "Target role is the authenticated role of an identity pool with a developer provider, with trust admitting "
        "that pool's authenticated Cognito web identity."),
    "cognito_developer_classic_role": (("aws",), "bool_true",
        "Target role trusts the authenticated web identity of a developer identity pool whose Basic (Classic) "
        "flow is enabled, whether or not it is the pool's default role."),
    "cognito_developer_settable_authenticated_role": (("aws",), "bool_true",
        "Target role can become the authenticated role of a collected developer identity pool and trusts that "
        "pool's authenticated web identity; the source must be able to mint a developer token for the same pool."),
    "cognito_developer_enable_classic_role": (("aws",), "bool_true",
        "Target role trusts a developer identity pool whose Basic (Classic) flow is disabled; the source can enable "
        "that flow and mint a developer token for the same pool."),
    "cognito_user_pool_group_role_covered_by": (("aws",), "action",
        "Target role is the RoleArn of a user-pool group covered by the action; dropped when the account's "
        "cognito_user_pool inventory is collected and empty, otherwise unknown (groups not collected)."),
    "codedeploy_group_instance_role_covered_by": (("aws",), "action",
        "Target role is the instance role of a CodeDeploy deployment group covered by the action (not collected)."),
    "ecs_task_role_on_ec2_capacity": (("aws",), "bool_true",
        "Target role is the taskRoleArn of an EC2/EXTERNAL-capable task definition (or of a running EC2 task) in an account "
        "whose ECS clusters have registered container instances; dropped when no such definition exists or every cluster "
        "has 0 container instances, conditional without task placement, unknown without task-definition inventory."),
    "ecs_container_instance_role_in_cluster_covered_by": (("aws",), "action",
        "Target role is the instance role of an ECS container instance or the task role of a task placed on one "
        "(dropped when every cluster has 0 container instances; unknown without container-instance/task inventory)."),
    "ecs_task_colocated_with_source_container_instance": (("aws",), "string",
        "Value {source.arn}: the source is an EC2 container-instance role and the target task or task-execution role "
        "runs (or, without placement facts, may run: unknown) on an EC2 container instance carrying the source's instance profile."),
    "eks_authentication_mode": (("aws",), "string_or_list",
        "EKS cluster accessConfig.authenticationMode is one of the values (API, API_AND_CONFIG_MAP, CONFIG_MAP); unknown when not collected."),
    "trust_allows_oidc_provider_covered_by": (("aws",), "action",
        "Role trusts an IAM OIDC provider ({target.oidc_provider_arn}); the entry's requirements on that ARN carry the action."),
    "trust_federated_provider_missing": (("aws",), "string_or_list",
        "Role trusts a SAML ('saml') or OIDC ('oidc') provider ARN of its own account that does not exist "
        "(iam_saml_provider / iam_oidc_provider inventory; unknown when not collected)."),
    "trust_allows_principal_org": (("aws",), "bool_true",
        "Role trust allows Principal '*' restricted by aws:PrincipalOrgID / aws:PrincipalOrgPaths, satisfied by an account "
        "of the snapshot's organization (unknown without the organization id)."),
    "org_member_account": (("aws",), "bool_true",
        "Target belongs to an operational organization member account (not the management account); unknown without organization_account."),
    "emr_runtime_role_of_cluster": (("aws",), "bool_true",
        "Role trust names an EC2 instance-profile role used by an EMR cluster with a security configuration "
        "(runtime roles); unknown without emr_cluster inventory."),
    "trust_allows_emr_containers_oidc": (("aws",), "bool_true",
        "Role trusts an EKS OIDC provider with a sub condition on emr-containers-sa-* service accounts (EMR on EKS execution role)."),
    "instance_profile_name_prefix_or_path": (("aws",), "string_or_list",
        "One of the role's instance profiles has a name starting with the value, or (values starting with '/') a path containing it."),
    "portfolio_of_target_product_covered_by": (("aws",), "action",
        "Target role is the launch-constraint role of a Service Catalog product in a portfolio ({target.portfolio_arn}); "
        "unknown without servicecatalog_portfolio inventory."),
    "assigned_to_identity_center_group": (("aws",), "bool_true",
        "Permission set / user is reachable through an Identity Center group assignment (not collected)."),
    "rolesanywhere_profile_includes_target": (("aws",), "bool_true",
        "Target role is listed in an IAM Roles Anywhere profile ({target.rolesanywhere_profile_arn}, accepting "
        "{target.trust_anchor_arn}); dropped when the account's rolesanywhere_trust_anchor inventory is collected and "
        "empty, otherwise unknown (profiles not collected)."),
    # ---- GCP -------------------------------------------------------------
    "gcp_challenge_fact": (("gcp",), "string",
        "Exact reviewed technique/source/target/scope evidence from gcp_privesc_challenge_evidence. "
        "Only verified preconditions produce a conditional path; missing or incomplete evidence is unresolved."),
    "gcp_resource_self_grant": (("gcp",), "bool_true",
        "A reviewed accepted self-grant or a modeled exact-resource policy write that adds a new permission; prospective resources include Secret Manager secrets, Cloud KMS keys, Pub/Sub topics and subscriptions, standard Artifact Registry repositories, and Analytics Hub exchanges and listings."),
    "gcp_external_principal_evidence": (("gcp",), "bool_true",
        "Unique complete reviewed evidence binds a declared action to one named external-plane principal, usable credential, and a newly allowed target action."),
    "gcp_agentregistry_skill_evidence": (("gcp",), "bool_true",
        "Unique reviewed evidence ties a changed Agent Registry Skill to one floating consumer, runtime identity, and newly successful bounded action."),
    "gcp_external_plane": (("gcp",), "string",
        "Exact external authorization plane named by the reviewed principal-gain record."),
    "gcp_bounded_access_gain": (("gcp",), "bool_true",
        "Unique reviewed evidence proves a newly allowed bounded action through one created or authorized intermediate resource."),
    "gcp_bounded_mechanism": (("gcp",), "string",
        "Exact indirect-access mechanism in the bounded-access evidence record."),
    "gcp_clouddeploy_custom_render_path": (("gcp",), "bool_true",
        "A collected pipeline stage, custom target, custom target type, and render service account are joined to exact update and release-create grants."),
    "gcp_clouddeploy_existing_custom_render_path": (("gcp",), "bool_true",
        "A collected pipeline stage and custom target render account are joined to release creation on the exact pipeline."),
    "gcp_clouddeploy_pipeline_policy_custom_render_path": (("gcp",), "bool_true",
        "A collected custom target render account is joined to setIamPolicy on its exact delivery pipeline."),
    "gcp_clouddeploy_configurable_custom_render_path": (("gcp",), "bool_true",
        "Source can create or update an exact custom target and pipeline route, then create its release with the selected render account."),
    "gcp_cloudbuild_writable_trigger_token_path": (("gcp",), "bool_true",
        "An exact repository token grant is joined to an enabled push trigger whose repository build config and service account are recorded."),
    "gcp_cloudbuild_writable_trigger_policy_path": (("gcp",), "bool_true",
        "An exact connection policy grant can self-grant repository token access for an enabled push trigger with a recorded build identity."),
    "gcp_workflows_update_execute_same_workflow": (("gcp",), "bool_true",
        "Source can update and execute the same active workflow attached to the target service account."),
    "gcp_workflows_update_attach_path": (("gcp",), "bool_true",
        "Source can update and execute an existing active workflow in the target service account's project."),
    "gcp_workflows_observed_external_execution": (("gcp",), "bool_true",
        "An enabled Scheduler job is recorded to execute an exact workflow the source can update; other possible triggers remain unresolved."),
    "gcp_cloudscheduler_update_job_path": (("gcp",), "bool_true",
        "Source can update an enabled scheduler job, or update and resume a paused job, in the target service account's project."),
    "gcp_cloudscheduler_authenticated_delivery": (("gcp",), "bool_true",
        "The project's Cloud Scheduler service agent has its required role for authenticated job delivery."),
    "gcp_cloudtasks_enqueue_path": (("gcp",), "bool_true",
        "Source can create a task in a running queue, resume a paused queue, or create a new queue and task in the target account's project."),
    "gcp_cloudtasks_authenticated_delivery": (("gcp",), "bool_true",
        "The Cloud Tasks service agent has its project role and access to the exact target service account."),
    "gcp_cloudtasks_queue_policy_path": (("gcp",), "bool_true",
        "Source can add task creation on an exact queue it does not already control, remove a target override when permitted, and dispatch from a running or resumable queue."),
    "gcp_cloudfunctions_create_path": (("gcp",), "bool_true",
        "Source can create a function with uploaded source and a known build account it can use, and can invoke it."),
    "gcp_cloudfunctions_existing_source_update_path": (("gcp",), "bool_true",
        "Source can update the source of an active function, act as its build identity, and reach an observed invocation route."),
    "gcp_cloudfunctions_env_startup_path": (("gcp",), "bool_true",
        "Source can update an active Node.js 20 or later function, use its build identity, and reach an execution route."),
    "gcp_cloudfunctions_source_deploy_build_path": (("gcp",), "bool_true",
        "Source can create or update a function built as an observed legacy Cloud Build default identity and can act as the function runtime identity."),
    "gcp_vertex_new_model_endpoint_path": (("gcp",), "bool_true",
        "Source can upload a custom model, create an endpoint, deploy it, and use a target service account delegated to the Vertex AI service agent."),
    "gcp_vertex_batch_prediction_path": (("gcp",), "bool_true",
        "Source can create a batch prediction job with an inline container and use a target service account delegated to the Vertex AI service agent."),
    "gcp_workbench_existing_takeover_path": (("gcp",), "bool_true",
        "Source can update and boot the same existing Workbench instance or self-grant its instance administration rights."),
    "gcp_run_job_override_path": (("gcp",), "bool_true",
        "Source can run a collected Cloud Run job and override that same job's execution under its pinned service account."),
    "gcp_run_job_policy_override_path": (("gcp",), "bool_true",
        "Source can set the IAM policy of a collected Cloud Run job pinned to the target service account."),
    "gcp_run_service_update_path": (("gcp",), "bool_true",
        "Source can update an exact collected Cloud Run service in the target service account's project."),
    "gcp_run_job_update_execute_path": (("gcp",), "bool_true",
        "Source can update and run the same collected Cloud Run job in the target service account's project."),
    "gcp_run_instance_create_or_update_path": (("gcp",), "bool_true",
        "Source can create a Cloud Run instance in the target project or update an exact existing instance there."),
    "gcp_run_instance_ssh_path": (("gcp",), "bool_true",
        "Source has SSH permission on an attached Cloud Run instance that is running or can be started."),
    "gcp_run_service_ssh_path": (("gcp",), "bool_true",
        "Source has SSH permission on an attached, ready second-generation Cloud Run service with SSH enabled."),
    "gcp_appengine_instance_ssh_path": (("gcp",), "bool_true",
        "Exact flexible App Engine instance, backing VM, runtime identity, login method and SSH route."),
    "gcp_appengine_deploy_path": (("gcp",), "bool_true",
        "Existing App Engine application, source staging bucket, and target runtime service-account repository access."),
    "gcp_appengine_legacy_actas_unenforced": (("gcp",), "bool_true",
        "Visible legacy App Engine actAs constraint with effective enforcement disabled for the target project."),
    "gcp_appintegration_run_as_path": (("gcp",), "bool_true",
        "Enabled Application Integration service, one observed integration, same-integration invocation or publication rights, and actAs on the selected service account."),
    "gcp_gcr_namespace_path": (("gcp",), "bool_true",
        "Fully redirected gcr.io host with a missing matching repository, create and upload rights there, and an exact tagged workload consumer identity."),
    "gcp_artifact_policy_consumer_path": (("gcp",), "bool_true",
        "Exact standard Docker repository, tagged Cloud Run consumer and runtime account, plus repository policy-write authority."),
    "gcp_agentidentity_retrieve_path": (("gcp",), "bool_true",
        "Exact enabled Google OAuth provider and active authorization with useful granted scopes."),
    "gcp_agentidentity_update_path": (("gcp",), "bool_true",
        "Exact enabled Google OAuth provider and active authorization whose later refresh could reach a changed token endpoint."),
    "gcp_batch_agent_reporter_on_target": (("gcp",), "bool_true",
        "The target service account holds batch.states.report in its Batch job project."),
    "gcp_run_worker_pool_create_or_update_path": (("gcp",), "bool_true",
        "Source can create a worker pool in the target project or update an exact existing worker pool there."),
    "gcp_actas_granted_on_target": (("gcp",), "bool_true",
        "Source holds iam.serviceAccounts.actAs on the target SA (SA policy or project/folder/org inheritance)."),
    "gcp_sa_in_scope_of_permission": (("gcp",), "bool_true",
        "Requirements with resource '*' must hold on the target SA's project (or the SA / an ancestor)."),
    "gcp_hmac_storage_identity": (("gcp",), "bool_true",
        "Each enabled inventoried service account becomes a separate Cloud Storage-only HMAC authority target."),
    "gcp_bounded_service_execution": (("gcp",), "string",
        "An enabled service account becomes a separate bounded service authority target for the named mechanism."),
    "gcp_wif_restorable_path": (("gcp",), "bool_true",
        "An exact disabled or deleted workload pool or provider is joined to a pool-wide service-account token binding and the source's restore action."),
    "gcp_wif_active_path": (("gcp",), "string",
        "An exact active workload pool or provider is joined to a pool-wide service-account token binding and the source's control action."),
    "gcp_workforce_control_path": (("gcp",), "bool_true",
        "An exact workforce pool or provider control action is joined to an organization-local pool-wide service-account token binding."),
    "gcp_bounded_workspace_oauth": (("gcp",), "string",
        "A named Workspace user becomes a scope-limited OAuth authority target for the named mechanism."),
    "gcp_cross_project_run_service": (("gcp",), "bool_true",
        "A Cloud Run service can be created in a different collected project with the target SA only when the "
        "target project's effective cross-project org policy permits it and its service agent has token access."),
    "gcp_cross_project_run_job": (("gcp",), "bool_true",
        "A Cloud Run job can be created and run in a different collected project with the target SA only when the "
        "target project's effective cross-project org policy permits it and its service agent has token access."),
    "gcp_cross_project_cloudbuild": (("gcp",), "bool_true",
        "A build in another collected project can use the target SA only when the effective cross-project policy "
        "permits it and that project's Cloud Build service agent has token access."),
    "gcp_cross_project_workflows": (("gcp",), "bool_true",
        "A workflow in another collected project can use the target SA only when the effective cross-project policy "
        "permits it and that project's Workflows service agent has token access."),
    "gcp_implicit_delegation_chain": (("gcp",), "bool_true",
        "Target SA is one a delegate chain can mint credentials for: the source holds iam.serviceAccounts.implicitDelegation "
        "on delegate D1, each Di holds implicitDelegation on Di+1 (transitively), and some Dk holds getAccessToken, signBlob "
        "or signJwt on the target. Delegates are not targets themselves (implicitDelegation does not yield their own token)."),
    "gcp_custom_role_bound_to_source": (("gcp",), "bool_true",
        "Target is the exact scope where the source has a binding to a collected custom role, and the source can update that exact role."),
    "gcp_actas_granted_to_service_agent": (("gcp",), "string",
        "Target SA is one on which the named Google service agent (cloudservices = Google APIs service agent "
        "<project-number>@cloudservices.gserviceaccount.com, used by managed instance groups) holds iam.serviceAccounts.actAs "
        "(SA policy or project/folder/org inheritance; Editor by default). Unknown when no binding of that agent is collected."),
    "gcp_pam_entitlement_requester": (("gcp",), "bool_true",
        "Target scope has a Privileged Access Manager entitlement whose eligible requesters include the source (directly or "
        "through a group) and whose roles give IAM control of the scope. PAM entitlements are not collected (not evaluated)."),
    # ---- Azure RBAC ------------------------------------------------------
    "azure_identity_assignable_in_scope": (("azure",), "bool_true",
        "Requirements with scope '*' must hold on a scope that contains the identity's attached resource "
        "(or the user-assigned identity resource)."),
    "azure_automation_assignable_uami": (("azure",), "bool_true",
        "The source can assign the exact user-assigned identity to an inventoried Automation account or create one in an inventoried group, then create or edit and run a runbook there."),
    "azure_automation_runbook_identity_path": (("azure",), "bool_true",
        "The source can create or edit and run a runbook on the exact Automation account carrying this managed identity."),
    "azure_automation_hybrid_worker_path": (("azure",), "bool_true",
        "The source can create or edit and run a runbook on the Automation account with an inventoried Hybrid Worker VM carrying this identity."),
    "azure_batch_job_pool_identity": (("azure",), "bool_true",
        "The source can create a Batch job or schedule on the exact Entra-enabled account with a runnable native pool carrying this user-assigned identity."),
    "azure_batch_shared_key_pool_identity": (("azure",), "bool_true",
        "The source can obtain a Shared Key from the exact Batch account with a native pool carrying this verified user-assigned identity."),
    "azure_batch_pool_starttask_identity": (("azure",), "bool_true",
        "The source can write the exact native Batch pool that carries this verified user-assigned identity."),
    "azure_batch_pool_assignable_uami": (("azure",), "bool_true",
        "The source can write an exact existing Batch pool or a new pool under an inventoried account and can assign the target user-assigned identity."),
    "azure_containerapp_assignable_uami": (("azure",), "bool_true",
        "The source can write an exact inventoried Container App, attach the target user-assigned identity, and run a controlled revision."),
    "azure_containerapp_create_uami_path": (("azure",), "bool_true",
        "The source can create an app under an inventoried resource group and join an existing or creatable managed environment in the same subscription."),
    "azure_containerapp_exec_identity": (("azure",), "bool_true",
        "The source can obtain a console token and execute or debug on the same Container App with a running revision whose current identity is available to its main container."),
    "azure_containerapp_job_assignable_uami": (("azure",), "bool_true",
        "The source can assign the verified user-assigned identity to an exact writable job in a usable managed environment, or create a scheduled job in an inventoried group and joinable environment."),
    "azure_confidential_ledger_admin_path": (("azure",), "bool_true",
        "The source has an Entra principal and the target is an inventoried usable Confidential Ledger whose ARM principal list can be updated."),
    "azure_appservice_assignable_uami": (("azure",), "bool_true",
        "The source can assign the exact inventoried user-assigned identity to an existing app it can write and control code in, or create an app in an inventoried resource group using a joinable plan."),
    "azure_appservice_backup_restore_code_path": (("azure",), "bool_true",
        "The source can restore a backup on the exact supported-tier App Service carrying the target identity; backup compatibility and code execution remain conditional."),
    "azure_appservice_config_code_path": (("azure",), "bool_true",
        "The target identity is attached to the exact app whose web or app-settings config child the source can write; the app's runtime must support a code-bearing configuration path."),
    "azure_appservice_enable_publishing_credentials_code_path": (("azure",), "bool_true",
        "The source can enable the exact app's SCM basic auth policy and read its publishing credentials; the app carries the target identity and can run deployed code."),
    "azure_appservice_kudu_code_path": (("azure",), "bool_true",
        "The target identity is attached to the exact App Service for which the source holds publish/action, with a supported Kudu hosting plan and an app that can run."),
    "azure_appservice_onedeploy_code_path": (("azure",), "bool_true",
        "The source can write the exact app's extensions/onedeploy child; the attached identity belongs to that app, and its runtime loads deployed packages."),
    "azure_appservice_publishing_credentials_code_path": (("azure",), "bool_true",
        "The source can read publishing credentials for the exact app carrying the target identity, SCM basic auth is enabled, and the runtime can load deployed code."),
    "azure_appservice_sitecontainers_code_path": (("azure",), "bool_true",
        "The source can write a SiteContainer child of the exact Linux app carrying the target identity, and that app uses SiteContainers mode."),
    "azure_appservice_siteextensions_code_path": (("azure",), "bool_true",
        "The source can install a site extension with a selectable package name on the exact Windows code app carrying the target identity."),
    "azure_appservice_slot_code_path": (("azure",), "bool_true",
        "The source has a code-bearing publish, source control, config, or SiteContainer route on the exact slot carrying the target identity."),
    "azure_appservice_slot_swap_code_path": (("azure",), "bool_true",
        "The source can stage code and swap the same inventoried slot into the exact production app carrying the target identity."),
    "azure_appservice_sourcecontrol_code_path": (("azure",), "bool_true",
        "The source can write the exact identity app's sourcecontrols/web child and that app can execute deployed repository code."),
    "azure_arc_entra_admin_ssh_path": (("azure",), "bool_true",
        "The source can read Arc relay credentials for the exact machine endpoint and log in as administrator through configured Entra SSH."),
    "azure_arc_custom_script_code_path": (("azure",), "bool_true",
        "The source can create or update a Custom Script child on the exact Arc identity machine while its connected agent permits that extension."),
    "azure_arc_run_command_code_path": (("azure",), "bool_true",
        "The source can create or update a Run Command child on the exact Arc identity machine while its connected agent permits the handler."),
    "azure_deployment_script_uami_path": (("azure",), "bool_true",
        "The source can create or update a deployment script with the exact assignable UAMI and can manage its required support resources."),
    "azure_appservice_slot_publishing_credentials_code_path": (("azure",), "bool_true",
        "The source can read publishing credentials for the exact slot carrying the target identity, and that slot's SCM basic auth policy allows credential use."),
    "azure_acr_assignable_uami": (("azure",), "bool_true",
        "The source can write a task on an inventoried ACR registry or existing task and assign an exact, verified user-assigned identity resource."),
    "azure_acr_existing_task_identity": (("azure",), "bool_true",
        "The exact inventoried ACR task carries the target managed identity and the source can write that task."),
    "azure_aks_rbac_group_impersonation": (("azure",), "bool_true",
        "The exact AKS cluster enables Azure RBAC for Kubernetes, and the source can authenticate to its Kubernetes API."),
    "azure_aks_rbac_cluster_binding": (("azure",), "bool_true",
        "The exact AKS cluster enables Azure RBAC for Kubernetes, and the source can authenticate to its Kubernetes API before creating a ClusterRoleBinding."),
    "azure_flux_cluster_path": (("azure",), "bool_true",
        "A writable Flux configuration belongs to the exact AKS or Arc cluster and has cluster scope."),
    "azure_vmss_instance_identity": (("azure",), "bool_true",
        "The selected scale-set VM instance belongs to a scale set carrying this managed identity."),
    "azure_aci_assignable_uami": (("azure",), "bool_true",
        "The source can assign the exact user-assigned identity and write an inventoried ACI container group or create one in an inventoried resource group; missing inventory stays unresolved."),
    "azure_aci_exec_running_identity": (("azure",), "bool_true",
        "The exact native ACI container group carries the target managed identity, has a running container, and the source can execute a command there."),
    "azure_aci_existing_write_identity": (("azure",), "bool_true",
        "The source can update an exact existing running ACI group that carries the target managed identity; terminated groups do not qualify."),
    "azure_apim_restorable_backup": (("azure",), "bool_true",
        "One fresh reviewed record binds a valid APIM-created backup, storage access, compatible restore target, controlled policy, and the exact attached identity."),
    "managed_identity_type": (("azure",), "string",
        "Managed identity is user_assigned or system_assigned."),
    "custom_role_assigned_to_source": (("azure",), "bool_true",
        "Target scope is one where a custom role assigned to the source applies (role definition rewrite)."),
    "credential_stored_in_scope": (("azure",), "string",
        "Principals whose secrets are stored in that resource/scope (always conditional; secret contents are never read)."),
    "azure_host_linked_to_pivot": (("azure",), "host_link",
        "Identity of a VM linked to the pivot resource: avd_session_host (application group -> hostPoolArmPath -> session "
        "hosts), automation_hybrid_worker (hybrid runbook workers' vmResourceId), devtest_lab_compute_vm (lab VM computeId), "
        "service_fabric_node_vmss (not collected: always unresolved). Linked VM identities are derived; the others are "
        "dropped when every link under {pivot} is collected, else unresolved."),
    "azure_deployer_of_pivot": (("azure",), "bool_true",
        "Identity that deploys the pivot resource (e.g. deployment script runner); not collected (unknown)."),
    "azure_site_kind": (("azure",), "string_or_list",
        "Microsoft.Web/sites kind contains the value (functionapp, app, ...)."),
    "ml_compute_assigned_to_source": (("azure",), "bool_true",
        "Azure ML compute instance assigned to the source (not collected, unknown)."),
    "azure_consumer_of_pivot": (("azure",), "consumer_binding",
        "Managed identity of a workload that reads the pivot resource (value = binding kind(s): "
        f"{', '.join(sorted(('key_vault_reference', 'storage_content', 'app_configuration_reference', 'queue_trigger', 'service_bus_trigger', 'event_subscription')))}). "
        "An identity holding the binding's read data action on a pivot resource is conditional "
        "(consumer_binding_not_collected); every other one is unresolved. Whether the consumer trusts the value enough "
        "to execute it is application logic: entries keep a condition for it."),
    "azure_assignable_via_identity_holding": (("azure",), "action",
        "User-assigned identity reached through an intermediate user-assigned identity T: the source holds "
        "Microsoft.ManagedIdentity/userAssignedIdentities/assign/action on T and T holds the named action on the target "
        "identity resource (e.g. an Image Builder template identity that assigns the build-VM identity). The edge takes "
        "the weaker of both grants and the condition via_intermediate_identity:<T>."),
    "azure_users_assigned_to_pivot": (("azure",), "bool_true",
        "azure_user targets holding Desktop Virtualization User (directly or through a group) on an AVD application "
        "group within {pivot}; always conditional (user_launches_app)."),
    "attached_to_vm_joined_to_entra_domain_services": (("azure",), "bool_true",
        "Managed identity attached to a VM joined to a Microsoft Entra Domain Services managed domain (JsonADDomainExtension "
        "naming the domainName of a Microsoft.AAD/domainServices resource): conditional (domain_join_state_not_verified); "
        "other VM identities unresolved (manual joins leave no ARM trace) unless no managed domain is inventoried."),
    "azure_assignment_condition_uses_principal_attribute": (("azure",), "bool_true",
        "azure_scope_owner / azure_dataplane_admin targets covered by a role assignment of the source (or its groups) whose "
        "ABAC condition reads @Principal custom security attributes (scope owner: the role grants roleAssignments/write at "
        "that scope; data-plane admin: the role has DataActions over the resource). Conditional "
        "(attribute_value_satisfying_condition_not_verified)."),
    "fabric_workspace_identity": (("azure",), "bool_true",
        "azure_service_principal targets that are the workspace identity of a Microsoft Fabric workspace; "
        "{target.host_resource} = that workspace (for fabric_workspace_role requirements)."),
    # ---- Entra ID --------------------------------------------------------
    "entra_role_assignable": (("azure",), "string_or_list",
        "Target is the named Entra directory role (display name, template ID, '*' or 'any')."),
    "entra_reset_matrix_column": (("azure",), "string",
        "Targets whose password the role column may reset per Microsoft's 'who can reset passwords' table, "
        "excluding role-assignable-group members and restricted-AU members."),
    "entra_role_assignment_scope_covers_target": (("azure",), "bool_true",
        "The directory role assignment's directoryScopeId ('/', AU or object) contains the target."),
    "entra_target_not_in_restricted_au": (("azure",), "bool_true",
        "Target is not a member of a restricted management administrative unit (AU facts needed)."),
    "entra_sp_has_tenant_application": (("azure",), "bool_true",
        "Service principal's appId belongs to an application registered in this tenant."),
    "entra_app_sign_in_audience": (("azure",), "string_or_list",
        "Application signInAudience equals the value."),
    "entra_sp_type_in": (("azure",), "string_or_list",
        "Service principal servicePrincipalType is one of the values."),
    "entra_source_is_owner_of_application": (("azure",), "bool_true", "Source owns the target's application object."),
    "entra_source_is_owner_of_service_principal": (("azure",), "bool_true", "Source owns the target service principal."),
    "entra_source_is_owner_of_group": (("azure",), "bool_true", "Source owns the target group."),
    "entra_custom_role_assigned_to_source": (("azure",), "bool_true",
        "Target is reached by editing a custom directory role already assigned to the source."),
    "entra_pim_eligible_for_source": (("azure",), "bool_true",
        "Source has a PIM eligibility schedule for the target role."),
    "entra_agent_blueprint_principal_or_child_identity": (("azure",), "bool_true",
        "Target is an agent identity blueprint principal or one of its child agent identities."),
    "entra_user_upn_on_federatable_custom_domain": (("azure",), "bool_true",
        "Target user's UPN is on a verified custom domain whose federation the source can change (domain facts needed)."),
    "entra_group_role_assignable": (("azure",), "bool",
        "Group isAssignableToRole equals the value."),
    "entra_group_membership_type": (("azure",), "string",
        "Group membership is 'assigned' or 'dynamic' (groupTypes contains DynamicMembership)."),
    "entra_group_membership_cloud_writable": (("azure",), "bool_true",
        "Synchronized or missing group source-of-authority facts keep a membership-write path conditional."),
    "entra_group_source_self_membership": (("azure",), "bool_true",
        "An application source needs Graph group-write and application-write permission to add its own service principal as a member."),
    "entra_group_type_covered_by_permission": (("azure",), "bool_true",
        "Group type (security / Microsoft 365) is covered by the entra_permission variant (groups.security / groups.unified)."),
    "entra_dynamic_rule_attributes_writable_by_source": (("azure",), "bool_true",
        "Dynamic membershipRule references user attributes the source can write (membershipRule needed)."),
    "entra_dynamic_rule_satisfiable_by_invited_guest": (("azure",), "bool_true",
        "Dynamic membershipRule can be satisfied by a guest the source can invite (membershipRule needed)."),
    "entra_pim_group_eligible_for_source": (("azure",), "pim_group_access",
        "entra_group targets for which the source (or one of its groups) has a PIM for Groups eligibility: true = member "
        "or owner, or 'member' / 'owner'. Always conditional (pim_activation_required)."),
    "entra_resource_in_catalog": (("azure",), "bool_true",
        "entra_group / azure_service_principal / entra_role targets that are resources of an entitlement-management "
        "catalog; {target.catalog} = those catalogs (for entra_catalog_role requirements)."),
    "entra_access_package_auto_assignment_open_to_guest": (("azure",), "bool_true",
        "Targets that are resources of an access package with an automatic-assignment policy whose rule does not exclude "
        "guests (userType -eq \"Member\"). Conditional (auto_assignment_rule_semantics_approximated)."),
    "intune_managed_device_user": (("azure",), "bool_true",
        "azure_user targets that are the primary user of an Intune-managed device. Conditional "
        "(device_session_not_verified): code run on the device reaches the user's session only while they sign in."),
    # ---- Kubernetes ------------------------------------------------------
    "k8s_sa_in_namespace": (("k8s",), "namespace",
        "Target service account namespace: '{source.namespace}', '{target.namespace}', '*', or a literal namespace."),
    "k8s_node_hosting_pods_with_sa": (("k8s",), "bool_true",
        "Service account is mounted by a scheduled pod (k8s_service_account) or node hosts pods (k8s_node); "
        "with a k8s_node source, the SAs of pods scheduled on that node."),
    "k8s_sa_used_by_running_pod": (("k8s", "gcp"), "bool_true", "Service account is used by a running pod with an available token."),
    "k8s_sa_used_by_controller_managed_pod": (("k8s",), "bool_true",
        "Service account is used by a pod owned by a controller (ownerReferences)."),
    "k8s_node_schedulable": (("k8s",), "bool_true",
        "Node can be targeted by direct pod placement with spec.nodeName even when cordoned; unconfirmed readiness is conditional."),
    "k8s_node_hosting_pods_in_namespace": (("k8s",), "namespace", "Node hosts pods of that namespace."),
    "k8s_node_hosting_privileged_pod_in_namespace": (("k8s",), "namespace",
        "Node hosts a pod of that namespace with a privileged container (containers, initContainers or "
        "ephemeralContainers); added SYS_ADMIN / SYS_MODULE / DAC_READ_SEARCH / ALL, or SYS_PTRACE with hostPID, "
        "match conditionally. hostNetwork, hostIPC and hostPID alone do not match."),
    "k8s_node_hosting_host_mount_pod_in_namespace": (("k8s",), "namespace",
        "Node hosts a pod of that namespace mounting a sensitive hostPath: a container runtime socket or a node "
        "credential path (even readOnly), or a host-executed path mounted writable; /etc/kubernetes, /home, "
        "/var/lib/docker|containerd and subPath mounts match conditionally. Other hostPaths (e.g. /var/log) do not match."),
    "k8s_sa_name": (("k8s",), "string_or_list", "Target service account name is one of the listed names."),
    "k8s_sa_used_by_pod_consuming_configmap": (("k8s",), "bool_true",
        "Service account is used by a running pod that consumes a ConfigMap (volume, projected volume, envFrom or "
        "env valueFrom; kube-root-ca.crt ignored); always conditional because execution of the content is not verified."),
    "exclude_names": (("k8s",), "string_or_list", "Drop targets whose name is in the list."),
    "k8s_sa_cloud_binding": (("k8s",), "string",
        "Cloud identity bound to the source SA via irsa|eks_pod_identity|gke_workload_identity|azure_workload_identity|aks_identity_binding (cloud facts needed)."),
    "trust_allows_k8s_sa_oidc_subject": (("k8s",), "bool_true", "IAM role trust allows the cluster OIDC subject of the SA (cloud facts needed)."),
    "gcp_workload_identity_user_granted_to_k8s_sa": (("k8s",), "bool_true",
        "GSA grants roles/iam.workloadIdentityUser to the KSA member (cloud facts needed)."),
    "azure_fic_matches_k8s_sa": (("k8s",), "bool_true", "Federated identity credential subject matches the SA (cloud facts needed)."),
    "k8s_node_cloud_identity": (("k8s",), "bool_true", "Cloud identity attached to the node (cloud facts needed)."),
    "k8s_nodes_mapped_to_cloud_identity": (("k8s",), "bool_true",
        "Nodes running with the source EKS node role (instance facts) that the role is mapped to: a node access entry "
        "(EC2_LINUX/EC2_WINDOWS) = derived, no entry = conditional (aws-auth mapRoles not collected; dropped in API-only "
        "authentication mode); not evaluated without the related AWS eks_access_entry inventory."),
    "k8s_sa_absent_but_bound": (("k8s",), "bool_true",
        "Service account referenced by a (Cluster)RoleBinding subject but absent from the serviceaccount inventory "
        "(virtual SA node; anyone who can create it inherits the binding)."),
    "trust_allows_oidc_subject_wildcard": (("k8s",), "string",
        "IAM role trust matches the given OIDC subject pattern (e.g. system:serviceaccount:{pivot.namespace}:*) on the cluster OIDC provider (cloud facts needed)."),
    "kube2iam_namespace_permits_role": (("k8s",), "namespace",
        "Namespace (usually {pivot.namespace}) annotation iam.amazonaws.com/permitted (kube2iam/kiam) allows the target role (annotation facts needed)."),
    "k8s_sa_has_token_secret": (("gcp",), "bool_true",
        "GKE: KSAs of cluster {target.scope} referenced by a kubernetes.io/service-account-token Secret "
        "(annotation kubernetes.io/service-account.name); joined from the related K8s snapshot, else one conditional aggregate per cluster."),
    "k8s_sa_in_cluster": (("gcp",), "bool_true",
        "GKE: every KSA of cluster {target.scope}; joined from the related K8s snapshot, else one conditional aggregate per cluster."),
    "assumable_by_pivot_role": (("aws",), "bool_true",
        "Role the pivot role ({pivot}, e.g. a StackSet administration role) can assume: its trust admits the pivot role "
        "(or its account) and the pivot's identity policy allows sts:AssumeRole on it (trust naming the pivot ARN in the same "
        "account suffices). For StackSets, a new or existing self-managed StackSet route must also reach the target "
        "account. The pivot itself is excluded; roles in other accounts are included."),
    "k8s_sa_has_legacy_token_secret": (("k8s",), "bool_true",
        "ServiceAccounts referenced by a kubernetes.io/service-account-token Secret in their namespace "
        "(annotation kubernetes.io/service-account.name, from secret metadata; never data)."),
    "openshift_namespace_has_sa_with_host_scc": (("k8s",), "namespace",
        "The OpenShift namespace (usually {pivot.namespace}) contains an SA allowed to use a host-level SCC (privileged / host "
        "PID / network / IPC / hostPath): from collected securitycontextconstraints users[] / groups[] and RBAC 'use' grants on "
        "security.openshift.io securitycontextconstraints. Unresolved when the SCC inventory or api_discovery is missing."),
    "service_plane": (("aws",), "service_plane",
        "aws_service_plane_admin: the managed service whose application plane is administered "
        "(" + "|".join(SERVICE_PLANES) + "; IAM service prefix)."),
    "k8s_sa_used_by_pending_pod": (("k8s",), "bool_true",
        "Service account of a collected pod in phase Pending with no spec.nodeName (unscheduled; a pods/binding or "
        "bindings write can place it on a node the attacker controls)."),
    "k8s_node_hosting_pod_of_source": (("k8s",), "bool_true",
        "k8s_node targets hosting a collected pod that runs as the source service account (the 'associated node')."),
    "k8s_sa_namespace_absent": (("k8s",), "bool_true",
        "Service account referenced by a binding subject or an SCC users[] entry whose namespace is absent from a "
        "complete namespace inventory (creating the namespace and the SA inherits the reference)."),
    "k8s_sa_named_in_scc_users": (("k8s",), "bool_true",
        "OpenShift: service account named in a SecurityContextConstraints users[] entry (system:serviceaccount:<ns>:<name>); "
        "SA nodes that only an SCC names are virtual (not in the serviceaccount inventory). Not OpenShift: no targets."),
    "k8s_secret_holds_cloud_credential": (("k8s",), "secret_provider",
        "cloud_identity targets standing for a static cloud credential stored in a Secret (one node per Secret, scope "
        "<cluster>/<namespace>, {target.name} = Secret name), recognised from Secret metadata only (name, labels, "
        "annotations: never data); value aws|gcp|azure|any or a list. Always conditional (content not verified)."),
    "k8s_secret_holds_remote_cluster_credential": (("k8s",), "label_selector",
        "k8s_remote_cluster targets: Secrets whose labels match one 'key=value' (or 'key') selector; true = known markers "
        "(argocd.argoproj.io/secret-type=cluster, cluster.x-k8s.io/cluster-name with a *-kubeconfig name)."),
    "gcp_group_join_open_to_source": (("gcp",), "bool_true",
        "gcp_group targets the source can join without approval (Groups Settings whoCanJoin ANYONE_CAN_JOIN, or "
        "ALL_IN_DOMAIN_CAN_JOIN with the source's email domain equal to the group's; a source outside the group's "
        "domain also needs allowExternalMembers=true). Use with requires: {} and source_kind gcp_user."),
    "gcp_workspace_super_admin_with_registered_domain": (("gcp",), "bool_true",
        "gcp_workspace_user targets that are Workspace super administrators whose primary email domain is the domainName "
        "of a collected Cloud Domains registration; {target.domain_registration} = those registration resource names."),
    "gcp_image_family_consumer": (("gcp",), "bool_true",
        "gcp_service_account targets attached to a collected instance template whose boot disk sourceImage is an image "
        "family (projects/<p>/global/images/family/<f>); {target.image_family_project} = projects/<p> of those families."),
    "target_id_glob": (("aws", "gcp", "azure", "k8s"), "glob_list",
        "Generic (evaluator): target node id (ARN / SA email / object id / cluster:ns:name) matches one of the "
        "case-insensitive globs (e.g. '*-compute@developer.gserviceaccount.com', 'arn:aws:iam::*:role/aws-reserved/*')."),
    "target_name_glob": (("aws", "gcp", "azure", "k8s"), "glob_list",
        "Generic (evaluator): target display name (role / user / SA / identity name) matches one of the globs."),
    "exclude_target_id_glob": (("aws", "gcp", "azure", "k8s"), "glob_list",
        "Generic (evaluator): drop targets whose node id matches one of the globs."),
}
# Keys allowed under the top-level `source_selector` (restricts which principals act as sources).
SOURCE_SELECTOR_KEYS = {
    "azure_member_user": (("azure",), "bool",
        "Source is a directory user whose collected userType is Member; absent or Guest userType does not satisfy this selector."),
    "include_service_managed": (("aws", "gcp", "azure", "k8s"), "bool",
        "Allow service-managed identities (AWS service-linked roles, Google-managed agents, Microsoft first-party "
        "service principals) as sources; they are skipped by default because customers cannot act as them."),
    "k8s_node_role": (("k8s",), "string", "Node carries node-role.kubernetes.io/<value> label."),
    "eks_access_entry_type": (("k8s",), "string",
        "EKS access entry type of the source EKS node-role cloud identity (related AWS eks_access_entry); sources whose "
        "entries have another type are dropped, sources without an entry are decided by the target selector."),
    "source_id_glob": (("aws", "gcp", "azure", "k8s"), "glob_list",
        "Generic (evaluator): the source principal id matches one of the case-insensitive globs."),
    "source_reaches_kind": (("aws", "gcp", "azure", "k8s"), "target_kind",
        "Generic (evaluator, graph post-pass): the source is of that target kind or reaches a node of that kind through "
        "the other techniques' edges (fixpoint); the edge takes the weakest confidence of the best chain and the "
        "condition source_reaches_<kind>_via_chain."),
    "source_bound_to_aggregated_clusterrole": (("k8s",), "bound_scope",
        "Source is bound to a ClusterRole with an aggregationRule: true = by any (Cluster)RoleBinding, 'cluster' = by a "
        "ClusterRoleBinding only (cluster-wide)."),
    "gcp_workspace_admin_role": (("gcp",), "string",
        "Source is a Workspace/Cloud Identity user holding that admin role: 'super_admin' (users.isAdmin or a role with "
        "isSuperAdminRole) or an admin roleId / roleName (Admin SDK roleAssignments)."),
}
# Collection types/fields a selector or requirement needs; reported in coverage when missing.
FACTS_NEEDED = {
    "gcp_clouddeploy_custom_render_path": "Cloud Deploy pipelines, targets, custom target types, and their render execution service accounts",
    "gcp_clouddeploy_existing_custom_render_path": "Cloud Deploy pipelines, targets, custom target types, and their render execution service accounts",
    "gcp_clouddeploy_pipeline_policy_custom_render_path": "Cloud Deploy pipelines, targets, custom target types, and their render execution service accounts",
    "gcp_clouddeploy_configurable_custom_render_path": "Cloud Deploy pipelines, targets, custom target types, and their render execution service accounts",
    "gcp_cloudbuild_writable_trigger_token_path": "Cloud Build repository push triggers, source build config, and explicit service accounts",
    "gcp_cloudbuild_writable_trigger_policy_path": "Cloud Build repository push triggers, source build config, and explicit service accounts",
    "gcp_workflows_update_execute_same_workflow": "Active Workflows resources, their attached service accounts, and exact workflow permissions",
    "gcp_workflows_update_attach_path": "Active Workflows resources and exact workflow update and execution permissions",
    "gcp_workflows_observed_external_execution": "Active Workflows resources and recorded Cloud Scheduler execution targets",
    "gcp_cloudscheduler_update_job_path": "Cloud Scheduler jobs, their state, and exact update or resume permissions",
    "gcp_cloudscheduler_authenticated_delivery": "Project number and Cloud Scheduler service agent role binding",
    "gcp_cloudtasks_enqueue_path": "Cloud Tasks queues, state, target overrides, queue IAM, and exact task creation grants",
    "gcp_cloudtasks_authenticated_delivery": "Project number, Cloud Tasks service agent role, and access to the target service account",
    "gcp_cloudtasks_queue_policy_path": "Cloud Tasks queue state and IAM, prior task grants, exact policy and override-update grants, deny policy, and IAM member restrictions",
    "gcp_cloudfunctions_create_path": "Cloud Build default identity by location, Cloud Functions create and source-upload rights, build actAs, and invocation rights",
    "gcp_cloudfunctions_existing_source_update_path": "Cloud Functions inventory, exact update and upload rights, build identity, and invocation route",
    "gcp_cloudfunctions_env_startup_path": "Active Cloud Functions with a Node.js 20 or later runtime, exact update rights, build actAs, and an invocation route",
    "gcp_cloudfunctions_source_deploy_build_path": "Cloud Build legacy default identity, function create or update and source-upload rights, and runtime service-account actAs",
    "gcp_vertex_new_model_endpoint_path": "Vertex model upload, endpoint create and deploy permissions, project number, and service-agent delegation to the target service account",
    "gcp_vertex_batch_prediction_path": "Vertex batch prediction job creation, project number, and service-agent delegation to the target service account",
    "gcp_workbench_existing_takeover_path": "Workbench instance inventory with attached service account, state, instance IAM policy, and exact update and boot or policy-write rights",
    "gcp_run_job_override_path": "Cloud Run job inventory with pinned service account and run plus runWithOverrides on the same job",
    "gcp_run_job_policy_override_path": "Cloud Run job inventory with pinned service account and setIamPolicy on that job",
    "gcp_run_service_update_path": "Cloud Run service inventory and update permission on an existing service in the target project",
    "gcp_run_job_update_execute_path": "Cloud Run job inventory and update plus run permissions on the same existing job in the target project",
    "gcp_run_instance_create_or_update_path": "Cloud Run instance inventory, project-level create permission, and exact existing-instance update permission",
    "gcp_run_instance_ssh_path": "Cloud Run instance inventory, its SSH setting and state, and exact SSH and start permissions",
    "gcp_run_service_ssh_path": "Cloud Run service inventory, SSH flag, second-generation environment, readiness, and exact SSH permission",
    "gcp_appengine_instance_ssh_path": "Flexible App Engine instance, backing VM, runtime identity, debug or OS Login rights, and SSH route",
    "gcp_appengine_deploy_path": "Existing App Engine app, staging bucket, and target runtime service-account Docker repository access",
    "gcp_appengine_legacy_actas_unenforced": "Project constraint visibility and effective policy for the legacy App Engine default service-account exception",
    "gcp_appintegration_run_as_path": "Application Integration service state, observed integration versions, exact source IAM permissions, and target service-account actAs",
    "gcp_gcr_namespace_path": "Artifact Registry redirection and repository coverage, exact create and upload grants, and a tagged Cloud Run consumer with its runtime service account",
    "gcp_artifact_policy_consumer_path": "Exact standard Docker repository, mutable tagged Cloud Run consumer, runtime account, and repository-scoped IAM policy write",
    "gcp_agentidentity_retrieve_path": "Exact enabled Google OAuth provider and active authorization with useful granted scopes",
    "gcp_agentidentity_update_path": "Exact enabled Google OAuth provider and active authorization with a possible later refresh through a changed token endpoint",
    "gcp_batch_agent_reporter_on_target": "Target service account's effective batch.states.report grant in the job project",
    "gcp_run_worker_pool_create_or_update_path": "Cloud Run worker pool inventory, project-level create permission, and exact existing-pool update permission",
    "gcp_cross_project_run_service": "effective cross-project service-account policy, Cloud Run host project number, and the host service agent's target service-account grant",
    "gcp_cross_project_run_job": "effective cross-project service-account policy, Cloud Run job host project number, and the host service agent's target service-account grant",
    "gcp_cross_project_cloudbuild": "effective cross-project service-account policy, Cloud Build host project number, and the host service agent's target service-account grant",
    "gcp_cross_project_workflows": "effective cross-project service-account policy, Workflows host project number, and the host service agent's target service-account grant",
    "iam_user_access_keys_not_collected": "the target IAM user's access-key list",
    "lambda_code_signing_not_collected": "the Lambda function's code-signing attachment and configuration",
    "lambda_code_signing_function_binding_unclear": "a match between the permitted Lambda function and its enforced code-signing setting",
    "source_permissions_boundary_not_collected": "the source role or user's permissions boundary policy document",
    "source_permissions_boundary_conditions": "the source permissions boundary conditions needed to decide full account administration",
    "source_boundary_policy_version_contents": "stored versions of the source permissions boundary policy",
    "source_boundary_replacement_authorization": "the replacement boundary policy and request conditions on changing the source boundary",
    "aws_s3_policy_self_grant": "unique collected aws_s3_policy_self_grant_evidence with exact source, bucket, prefix, policy principal/resource and observed before/after GetObject authorization",
    "aws_sqs_policy_self_grant": "the exact queue ARN, a same-account IAM user's SetQueueAttributes grant, absent prior ReceiveMessage and no surviving explicit deny or SSE-KMS key",
    "aws_sns_policy_self_grant": "the exact topic ARN, a same-account IAM user's SetTopicAttributes grant, absent prior Subscribe and no surviving explicit deny",
    "aws_dynamodb_policy_self_grant": "an active table with an exact ARN and AWS-owned encryption, a same-account IAM user's PutResourcePolicy grant, absent prior GetItem and no surviving explicit deny",
    "aws_s3_access_grants_self_grant": "unique collected aws_s3_access_grants_self_grant_evidence with exact source, location role, grant, target prefix, scoped session and observed before/after GetObject authorization",
    "aws_secretsmanager_policy_self_grant": "unique reviewed exact-source, exact-secret policy grant with observed before/after GetSecretValue and KMS authorization",
    "aws_efs_policy_self_grant": "unique reviewed exact-source, exact-file-system policy grant with observed before/after ClientMount authorization",
    "aws_cases_tag_self_grant": "unique reviewed exact-source Cases domain tag mutation and before/after PutCaseEventConfiguration authorization",
    "aws_sitewise_portal_self_grant": "unique reviewed exact-source SiteWise Monitor portal ADMINISTRATOR access policy with observed before/after access",
    "k8s_helm_values_rbac": "unique collected k8s_helm_values_rbac_evidence with the exact source ConfigMap, values key, chart fields, reconciler authority, generated Role/RoleBinding, source ServiceAccount, prior denial and admitted observed grant",
    "k8s_verified_pivot": "unique collected k8s_verified_pivot_evidence with exact source, Secret/RoleBinding/Pod object, accepted target subject, and a newly allowed named action",
    "azure_challenge_fact": "azure_privesc_challenge_evidence with exact TechniqueId, SourceId, TargetKind, TargetId, TargetScope, EvidenceRef, Status and VerifiedPreconditions",
    "azure_external_principal_evidence": "unique collected azure_external_principal_evidence binding exact source action/resource, named adjacent-plane subject, usable credential or grant, prior denial and newly allowed action",
    "k8s_challenge_fact": "k8s_privesc_challenge_evidence with exact TechniqueId, SourceId, TargetKind, TargetId, TargetScope, EvidenceRef, Status and VerifiedPreconditions",
    "gcp_challenge_fact": "gcp_privesc_challenge_evidence with TechniqueId, SourceId, TargetKind, TargetId, "
                          "TargetScope, Status and VerifiedPreconditions for the exact exploit preconditions",
    "gcp_resource_self_grant": "unique accepted mutation evidence, or complete exact-resource inventory and IAM policy with a supported prospective self-grant; absent prerequisites stay unresolved",
    "gcp_external_principal_evidence": "unique collected gcp_external_principal_evidence binding the exact action, target service/subject, usable credential, prior source denial and observed new permission",
    "gcp_agentregistry_skill_evidence": "unique collected gcp_agentregistry_skill_evidence binding an exact Agent Registry Skill revision, floating consumer, runtime identity, and newly successful bounded action",
    "gcp_bounded_access_gain": "unique collected gcp_bounded_access_gain_evidence binding exact source actions/resources, intermediate object, protected resource and before/after action",
    "aws_challenge_fact": "aws_privesc_challenge_evidence with exact TechniqueId, SourceArn, TargetKind, TargetId, TargetAccount, Status and VerifiedPreconditions",
    "via_resource_type": "AWS: per-type workload inventories carrying the role (ecs task definitions, glue jobs, sagemaker, ...), "
                         "fully collected in every region: imagebuilder_pipeline (imagebuilder:ListImagePipelines + "
                         "ListInfrastructureConfigurations {instanceProfileName}), sagemaker_user_profile (sagemaker:ListUserProfiles + "
                         "DescribeUserProfile {UserSettings.ExecutionRole} / DescribeDomain DefaultUserSettings.ExecutionRole), "
                         "sagemaker_space (ListSpaces + DescribeSpace {SpaceArn, AppType, SharingType, OwnerUserProfileName} "
                         "+ DescribeDomain DefaultSpaceSettings.ExecutionRole or owner DescribeUserProfile ExecutionRole), "
                         "sagemaker_cluster (sagemaker:ListClusters + DescribeCluster {InstanceGroups[].ExecutionRole})",
    "via_artifact_type": "AWS: artifact consumer mapping (S3 object / ECR repo / SSM document -> consuming role)",
    "consumer_input_writable_via": "AWS: workload input mapping (ECR repo / S3 object -> consuming role); Image Builder: "
                                   "imagebuilder_pipeline (ListImagePipelines + ListInfrastructureConfigurations) in every region",
    "cognito_user_pool_covered_by": "AWS: cognito_identity_pool Roles {Roles, RoleMappings} (cognito-identity:GetIdentityPoolRoles) + "
                                    "Configuration.CognitoIdentityProviders (DescribeIdentityPool) in every region",
    "cognito_developer_authenticated_role": "AWS: cognito_identity_pool Configuration.DeveloperProviderName "
                                            "(DescribeIdentityPool), Roles.Roles.authenticated (GetIdentityPoolRoles), "
                                            "and exact role web-identity trust for the pool audience and authenticated method",
    "cognito_developer_classic_role": "AWS: cognito_identity_pool Configuration.{DeveloperProviderName, AllowClassicFlow} "
                                      "(DescribeIdentityPool) and IAM role web-identity trust for that pool's audience "
                                      "and authenticated developer-provider method",
    "cognito_developer_settable_authenticated_role": "AWS: cognito_identity_pool Configuration.DeveloperProviderName "
                                                     "(DescribeIdentityPool) and IAM role web-identity trust for "
                                                     "the same pool's audience and authenticated method",
    "cognito_developer_enable_classic_role": "AWS: cognito_identity_pool Configuration.{DeveloperProviderName, AllowClassicFlow} "
                                             "(DescribeIdentityPool), IAM role web-identity trust, and exact "
                                             "UpdateIdentityPool plus token-mint permission on the same pool",
    "cognito_user_pool_group_role_covered_by": "AWS: cognito_user_pool Groups {GroupName, RoleArn} (cognito-idp:ListGroups) in every region",
    "codedeploy_group_instance_role_covered_by": "AWS: codedeploy_deployment_group {ec2TagFilters, ec2TagSet, autoScalingGroups} "
                                                 "(codedeploy:BatchGetDeploymentGroups) + instance {Tags, IamInstanceProfile} in the same region",
    "ecs_task_role_on_ec2_capacity": "AWS: ecs_task_definition {taskDefinitionArn, taskRoleArn, compatibilities} + ecs_cluster "
                                     "{registeredContainerInstancesCount} in every region (ecs:DescribeTaskDefinition, ecs:DescribeClusters)",
    "ecs_container_instance_role_in_cluster_covered_by": "AWS: ecs_cluster ContainerInstances {containerInstanceArn, ec2InstanceId} "
                                                         "(ecs:ListContainerInstances + DescribeContainerInstances) and Tasks {taskDefinitionArn, "
                                                         "launchType, containerInstanceArn, overrides.taskRoleArn} (ecs:ListTasks + DescribeTasks)",
    "ecs_task_colocated_with_source_container_instance": "AWS: ecs_cluster ContainerInstances {containerInstanceArn, ec2InstanceId} + Tasks "
                                                         "{taskDefinitionArn, launchType, containerInstanceArn, taskRoleArn, executionRoleArn, overrides} "
                                                         "+ task definitions {taskRoleArn, executionRoleArn} + instance IamInstanceProfile",
    "eks_authentication_mode": "AWS: eks_cluster describe_cluster {cluster.arn, cluster.accessConfig.authenticationMode}",
    "trust_allows_oidc_provider_covered_by": "AWS: iam_role AssumeRolePolicyDocument (collected)",
    "trust_federated_provider_missing": "AWS: iam_saml_provider (iam:ListSAMLProviders {Arn}) / iam_oidc_provider (iam:ListOpenIDConnectProviders {Arn})",
    "trust_allows_principal_org": "AWS: organization_account Arn (organizations:ListAccounts; org id + management account) + organization_parent root",
    "org_member_account": "AWS: organization_account {Id, Arn, State} (organizations:ListAccounts)",
    "emr_runtime_role_of_cluster": "AWS: emr_cluster (elasticmapreduce:ListClusters + DescribeCluster {Cluster.SecurityConfiguration, "
                                   "Cluster.Ec2InstanceAttributes.IamInstanceProfile})",
    "trust_allows_emr_containers_oidc": "AWS: iam_role AssumeRolePolicyDocument (collected)",
    "instance_profile_name_prefix_or_path": "AWS: iam_role InstanceProfileList (collected)",
    "portfolio_of_target_product_covered_by": "AWS: servicecatalog_portfolio {ARN, Constraints[{Type, ProductId, ConstraintParameters.RoleArn|LocalRoleName}]} "
                                              "(servicecatalog:ListPortfolios, ListConstraintsForPortfolio, DescribeConstraint)",
    "assigned_to_identity_center_group": "AWS: aws_identity_center_account_assignment {PrincipalType, PrincipalId} "
                                         "(sso-admin:ListAccountsForProvisionedPermissionSet + ListAccountAssignments) in every region",
    "rolesanywhere_profile_includes_target": "AWS: rolesanywhere_profile {profileArn, roleArns, enabled} (rolesanywhere:ListProfiles) "
                                             "in every region",
    "entra_target_not_in_restricted_au": "Azure: directory_administrative_unit {id,isMemberManagementRestricted} + members",
    "entra_reset_matrix_column": "Azure: directory_role_assignment for target users, directory_group.isAssignableToRole, AU membership",
    "entra_sp_has_tenant_application": "Azure: directory_application.appId",
    "entra_app_sign_in_audience": "Azure: directory_application.signInAudience",
    "entra_source_is_owner_of_application": "Azure: directory_owner (applications/{id}/owners)",
    "entra_source_is_owner_of_service_principal": "Azure: directory_owner (servicePrincipals/{id}/owners)",
    "entra_source_is_owner_of_group": "Azure: directory_owner (groups/{id}/owners)",
    "entra_pim_eligible_for_source": "Azure: directory_role_eligibility_schedule (roleManagement/directory/roleEligibilitySchedules)",
    "entra_agent_blueprint_principal_or_child_identity": "Azure: agent identity blueprint principals",
    "entra_user_upn_on_federatable_custom_domain": "Azure: directory_domain {id,authenticationType,isVerified} + user UPNs",
    "entra_group_role_assignable": "Azure: directory_group.isAssignableToRole",
    "entra_group_membership_type": "Azure: directory_group.groupTypes (collected)",
    "entra_group_membership_cloud_writable": "Azure: directory_group.onPremisesSyncEnabled and cloud source-of-authority status for synchronized groups",
    "entra_group_source_self_membership": "Azure: source principal type and directory_app_role_assignment Graph application permissions",
    "entra_dynamic_rule_attributes_writable_by_source": "Azure: directory_group.membershipRule",
    "entra_dynamic_rule_satisfiable_by_invited_guest": "Azure: directory_group.membershipRule + authorizationPolicy.allowInvitesFrom",
    "azure_host_linked_to_pivot": "Azure: avd_session_host {id, properties.resourceId} scoped to the host pool id "
                                  "(hostPools/{id}/sessionHosts) + Resource Graph applicationGroups properties.hostPoolArmPath; "
                                  "automation_hybrid_worker {id, properties.vmResourceId} scoped to the automation account "
                                  "(hybridRunbookWorkerGroups/*/hybridRunbookWorkers); Resource Graph "
                                  "Microsoft.DevTestLab/labs/virtualMachines properties.computeId (or devtest_lab_vm scoped to "
                                  "the lab); Service Fabric cluster -> node VMSS link (not modelled)",
    "azure_deployer_of_pivot": "Azure: deployment script / pipeline runner identities",
    "ml_compute_assigned_to_source": "Azure: machine learning compute instances personal assignment",
    "credential_stored_in_scope": "Azure: secret holder mapping (never secret values)",
    "azure_appservice_config_code_path": "Azure: exact App Service kind, hosting plan, attached identity and config child scope; Windows and app-settings-only routes need executable package or payload evidence",
    "azure_appservice_kudu_code_path": "Azure: exact App Service kind, hosting plan, running state and source publish/start permissions on that app; SCM network reachability remains conditional",
    "azure_appservice_onedeploy_code_path": "Azure: exact App Service kind, attached identity, extensions/onedeploy permission and running state; custom container package execution needs evidence",
    "azure_appservice_backup_restore_code_path": "Azure: exact App Service restore permission, supported hosting tier and runtime, attached identity, and running state; backup validity, storage access and execution remain conditional",
    "azure_appservice_enable_publishing_credentials_code_path": "Azure: exact app SCM policy child write plus publishing credential read, app kind and running state; policy change, SCM reachability and execution remain conditional",
    "azure_appservice_publishing_credentials_code_path": "Azure: exact App Service publishxml or config/list permission, collected SCM basic auth policy, app kind and running state; SCM reachability and package execution remain conditional",
    "azure_appservice_sitecontainers_code_path": "Azure: exact app SiteContainer child write, Linux SiteContainers runtime mode, attached identity and running state; image run and identity access remain conditional",
    "azure_appservice_siteextensions_code_path": "Azure: exact Windows App Service site extension write, attached identity and running state; package availability and app-content execution remain conditional",
    "azure_appservice_slot_code_path": "Azure: exact deployment slot identity and executable slot-scoped publish, source-control, config or SiteContainer route; runtime and deployment stay conditional",
    "azure_appservice_slot_swap_code_path": "Azure: exact production app identity, inventoried source slot, code-bearing slot route and site-level or same-slot swap action",
    "azure_appservice_sourcecontrol_code_path": "Azure: exact production app sourcecontrols/web write, code app runtime and start availability; deployment remains conditional",
    "azure_arc_entra_admin_ssh_path": "Azure: exact Arc machine and default endpoint rights, configured SSH service and provisioned Entra SSH extension; agent and OS login remain conditional",
    "azure_arc_custom_script_code_path": "Azure: exact Arc identity machine and Custom Script child write, connected agent, enabled full-mode extension manager and compatible allow/block lists",
    "azure_arc_run_command_code_path": "Azure: exact Arc identity machine and Run Command child write, agent v1.33 or later, enabled handler and compatible local allow/block lists",
    "azure_deployment_script_uami_path": "Azure: exact script create/update and assignable UAMI with storage/ACI support rights in the script resource group",
    "azure_appservice_slot_publishing_credentials_code_path": "Azure: exact slot publishxml or config/list permission, collected slot SCM basic auth policy, runtime and running state; SCM reachability and deployment remain conditional",
    "k8s_sa_cloud_binding": "Cloud: IRSA annotations + IAM trust, EKS pod identity associations, GKE WI bindings, AKS FICs",
    "trust_allows_k8s_sa_oidc_subject": "AWS: iam_role trust policies in the cluster's account",
    "gcp_workload_identity_user_granted_to_k8s_sa": "GCP: service_account iamPolicy",
    "azure_fic_matches_k8s_sa": "Azure: user-assigned identity federatedIdentityCredentials",
    "k8s_node_cloud_identity": "Cloud: node instance role / node SA",
    "k8s_node_hosting_privileged_pod_in_namespace": "K8s: pod inventory (spec.containers/initContainers/ephemeralContainers securityContext)",
    "k8s_node_hosting_host_mount_pod_in_namespace": "K8s: pod inventory (spec.volumes hostPath + volumeMounts readOnly/subPath)",
    "k8s_sa_used_by_pod_consuming_configmap": "K8s: pod inventory (configMap volumes, envFrom, configMapKeyRef)",
    "k8s_nodes_mapped_to_cloud_identity": "AWS (related snapshot): eks_access_entry (eks:ListAccessEntries + DescribeAccessEntry {type}) "
                                          "of the EKS cluster, fully collected, plus instance facts mapping nodes to their role",
    "trust_allows_oidc_subject_wildcard": "AWS: iam_role trust policies in the cluster's account (join with AWS snapshot)",
    "kube2iam_namespace_permits_role": "K8s: namespace metadata.annotations (iam.amazonaws.com/permitted)",
    "k8s_sa_has_legacy_token_secret": "K8s: secret_metadata {metadata.namespace, type, metadata.annotations[kubernetes.io/service-account.name]}",
    "openshift_namespace_has_sa_with_host_scc": "K8s/OpenShift: securitycontextconstraints {users, groups, allowHostPID/Network/DirVolumePlugin, allowPrivilegedContainer}",
    "gcp_implicit_delegation_chain": "GCP: service_account iamPolicy + project/folder/org iam_policy (collected)",
    "ecr_tag_immutability": "AWS: ecr_repository {repositoryArn, imageTagMutability}",
    "pod_security_admission": "K8s: namespace inventory (metadata.labels pod-security.kubernetes.io/enforce) of the namespace the "
        "workload is created in ({pivot.namespace}, {target.namespace} or every namespace for cluster-wide grants)",
    "pivot_namespace_psa_enforce_baseline_or_restricted": "K8s: namespace inventory (metadata.labels "
        "pod-security.kubernetes.io/enforce) of the pivot namespaces",
    "admission_policy": "K8s: admission_policy (ValidatingAdmissionPolicy / MutatingAdmissionPolicy and their bindings) "
        "plus namespace labels for namespaceSelector matching",
    "admission_webhook": "K8s: admission_configuration (ValidatingWebhookConfiguration webhooks[].rules / namespaceSelector / "
        "failurePolicy) plus namespace labels",
    "kyverno_policy": "K8s: api_discovery (kyverno.io / policies.kyverno.io API groups)",
    "gatekeeper_constraint": "K8s: api_discovery (templates|constraints|config.gatekeeper.sh API groups)",
    "k8s_sa_has_token_secret": "K8s: secret metadata {metadata.namespace, type, metadata.annotations[kubernetes.io/service-account.name]} "
                               "(never data) in a K8s snapshot of the GKE cluster passed as related_snapshots; GCP: gke_cluster",
    "k8s_sa_in_cluster": "K8s: serviceaccount inventory of the GKE cluster passed as related_snapshots; GCP: gke_cluster",
    "assumable_by_pivot_role": "AWS: iam_role trust policies + the pivot role's identity policies (collected)",
    "gcp_workspace_admin_role": "GCP: workspace_user {primaryEmail, isAdmin}, workspace_role {roleId, roleName, isSuperAdminRole}, "
                                "workspace_role_assignment {roleId, assignedTo} (Admin SDK Directory API)",
    "k8s_sa_absent_but_bound": "K8s: serviceaccount inventory for every namespace (collected)",
    "service_plane": "AWS: application-plane inventories in every region: connect_instance (connect:ListInstances), "
                     "grafana_workspace (grafana:ListWorkspaces), quicksight_user (quicksight:ListUsers), supplychain_instance "
                     "(scn:ListInstances), amplify_app BackendEnvironments (amplify:ListApps + ListBackendEnvironments)",
    "k8s_sa_used_by_pending_pod": "K8s: pod inventory {spec.serviceAccountName, spec.nodeName, status.phase}",
    "k8s_node_hosting_pod_of_source": "K8s: pod inventory {spec.serviceAccountName, spec.nodeName}",
    "k8s_sa_namespace_absent": "K8s: namespace inventory (complete) and bindings / securitycontextconstraint users",
    "k8s_sa_named_in_scc_users": "K8s (OpenShift): securitycontextconstraint {metadata.name, users}",
    "k8s_secret_holds_cloud_credential": "K8s: secret_metadata {metadata.name, namespace, labels, annotations} (never data)",
    "k8s_secret_holds_remote_cluster_credential": "K8s: secret_metadata {metadata.name, namespace, labels} (never data)",
    "gcp_group_join_open_to_source": "GCP: group {groupKey.id} with Groups Settings {whoCanJoin, allowExternalMembers} "
                                     "(groupssettings.googleapis.com groups/{email}; not collected by default)",
    "gcp_workspace_super_admin_with_registered_domain": "GCP: domains_registration {name, domainName} "
                                                        "(domains.googleapis.com projects/*/locations/*/registrations) + workspace_user isAdmin",
    "gcp_image_family_consumer": "GCP: instance_template {properties.disks[].initializeParams.sourceImage, properties.serviceAccounts[].email}",
    "eks_access_entry_type": "AWS (related snapshot): eks_access_entry (eks:DescribeAccessEntry {type}) of the EKS cluster",
    # Placeholders the models deliberately leave unresolved (the requirement is checked on ANY resource, unknown).
    "target.host_resource.content_storage": "Azure/GCP: the host's content storage (Function App AzureWebJobsStorage account, "
                                            "Composer DAG bucket, or other staging bucket); Composer bucket joins use collected environment metadata",
    "target.composer_dag_managed_folder": "GCP: collected managed folder whose prefix intersects a Composer environment's DAG prefix",
    "target.dataproc_init_managed_folder": "GCP: collected managed folder containing an exact Dataproc initialization action object",
    "target.dataproc_init_object": "GCP: exact Cloud Storage object named by a collected Dataproc initialization action",
    "target.cloudbuild_source_object": "GCP: exact unpinned StorageSource archive of a collected non-triggered Cloud Build",
    "target.host_resource.workspace": "Azure: the Machine Learning workspace of the compute / endpoint host - not collected",
    "graph_app_permission": "Azure: directory_app_role_assignment (servicePrincipals/{id}/appRoleAssignments) incl. resourceId+appRoleId",
    "entra_owner_of": "Azure: directory_owner {object_id, object_type, owner_ids}",
    "entra_pim_eligible_role": "Azure: directory_role_eligibility_schedule {principalId, roleDefinitionId, directoryScopeId}",
    "entra_tenant_setting": "Azure: directory_authorization_policy {allowInvitesFrom, guestUserRoleId}",
    "entra_group_member": "Azure: directory_group {id, displayName} + directory_membership (groups/{id}/transitiveMembers)",
    "fabric_workspace_role": "Azure/Fabric: fabric_workspace_role_assignment {workspaceId, principal{id,type}, role} "
                             "(GET api.fabric.microsoft.com/v1/workspaces/{id}/roleAssignments, scope Workspace.Read.All)",
    "fabric_workspace_identity": "Azure/Fabric: fabric_workspace {id, displayName, workspaceIdentity.servicePrincipalId} "
                                 "(GET api.fabric.microsoft.com/v1/workspaces/{id})",
    "intune_permission": "Azure/Intune: intune_role_assignment {id, members[group ids], scopeMembers, roleDefinition"
                         "{displayName, rolePermissions[].resourceActions[].allowedResourceActions}} "
                         "(deviceManagement/roleAssignments?$expand=roleDefinition)",
    "intune_managed_device_user": "Azure/Intune: intune_managed_device {id, userId, operatingSystem, azureADDeviceId} "
                                  "(deviceManagement/managedDevices)",
    "entra_catalog_role": "Azure: entitlement_role_assignment {principalId, roleDefinitionId, roleDefinition.displayName, "
                          "appScopeId '/AccessPackageCatalog/<id>' or '/'} (roleManagement/entitlementManagement/roleAssignments)",
    "entra_resource_in_catalog": "Azure: entitlement_catalog_resource {catalogId, originId, originSystem} "
                                 "(identityGovernance/entitlementManagement/catalogs/{id}/resources)",
    "entra_access_package_auto_assignment_open_to_guest":
        "Azure: entitlement_assignment_policy {accessPackageId, allowedTargetScope, automaticRequestSettings."
        "requestAccessForAllowedTargets, specificAllowedTargets[].membershipRule} + entitlement_access_package_resource "
        "{accessPackageId, originId} (accessPackages/{id}/resourceRoleScopes)",
    "entra_pim_group_eligible_for_source": "Azure: directory_group_eligibility_schedule {principalId, groupId, accessId, status} "
                                           "(identityGovernance/privilegedAccess/group/eligibilitySchedules)",
    "azure_consumer_of_pivot": "Azure: workload->resource bindings never collected (App Service/Functions Key Vault and App "
                               "Configuration references, AzureWebJobsStorage / WEBSITE_RUN_FROM_PACKAGE / trigger bindings, "
                               "Data Factory / Synapse linked services, Event Grid destinations; never values); RBAC read "
                               "grants on the pivot (collected) give conditional consumers",
    "azure_assignable_via_identity_holding": "Azure: role_assignment + role_definition of user-assigned identities (collected)",
    "azure_users_assigned_to_pivot": "Azure: role_assignment (Desktop Virtualization User) + directory_membership + "
                                     "Resource Graph applicationGroups (collected)",
    "attached_to_vm_joined_to_entra_domain_services": "Azure: vm resources[] extensions (JsonADDomainExtension settings.Name) + "
                                                      "Resource Graph Microsoft.AAD/domainServices properties.domainName",
    "azure_assignment_condition_uses_principal_attribute": "Azure: role_assignment condition (collected)",
}
# Machine-checked technique preconditions (entry field `preconditions: [id, ...]`). Each one is evaluated by the
# provider model against inventory facts: a target failing it is dropped, a target whose facts are missing becomes
# an "Unresolved" placeholder (unknown confidence, never FAIL). mode "target" depends only on the target and the
# inventory (shared candidate set); mode "source" also depends on the source principal.
PRECONDITIONS = {
    "braket_createjob_device_authorized": (("aws",), "source",
      "The caller can create a Braket hybrid job on a usable device rather than only on a job ARN.",
      "AWS: CreateJob must authorize a device ARN; a job-only grant cannot launch a hybrid job. Exact device grants outside the known simulator need device availability evidence."),
    "imagebuilder_component_publish_and_pipeline_start": (("aws",), "source",
        "The source can publish a newer build of an account-owned component consumed by one pipeline and start that same pipeline.",
        "AWS: complete Image Builder pipeline and recipe-component inventory; the same pipeline has the target instance-profile role, an unpinned component reference, source CreateComponent permission covering new versions or builds of that component, and source StartImagePipelineExecution on that pipeline"),
    "gameliftstreams_live_role_session_admin_shell": (("aws",), "source",
      "The caller can open an admin shell in one live GameLift Streams session carrying the target role.",
      "AWS: complete per-Region ListStreamGroups/ListStreamSessions inventory with the same session ARN, live status, exact RoleArn and parent group ARN; CreateStreamSessionAdminShell must allow that group"),
    "gameliftstreams_controlled_application_role_session": (("aws",), "source",
      "The caller can start a controlled GameLift Streams application in an eligible stream group with the target role.",
      "AWS: exact application content control, application-to-active-stream-group association and capacity, source StartStreamSession or CreateStreamUrl authorization on the required resources, and effective PassRole for the target role"),
    "ecs_exec_live_task_role": (("aws",), "source",
      "The caller can open an ECS Exec session in one running container carrying the target task role.",
      "AWS: collected running task and task-definition role, enabled ECS Exec and running ExecuteCommandAgent in the same container, exact cluster and task ExecuteCommand authorization, task-role SSM channel permissions, and any configured Exec KMS permissions"),
    "athena_existing_session_calculation_role": (("aws",), "source",
      "The caller can submit code to an idle PySpark 3 session with the target execution role.",
      "AWS: complete Athena ListSessions/GetSession inventory with exact SessionConfiguration.ExecutionRole, IDLE state, PySpark engine version 3, and StartCalculationExecution on its workgroup ARN"),
    "athena_existing_notebook_url_role": (("aws",), "source",
      "The caller can open an active PySpark 3 notebook backed by the target execution role.",
      "AWS: complete Athena ListSessions/GetSession inventory with exact SessionConfiguration.ExecutionRole, IDLE state, NotebookVersion, PySpark engine version 3, and CreatePresignedNotebookUrl on its workgroup ARN"),
    "athena_existing_spark_connect_role": (("aws",), "source",
      "The caller can get the endpoint token for an active Spark 3.5 session with the target execution role.",
      "AWS: complete Athena ListSessions/GetSession inventory with exact SessionConfiguration.ExecutionRole, active state, Apache Spark version 3.5, and GetSessionEndpoint on its workgroup and session ARNs"),
    "flink_new_application_startable": (("aws",), "source",
      "The caller can create and start one unused application name in the same Region.",
      "AWS: complete kinesisanalytics:ListApplications inventory in a Region, CreateApplication on *, and StartApplication on one available application ARN"),
    "flink_existing_studio_role_session": (("aws",), "source",
      "The caller can open a Zeppelin session on a running Studio application with the target role.",
      "AWS: complete Flink application detail; the same RUNNING INTERACTIVE application has the exact target ServiceExecutionRole and CreateApplicationPresignedUrl is authorized on that application ARN"),
    "ec2_spot_fleet_roles_ready": (("aws",), "source",
      "The caller can pass a Spot Fleet role, and the required service-linked roles exist or can be created.",
      "AWS: IAM role inventory, spotfleet.amazonaws.com trust, PassRole with PassedToService, and CreateServiceLinkedRole with AWSServiceName"),
    "quicksight_subscribed": (("aws",), "source",
      "The account has an active IAM-compatible QuickSight subscription and the source user's name is available.",
      "AWS: QuickSight subscription ACCOUNT_CREATED with IAM_ONLY or IAM_AND_QUICKSIGHT, and complete ListUsers in the registration Region"),
    "ec2_userdata_restart_execution_reviewed": (("aws",), "source",
      "The exact role-bearing EC2 instance executes changed user data on its next start.",
      "AWS: a fresh verified aws_privesc_challenge_evidence record naming the source, target role and instance, "
      "reviewed restart execution and role credential access; collected instance/profile state and exact "
      "ModifyInstanceAttribute(userData), StartInstances and, when running, StopInstances authorization"),
    "grafana_api_key_workspace_eligible": (("aws",), "source",
      "The selected Managed Grafana workspace still supports API keys through the AWS API.",
      "AWS: collected workspace ARN, ACTIVE status and Grafana version earlier than 12"),
    "grafana_service_account_workspace_eligible": (("aws",), "source",
      "The selected Managed Grafana workspace supports service accounts.",
      "AWS: collected workspace ARN, ACTIVE status and Grafana version 9 or later"),
    "grafana_saml_workspace_active": (("aws",), "source",
      "The selected Managed Grafana workspace can accept an authentication update.",
      "AWS: collected workspace ARN and ACTIVE status"),
    "batch_new_job_and_ec2_queue_authorized": (("aws",), "source",
      "One new Batch job definition can be registered and submitted through a usable EC2 job queue.",
      "AWS: batch:DescribeJobDefinitions, batch:DescribeJobQueues and batch:DescribeComputeEnvironments in the same Region; RegisterJobDefinition covers an unused name and SubmitJob covers its revision and one enabled valid EC2 queue"),
    "batch_existing_definition_submitjob_role": (("aws",), "source",
      "The caller can submit a command override through an existing EC2 Batch job definition with the target job role.",
      "AWS: complete Batch job-definition, queue and compute-environment inventory in one Region; ACTIVE container definition with exact jobRoleArn and image, enabled valid EC2 queue, and SubmitJob on both the versioned definition and queue ARNs"),
    "amplifybackend_create_token_backend_scope": (("aws",), "source",
      "The CreateToken grant covers a backend environment path as well as the challenge token path for the same app.",
      "AWS: a collected Amplify Gen 1 backend environment and amplifybackend:CreateToken on that app's backend environment path; a token-only grant remains unresolved"),
    "cloudcontrol_source_can_create_admin_user": (("aws",), "source",
      "The caller can pass a CloudFormation role that can create a new IAM user with a chosen console password and administrator permissions.",
      "AWS: PassRole to a CloudFormation-trusting role, then CreateUser, GetUser, CreateLoginProfile, and either AttachUserPolicy with AdministratorAccess or PutUserPolicy on one new user ARN"),
    "sagemaker_studio_profile_iam_domain_ready": (("aws",), "source",
        "The selected Studio profile belongs to an active IAM domain and can run a code app using its role.",
        "AWS: the exact user profile attached to the target role and its same-region domain are both InService, DescribeDomain reports AuthMode IAM, and a profile code app is InService or the source can CreateApp and AddTags on a matching app ARN"),
    "sfn_existing_state_machine_update_and_start": (("aws",), "source",
        "The source can update and start one active state machine using a passed execution role.",
        "AWS: a collected ACTIVE state machine ARN is covered by UpdateStateMachine and StartExecution, or by StartSyncExecution if the machine is EXPRESS"),
    "sagemaker_notebook_instance_accessible": (("aws",), "source",
        "The source can open a running notebook, or start a stopped notebook before opening it.",
        "AWS: the exact notebook attached to the target role is InService, or it is Stopped on a restartable platform and the source can call StartNotebookInstance on that notebook ARN"),
    "sagemaker_attached_notebook_lifecycle_update": (("aws",), "source",
        "The source can replace the startup script already attached to a notebook using the target role.",
        "AWS: a collected notebook names the exact existing lifecycle configuration and target RoleArn; UpdateNotebookInstanceLifecycleConfig covers that configuration ARN in the same account and Region, and the notebook can run again"),
    "sagemaker_new_notebook_creation_and_url_authorized": (("aws",), "source",
        "The source can create and open one new notebook instance using the passed role.",
        "AWS: a free notebook name in a collected Region is authorized for both CreateNotebookInstance and CreatePresignedNotebookInstanceUrl on the same ARN"),
    "apprunner_existing_customer_account": (("aws",), "source",
        "The account already uses App Runner, so it remains eligible to create services.",
        "AWS: a collected App Runner service with an ARN in the source account establishes prior App Runner use; no recorded service leaves eligibility unresolved"),
    "apprunner_existing_image_service_update": (("aws",), "source",
        "The source can update a running image-based App Runner service to use the passed instance role and a chosen image.",
        "AWS: a complete App Runner service inventory includes an exact RUNNING service ARN whose described SourceConfiguration uses ImageRepository; UpdateService covers that same ARN"),
    "apprunner_existing_instance_role_update": (("aws",), "source",
        "The source can change the start command of an existing image-based App Runner service with the target instance role.",
        "AWS: a collected RUNNING App Runner image service names the exact target InstanceRoleArn, and UpdateService covers that same service ARN"),
    "iot_new_alias_policy_certificate_same_region": (("aws",), "source",
        "One Region permits creation of a new IoT role alias, policy, and certificate that can receive that policy.",
        "AWS: iam:PassRole on the exact target and regional CreateRoleAlias, CreatePolicy, AttachPolicy, plus one global certificate action all authorize one source-account Region; alias and policy names have wildcard room and AttachPolicy covers new certificates"),
    "appsync_new_api_global_setup": (("aws",), "source",
        "The source can perform every action needed to create and invoke a new AppSync API using an API key.",
        "AWS: CreateGraphqlApi, StartSchemaCreation, CreateDataSource, CreateResolver and CreateApiKey are all authorized on the global resource rather than an existing API ARN"),
    "glue_existing_dev_endpoint_ssh_access": (("aws",), "source",
        "The source can add an SSH key to a ready Glue development endpoint with a public address.",
        "AWS: a complete development endpoint inventory records the exact role, READY status, public address, no legacy key and fewer than five managed keys; UpdateDevEndpoint and one endpoint-read action cover the same endpoint"),
    "glue_existing_session_ready_for_statement": (("aws",), "source",
        "The source can run a statement in a ready existing Glue session attached to the target role.",
        "AWS: a complete session inventory records the exact session ID, its execution role and READY status; RunStatement covers that session ARN"),
    "glue_new_session_with_statement": (("aws",), "source",
        "The source can create an interactive Glue session using the target role and run a statement in it.",
        "AWS: complete interactive session ID inventory in one Region; CreateSession and RunStatement both cover one unused session ARN chosen by the source"),
    "glue_existing_job_has_runnable_trigger": (("aws",), "source",
        "An existing Glue job that the source can update has a recorded way to run afterward.",
        "AWS: a recorded trigger in the job's Region names the same job; an active scheduled trigger has a schedule, or an on-demand trigger is startable by the source on that trigger ARN"),
    "glue_job_role_and_execution_bind": (("aws",), "source",
        "The source can create or update one Glue job with the passed role and cause that job to run.",
        "AWS: complete job inventory in one Region; CreateJob on one unused job ARN or UpdateJob on one existing job ARN; StartJobRun on that same job or CreateTrigger on an unused scheduled trigger ARN in the job's Region"),
    "glue_job_override_arguments_available": (("aws",), "source",
        "An existing Glue job can run with a script override supplied by the source.",
        "AWS: the job's command type and non-overridable code argument names are collected; --scriptLocation is not pinned; StartJobRun covers that job or CreateTrigger covers a new scheduled trigger name in its Region. Dependency-only routes remain unresolved until their runtime prerequisites are verified"),
    "glue_existing_job_script_object_writable_and_runnable": (("aws",), "source",
        "The source can replace the exact script object of an existing Glue job that runs as the target role.",
        "AWS: collected Glue job Name, Role, Command.ScriptLocation and code argument names; source s3:PutObject on that S3 object, target-role s3:GetObject on the same object, and source StartJobRun on that job with an unpinned --scriptLocation or an active scheduled trigger naming it without script redirects in job defaults or trigger arguments. Bucket policy, encryption and actual run remain conditional"),
    "appstream_new_app_block_builder_with_role": (("aws",), "source",
        "The source can create and start one app block builder with the target role and stream into it.",
        "AWS: complete builder and app-block name inventory, two available subnets in separate Availability Zones of one VPC, and CreateAppBlockBuilder, AssociateAppBlockBuilderAppBlock, StartAppBlockBuilder and CreateAppBlockBuilderStreamingURL on the same unused builder ARN; the associated APPSTREAM2 app block must be unassociated already, or be newly creatable with a regional S3 bucket"),
    "appstream_new_fleet_with_role": (("aws",), "source",
        "The source can create and start one fleet with the target role and stream through a stack.",
        "AWS: complete fleet, image and stack inventory in one Region; an AVAILABLE image that can run a fleet; CreateFleet authorized on the image and one unused fleet ARN; StartFleet, AssociateFleet and CreateStreamingURL on that same fleet; an existing stack or one creatable and associable by the source"),
    "appstream_new_image_builder_with_role": (("aws",), "source",
        "The source can create one unused image builder name from an available image and stream into it.",
        "AWS: complete image and image-builder inventory in one Region; an AVAILABLE image that supports image builders; CreateImageBuilder authorized on that image and one unused builder ARN; CreateImageBuilderStreamingURL authorized on the same builder ARN"),
    "appstream_existing_fleet_role_swap": (("aws",), "source",
        "The source can set the target role on one existing AppStream fleet and start a streaming session.",
        "AWS: a recorded stopped fleet, or a running fleet the source can stop; UpdateFleet, StartFleet and CreateStreamingURL on that same fleet ARN, plus an associated stack or permission to create and associate one new stack"),
    "appstream_existing_fleet_role_session": (("aws",), "source",
        "The source can open a desktop session on one running fleet that already has the target role.",
        "AWS: complete fleet inventory; the same running fleet has the exact target IamRoleArn, DESKTOP stream view, available capacity and a collected associated stack; CreateStreamingURL is authorized on that fleet ARN"),
    "appstream_existing_image_builder_role_session": (("aws",), "source",
        "The source can open a session on one running image builder that already has the target role.",
        "AWS: complete image-builder inventory; one RUNNING builder has the exact target IamRoleArn and CreateImageBuilderStreamingURL is authorized on that builder ARN"),
    "appstream_existing_app_block_builder_role_session": (("aws",), "source",
        "The source can open a session on one running app block builder that already has the target role.",
        "AWS: complete app-block-builder inventory; one RUNNING builder has the exact target IamRoleArn and CreateAppBlockBuilderStreamingURL is authorized on that builder ARN"),
    "emr_existing_cluster_step_instance_role": (("aws",), "source",
        "The source can add a command step to an active EMR cluster and use its EC2 instance role.",
        "AWS: complete EMR cluster and IAM role inventory; the same RUNNING or WAITING cluster records an instance profile attached to the exact target role; AddJobFlowSteps is authorized on that cluster ARN"),
    "appstream_existing_app_block_builder_role_swap": (("aws",), "source",
        "The source can set the target role on one existing AppStream app block builder and start a streaming session.",
        "AWS: a recorded stopped builder, or a running builder the source can stop; a recorded app block association; UpdateAppBlockBuilder, StartAppBlockBuilder and CreateAppBlockBuilderStreamingURL on the same builder ARN"),
    "codepipeline_new_s3_project_route": (("aws",), "source",
        "The source can create a pipeline and a CodeBuild project using the target role and start that pipeline.",
        "AWS: unused pipeline and project names in one Region; a versioned S3 source and artifact bucket, writable source ZIP key, readable source and artifacts, passable CodeBuild and CodePipeline roles, CreatePipeline and StartPipelineExecution on the same pipeline ARN, CreateProject and the pipeline role's StartBuild on the same project ARN"),
    "codepipeline_new_codecommit_project_route": (("aws",), "source",
        "The source can create a CodeCommit sourced pipeline and a CodeBuild project using the target role.",
        "AWS: an existing CodeCommit repository with a recorded branch or one the source can push, a pipeline role allowed to read and archive that repository, an accessible artifact bucket, unused pipeline and project names, passable service roles, and exact CreatePipeline, StartPipelineExecution, CreateProject and StartBuild permissions"),
    "codepipeline_new_ecr_project_route": (("aws",), "source",
        "The source can create an ECR sourced pipeline and a CodeBuild project using the target role.",
        "AWS: an existing ECR repository with a recorded tagged image that the pipeline role can describe, an accessible artifact bucket, unused pipeline and project names, passable service roles, and exact CreatePipeline, StartPipelineExecution, CreateProject and StartBuild permissions"),
    "codepipeline_existing_project_update_buildspec": (("aws",), "source",
        "The source can change a configured CodeBuild project's buildspec and start its pipeline.",
        "AWS: recorded source artifacts feed the CodeBuild action on the exact project without a buildspec override; the source can UpdateProject with inline buildspec and StartPipelineExecution on that pipeline; the pipeline role or action role can start the project, including batch and service-role override requirements"),
    "codebuild_existing_project_buildspec_override": (("aws",), "source",
        "The source can start an existing CodeBuild project with controlled build commands.",
        "AWS: a recorded CodeBuild project using the target role; StartBuild with inline buildspec on its ARN, or StartBuildBatch with inline buildspec and a recorded batch service role able to start child builds"),
    "codebuild_existing_project_update_buildspec": (("aws",), "source",
        "The source can change a recorded CodeBuild project's buildspec and start it with the target role.",
        "AWS: codebuild_project detail with the target service role; UpdateProject with a controlled buildspec and StartBuild on the same ARN, or StartBuildBatch with an existing batch role able to start child builds"),
    "codebuild_running_sandbox_command": (("aws",), "source",
        "The source can run a command in a recorded running CodeBuild sandbox using the target role.",
        "AWS: codebuild_sandbox inventory with a RUN_SANDBOX record, exact sandbox ARN and serviceRole; effective codebuild:StartCommandExecution on that ARN"),
    "codebuild_running_sandbox_connection": (("aws",), "source",
        "The source can connect to a recorded running CodeBuild sandbox using the target role.",
        "AWS: codebuild_sandbox inventory with a RUN_SANDBOX record, exact sandbox ARN and serviceRole; effective codebuild:StartSandboxConnection on that ARN"),
    "codebuild_new_project_role_and_build": (("aws",), "source",
        "The source can create and run one unused CodeBuild project name with the target role.",
        "AWS: complete codebuild_project name inventory in a Region; CreateProject and StartBuild or StartBuildBatch on one unused project ARN, with codebuild:serviceRole set to the target and an inline buildspec allowed at creation or build start; batch mode may use a distinct passable role able to start child builds"),
    "codebuild_existing_project_role_and_build": (("aws",), "source",
        "The source can change and run the same recorded CodeBuild project using controlled build commands.",
        "AWS: codebuild_project inventory with a project ARN; codebuild:UpdateProject and StartBuild or StartBuildBatch on that ARN; an inline buildspec allowed either in UpdateProject or at build start; batch mode needs a configured or creatable batch role able to start child builds"),
    "cloudfront_edge_distribution_and_service_roles": (("aws",), "source",
        "The source can update a recorded CloudFront distribution and the required Lambda@Edge service-linked roles exist or can be created.",
        "AWS: cloudfront_distribution inventory with an ARN covered by cloudfront:UpdateDistribution; IAM role inventory for AWSServiceRoleForLambdaReplicator and AWSServiceRoleForCloudFrontLogger, or iam:CreateServiceLinkedRole with the appropriate iam:AWSServiceName"),
    "lambda_microvm_shell_runnable_image_and_role": (("aws",), "source",
        "The MicroVM role allows Lambda session tagging and one runnable image is covered by run and shell-token grants.",
        "AWS: IAM trust grants sts:TagSession to lambda.amazonaws.com; lambda_microvm_image in CREATED or UPDATED state with latestActiveImageVersion; RunMicrovm and CreateMicrovmShellAuthToken on the same image ARN"),
    "lambda_existing_zip_function_direct_invoke_ready": (("aws",), "source",
        "The source can update and invoke one existing ZIP function using the target role.",
        "AWS: a collected active ZIP function has a supported runtime, completed its prior update, available concurrency, and no enforced code signing; UpdateFunctionCode and InvokeFunction cover its exact ARN"),
    "lambda_existing_zip_function_role_swap_ready": (("aws",), "source",
        "The source can repoint, replace code in, and invoke one existing ZIP function using the target role.",
        "AWS: one collected active ZIP function has a supported runtime, completed its prior update, available concurrency, and no enforced code signing; UpdateFunctionConfiguration, UpdateFunctionCode, and InvokeFunction cover that ARN, and PassRole permits the target role for that function"),
    "lambda_policy_rewrite_zip_code_and_invoke_ready": (("aws",), "source",
        "The source can replace one ZIP function policy to grant itself code update and invocation.",
        "AWS: one collected active ZIP function uses the target role, can run new unsigned code, and the source can rewrite its policy with a direct same-account grant that is not blocked by explicit denies or organization limits"),
    "lambda_enforced_zip_function_signing_bypass_and_invoke": (("aws",), "source",
        "The source can bypass enforced code signing, update, and invoke one existing ZIP function.",
        "AWS: the exact active function has enforced signing, supported runtime, completed update, and free concurrency; UpdateFunctionCode and InvokeFunction cover it, and DeleteFunctionCodeSigningConfig covers its ARN or Put/Update covers a collected code signing config ARN"),
    "agentcore_new_interpreter_broad_name_and_role_ready": (("aws",), "source",
        "The source can choose a fresh interpreter name and run code under a passed role.",
        "AWS: CreateCodeInterpreter is allowed in one Region; StartCodeInterpreterSession and InvokeCodeInterpreter cover every generated suffix for a freely chosen name, and the role trusts AgentCore"),
    "eks_existing_self_access_entry_can_receive_cluster_admin": (("aws",), "source",
        "The source can give its own existing STANDARD EKS access entry cluster-wide administrator access.",
        "AWS: collected eks_access_entry with principalArn equal to the source and type STANDARD; exact accessEntryArn; AssociatedAccessPolicies without an existing cluster-wide AmazonEKSClusterAdminPolicy; AssociateAccessPolicy on that ARN with the administrator policy and cluster scope"),
    "eks_new_self_access_entry_can_receive_cluster_admin": (("aws",), "source",
        "The source can create an access entry for its own IAM principal and give that entry cluster-wide administrator access.",
        "AWS: eks_access_entry inventory for the cluster; CreateAccessEntry with eks:principalArn set to the source and type STANDARD; AssociateAccessPolicy on the resulting access-entry ARN with AmazonEKSClusterAdminPolicy and cluster scope"),
    "eventbridge_subscriber_has_active_bus_and_bound_permissions": (("aws",), "source",
        "The source can create a subscriber on an active custom event bus with a passed role.",
        "AWS: recorded eventbridge_custom_bus EventBusArn and usable State (ACTIVE or UPDATE_FAILED), no unverified customer KMS key, events:CreateSubscriber on that bus and a new subscriber ARN, and events:PutEvents on the same bus"),
    "mwaa_existing_environment_update_with_dag_code": (("aws",), "source",
        "The source can update one usable MWAA environment to use the target role and upload a DAG that the role can read.",
        "AWS: collected mwaa_environment ARN, AVAILABLE or UPDATE_FAILED status, SourceBucketArn and DagS3Path; exact airflow:UpdateEnvironment and s3:PutObject for one new DAG, plus target role s3:ListBucket and s3:GetObject for that DAG"),
    "mwaa_existing_dag_object_execution_role": (("aws",), "source",
        "The source can upload a Python DAG to an existing MWAA environment and have it parsed under that environment's exact execution role.",
        "AWS: collected AVAILABLE mwaa_environment ARN, ExecutionRoleArn, SourceBucketArn and DagS3Path; exact s3:PutObject on a Python object in that DAG folder, plus the attached role's s3:ListBucket and s3:GetObject for the same object"),
    "mwaa_serverless_new_workflow_definition_and_start": (("aws",), "source",
        "The source can create a new workflow from a controlled S3 definition and start that exact workflow under the target role.",
        "AWS: complete workflow inventory and free name; same-Region versioned, private owned S3 bucket plus source Put/Get/List for a new YAML object; broad StartWorkflowRun covering generated workflow IDs, exact PassRole with iam:PassedToService=airflow-serverless.amazonaws.com, and required logging and service-linked-role permissions"),
    "m2_existing_environment_new_application_deploy": (("aws",), "source",
        "The source can create an M2 application with the target role, deploy it to an available environment, and start it.",
        "AWS: collected mainframe_environment in Available state; CreateDeployment on that exact environment and all new application IDs, StartApplication on all new application IDs, CreateApplication, PassRole with iam:PassedToService=m2.amazonaws.com, and source write/read access to one owned S3 definition object"),
    "mgh_automation_unit_home_region_target_and_run": (("aws",), "source",
        "The source can create a custom Migration Hub automation unit, attach the target role, and run a controlled target.",
        "AWS: Migration Hub home Region us-east-1 and feature access; a source-controlled runnable SSM document or Lambda function; the new automation-unit ARN authorized for AssociateAutomationUnitRole; CreateAutomationRun; PassRole to migrationhub.amazonaws.com; target role trust and target invocation permissions"),
    "migrationhub_orchestrator_bound_workflow_script_and_managed_target": (("aws",), "source",
        "The source can add or update a runnable automated workflow step that sends a controlled script to an online SSM-managed instance carrying the target role.",
        "AWS: collected Orchestrator workflow and step group/graph with same-workflow action grants; target EC2 instance selected by that workflow and online in SSM; service-linked role and usable migrationhub-orchestrator-* S3 script object the source can write; startable or retryable workflow state"),
    "ssm_incident_response_plan_runs_new_automation_document": (("aws",), "source",
        "The source can create an Automation document and start an incident under a response plan that names it and the target role.",
        "AWS: ssmincidents_account active ReplicationSets or existing ResponsePlans; ssm_document_metadata and CreateDocument; CreateResponsePlan or UpdateResponsePlan plus StartIncident on the same plan ARN"),
    "cloudformation_service_managed_stackset_targetable": (("aws",), "source",
        "Organizations access is enabled and the source can deploy a new service-managed StackSet to the member account's OU.",
        "AWS: cloudformation_organizations_access Status=ENABLED; organization_parent member OU; CreateStackSet and CreateStackInstances on one generated StackSet, OU target, and IAM role resource type"),
    "cloudformation_extension_package_and_invocation": (("aws",), "source",
        "The source can upload and read one handler package and invoke its registered private resource type.",
        "AWS: recorded S3 bucket; s3:PutObject and GetObject on the same package object; cloudformation:CreateResource or CreateStack/UpdateStack on a usable stack"),
    "cloudformation_new_stack_with_role": (("aws",), "source",
        "The source can create a new stack with a caller-controlled inline template and the target service role.",
        "AWS: cloudformation:CreateStack on one unused stack name across generated stack IDs, with cloudformation:RoleArn set to the target role"),
    "cloudformation_new_changeset_with_role": (("aws",), "source",
        "The source can create and execute a CREATE-type change set on the same new stack using the target service role.",
        "AWS: cloudformation:CreateChangeSet and ExecuteChangeSet on one unused stack name across generated stack IDs, with cloudformation:RoleArn set to the target role"),
    "cloudformation_existing_stack_updatable_with_role": (("aws",), "source",
        "An existing stack in an updatable state can be changed with the target CloudFormation service role.",
        "AWS: cloudformation_stack {StackId, StackStatus} by Region; exact cloudformation:UpdateStack permission on the stack ARN with cloudformation:RoleArn set to the target role"),
    "cloudformation_attached_role_stack_updatable": (("aws",), "source",
        "An existing updatable stack already carries the target service role and the source can update that stack.",
        "AWS: cloudformation_stack {StackId, StackStatus, RoleARN} by Region; exact cloudformation:UpdateStack permission on that StackId"),
    "cloudformation_attached_role_changeset_executable": (("aws",), "source",
        "An existing updatable stack already carries the target service role and the source can create and execute a change set on that stack.",
        "AWS: cloudformation_stack {StackId, StackStatus, RoleARN} by Region; exact cloudformation:CreateChangeSet and ExecuteChangeSet permissions on the same StackId"),
    "ssm_shell_document_on_online_instance": (("aws",), "source",
        "The source can use a shell-capable Run Command document on the same online instance carrying the target role.",
        "AWS: ssm:SendCommand on an online EC2 instance and AWS-RunShellScript or AWS-RunPowerShellScript in its Region"),
    "ssm_shell_session_on_online_instance": (("aws",), "source",
        "The source can open the default shell session document and data channel on the same online instance carrying the target role.",
        "AWS: ssm:StartSession on an online EC2 instance and its SSM-SessionManagerRunShell document, plus ssmmessages:OpenDataChannel"),
    "ssm_hybrid_sendcommand_role": (("aws",), "source",
        "The source can send a shell command to an online hybrid managed node carrying the exact target service role.",
        "AWS: collected online mi- managed node with IamRole equal to the target role name; source ssm:SendCommand on its managed-instance ARN and the platform-matching AWS shell document"),
    "ssm_hybrid_startsession_role": (("aws",), "source",
        "The source can open an interactive shell on an online hybrid managed node carrying the exact target service role.",
        "AWS: collected online mi- managed node with IamRole equal to the target role name; source ssm:StartSession on its managed-instance ARN and SSM-SessionManagerRunShell document, plus future ssmmessages:OpenDataChannel"),
    "ssm_shell_association_targets": (("aws",), "source",
        "The source can create an association for a shell-capable document in the Region of an online target instance.",
        "AWS: ssm:CreateAssociation on a new association ARN and AWS-RunShellScript or AWS-RunPowerShellScript document in the instance Region; Targets can name its InstanceIds value"),
    "ssm_maintenance_window_run_command_target": (("aws",), "source",
        "An enabled maintenance window can schedule a Run Command task for an online instance carrying the target role.",
        "AWS: ssm_maintenance_window {WindowId, Enabled, NextExecutionTime, Tasks} in the instance Region; exact RegisterTaskWithMaintenanceWindow permission on the window or UpdateMaintenanceWindowTask permission on the window and an existing RUN_COMMAND task"),
    "ssm_maintenance_window_automation_task_ready": (("aws",), "source",
        "An enabled maintenance window can schedule a newly created Automation document under the target service role.",
        "AWS: ssm_maintenance_window {WindowId, Enabled, NextExecutionTime, Tasks}; exact RegisterTaskWithMaintenanceWindow permission on the window or UpdateMaintenanceWindowTask permission on the window and an existing AUTOMATION task; CreateDocument on a new Automation document in that Region"),
    "ssm_jit_approved_online_instance": (("aws",), "source",
        "The assumed source role can request a token for the exact online instance, and its access is approved.",
        "AWS: ssm:StartAccessRequest on arn:...:ec2:Region:Account:instance/InstanceId, source kind aws_role, online ssm_managed_instance, and a proven auto-approval policy or current approved access request for this role and instance"),
    "ssm_new_automation_document_executable": (("aws",), "source",
        "The source can create an Automation document and start that same document in one Region.",
        "AWS: ssm:CreateDocument with ssm:DocumentType Automation on a new document ARN, ssm:StartAutomationExecution on the same document ARN and generated automation-execution ARN, plus ssm_document_metadata for exact-name collisions"),
    "target_codecommit_git_permission": (("aws",), "target",
        "The IAM user has a recorded CodeCommit Git permission that an uploaded SSH key could exercise.",
        "AWS: target IAM user identity and inherited policies granting codecommit:GitPull or codecommit:GitPush"),
    "target_ssh_public_key_capacity": (("aws",), "source",
        "The target IAM user has room for another SSH public key, or the source can delete an existing key after listing its ID.",
        "AWS: iam_user SSHPublicKeys list and the source's effective iam:DeleteSSHPublicKey and iam:ListSSHPublicKeys permissions on the target user"),
    "service_specific_credential_ready": (("aws",), "source",
        "The target IAM user has room for a supported service credential or an active credential the source can reset.",
        "AWS: iam_user ServiceSpecificCredentials and service-scoped CreateServiceSpecificCredential or ResetServiceSpecificCredential permission"),
    "mfa_enrollment_credential_ready": (("aws",), "source",
        "The target IAM user can accept another MFA device and at least one credential action can supply usable credentials.",
        "AWS: IAM user MFADevices, AccessKeys, LoginProfile, and effective credential and MFA-device permissions"),
    "mfa_removal_password_ready": (("aws",), "source",
        "The target IAM user has an MFA device to remove and a password action matching its login-profile state.",
        "AWS: IAM user MFADevices, LoginProfile, and effective CreateLoginProfile or UpdateLoginProfile permission"),
    "target_console_login_without_mfa": (("aws",), "target",
        "The target IAM user has no MFA device that would prevent password-only console sign-in.",
        "AWS: iam_user MFADevices list for the exact target user"),
    "role_trust_rewrite_assumable": (("aws",), "source",
        "The role is editable and the source can assume it after naming itself in the trust policy.",
        "AWS: role path, source sts:AssumeRole explicit denies, permissions boundary, and applicable SCPs"),
    "group_adds_policy_to_source": (("aws",), "source",
        "Joining the group gives the source user a newly usable action on a resource.",
        "AWS: exact group membership and policies, the source user's effective action/resource access before and after joining, and applicable permissions boundary and SCP"),
    "source_attached_admin_policy_version_exists": (("aws",), "source",
        "An attached customer-managed policy has a nondefault version that clearly grants full account permissions.",
        "AWS: attached customer-managed policy versions with their documents and effective iam:SetDefaultPolicyVersion permission"),
    "source_attached_policy_version_capacity": (("aws",), "source",
        "An attached customer-managed policy can receive a new version, or the source can delete a nondefault version first.",
        "AWS: attached customer-managed policy versions and effective iam:DeletePolicyVersion permission when five versions exist"),
    "assumable_role_allows_account_admin": (("aws",), "source",
        "A role the source can assume and modify can gain full account permissions without a restrictive permissions boundary.",
        "AWS: exact assumable role, IAM policy mutation permission on that role, and the role's permissions boundary document"),
    "source_boundary_allows_account_admin": (("aws",), "source",
        "The source identity's permissions boundary permits full account administration after the policy change, or the source can remove that boundary.",
        "AWS: iam_role/iam_user PermissionsBoundary, its managed policy document, and effective permission to remove the boundary"),
    "lambda_enforcing_code_signing": (("aws",), "target",
        "A Lambda function attached to the target role has a code-signing configuration that enforces trusted artifacts.",
        "AWS: lambda_function CodeSigning and matching CodeSigningConfig details for the function"),
    "iam_user_access_key_capacity": (("aws",), "source",
        "The target IAM user has room for another access key, or the source can delete one of its existing keys first.",
        "AWS: iam_user AccessKeys list and the source's effective iam:DeleteAccessKey and iam:ListAccessKeys permissions on the target user"),
    "ec2_instance_running": (("aws",), "target",
        "The target role is attached (instance profile) to at least one EC2 instance in state pending/running.",
        "AWS: instance {InstanceId, State, IamInstanceProfile} in every region + iam_role InstanceProfileList"),
    "ec2_instance_connect_same_running_role_host": (("aws",), "source",
        "The source can push a key to the same running Linux instance that carries the target role, with instance metadata enabled.",
        "AWS: exact instance attachment, running state, platform, MetadataOptions, and SendSSHPublicKey permission"),
    "ssm_managed_instance": (("aws",), "target",
        "At least one running EC2 instance of the target role is registered with Systems Manager (PingStatus Online).",
        "AWS: ssm_managed_instance (ssm:DescribeInstanceInformation {InstanceId, PingStatus}) in every region + instance"),
    "ecs_container_instance_exists": (("aws",), "target",
        "An ECS cluster in the target's account has registered EC2 container instances (StartTask needs a host).",
        "AWS: ecs_cluster with describe_clusters {registeredContainerInstancesCount} in every region"),
    "ecs_task_definition_exists": (("aws",), "target",
        "At least one ECS task definition exists in the target's account (the technique overrides an existing one).",
        "AWS: ecs_task_definition in every region"),
    "ecs_existing_task_override_runnable_with_role": (("aws",), "source",
        "One active EC2 task definition with a container can run in an active cluster with capacity, using the target task role override.",
        "AWS: described ECS task definition and cluster, exact ecs:RunTask grant, and iam:PassRole on its execution role if present"),
    "eks_cluster_exists": (("aws",), "target",
        "At least one EKS cluster exists in the target's account (the technique attaches to an existing cluster).",
        "AWS: eks_cluster (eks:ListClusters) in every region"),
    "source_in_org_management_account": (("aws",), "source",
        "The source lives in the organization management account (only it can call the API).",
        "AWS: organization_account Arn (organizations:ListAccounts) to identify the management account"),
    "emr_containers_job_route": (("aws",), "source",
        "One running EMR on EKS virtual cluster allows this source to start a job with the target role.",
        "AWS: emr_container_virtual_cluster and exact StartJobRun authorization with ExecutionRoleArn context"),
    "emr_serverless_job_route": (("aws",), "source",
        "One runnable EMR Serverless application can use the target role to read a script the source can write.",
        "AWS: described EMR Serverless application, exact StartJobRun and PassRole grants, and a same-Region S3 object writable by source and readable by target"),
    "emr_containers_pod_identity_job_route": (("aws",), "source",
        "One running EMR on EKS virtual cluster has all three EKS Pod Identity associations for the target role and permits this source to submit a job.",
        "AWS: virtual cluster, EKS cluster, complete pod identity associations, exact PassRole and StartJobRun authorization"),
    "emr_cluster_session_runtime_role": (("aws",), "source",
        "The source can request session credentials for the target runtime role on one live EMR cluster with runtime roles enabled.",
        "AWS: described EMR cluster, matching security configuration, instance profile and role trust, exact GetClusterSessionCredentials grant"),
    "emr_containers_endpoint_route": (("aws",), "source",
        "One active EMR on EKS endpoint in a running virtual cluster allows this source to request a session with the target role.",
        "AWS: emr_container_virtual_cluster, emr_container_endpoint, and exact GetManagedEndpointSessionCredentials authorization"),
    "rolesanywhere_anchor_profile_trust_join": (("aws",), "source",
        "The source can update an enabled trust anchor in the same Region as an enabled profile listing the target role, and the role trust admits that exact anchor.",
        "AWS: rolesanywhere_trust_anchor, rolesanywhere_profile, target role trust policy, and effective rolesanywhere:UpdateTrustAnchor"),
    "rolesanywhere_new_anchor_profile_role_ready": (("aws",), "source",
        "The source can create an enabled trust anchor and profile in one Region, pass the target role, and satisfy the role's Roles Anywhere trust.",
        "AWS: exact source CreateTrustAnchor, CreateProfile, iam:PassRole, target role trust policy, and regional trust anchor/profile inventory"),
    "sagemaker_job_execution_route_unverified": (("aws",), "source",
        "A SageMaker job needs a runnable source-controlled image and a feasible input/output path under the passed role before a role execution path is reported.",
        "AWS: exact SageMaker job ARN, image metadata, target role image/data permissions, and effective job creation and PassRole permissions"),
    "target_in_other_account": (("aws",), "source",
        "The target lives in a different account than the source (cross-account technique).",
        "AWS: target and source account ids (always known)"),
    "k8s_eks_cluster": (("k8s",), "target",
        "The target's cluster is an Amazon EKS cluster (node spec.providerID aws://, EKS API groups or a kube-system/aws-auth ConfigMap).",
        "K8s: node spec.providerID, api_discovery groups, configmap_metadata in kube-system"),
    "k8s_openshift_cluster": (("k8s",), "target",
        "The target's cluster is OpenShift (api_discovery lists *.openshift.io API groups such as security.openshift.io).",
        "K8s: api_discovery (server API groups)"),
}
FACTS_NEEDED.update({f"precondition:{pid}": spec[3] for pid, spec in PRECONDITIONS.items()})
SCOPES =("same_account", "same_project", "inherited_scope", "same_namespace", "cluster", "tenant", "org", "any")
CONFIDENCES = ("derived", "conditional", "unknown")
SEVERITIES = ("critical", "high", "medium", "low", "info")
REQUIREMENT_FIELDS = {
    "aws": {"action", "resource", "notes", "bind", "request_context"},
    "gcp": {"action", "permission", "resource", "notes", "bind"},
    "azure": {"action", "data_action", "scope", "entra_permission", "entra_role", "directory_scope", "graph_app_permission",
              "entra_owner_of", "object_type", "entra_pim_eligible_role", "entra_tenant_setting", "notes", "bind",
              "entra_group_member", "fabric_workspace_role", "fabric_workspace", "intune_permission", "entra_catalog_role",
              "catalog"},
    "k8s": {"verb", "verb_prefix", "resource", "resource_match", "subresource", "api_group", "namespace", "resource_name",
            "notes", "bind"},
}
# K8s requirement `resource_match: any`: any resource (any API group unless api_group is given) the rule names
# satisfies the requirement. With `verb_prefix` it expresses KEP-5284 constrained impersonation
# (verbs impersonate-on:<mode>:<verb> on the impersonated request's resource).
K8S_RESOURCE_MATCH = ("any",)
# ---- schema extensions (v1.1, backward compatible; see docs/peaso-privesc-schema.md "Extensions") ----------------
# Nested boolean requirement groups: an item of all_of / an any_of group may be {all_of: [...]} or {any_of: [...]}.
GROUP_KEYS = ("all_of", "any_of")
MAX_GROUP_DEPTH = 4
MAX_ALTERNATIVES = 64       # DNF expansion cap (alternatives evaluated per entry)
# request_context (AWS): condition-key values the technique's own API request carries (machine-checked against
# Allow/Deny Condition blocks of identity policies, boundaries, SCPs/RCPs and resource policies).
REQUEST_CONTEXT_PROVIDERS = ("aws",)
REQUEST_CONTEXT_SPECIAL = ("absent", "chosen", "values", "admin_managed_policy", "source_principal")
MAX_CONTEXT_CHOICES = 16
_BIND = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
SECRET_PROVIDERS = ("aws", "gcp", "azure", "any")
_LABEL_SEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*(=[A-Za-z0-9._-]*)?$")


def as_str_list(value):
    return [value] if isinstance(value, str) else list(value) if isinstance(value, list) else []
_CONTEXT_KEY = re.compile(r"^[A-Za-z0-9-]+:[A-Za-z0-9_./*-]+$")
# target.outcome: what the source obtains. Defaults (when omitted) are inferred from the target kind.
OUTCOMES = {
    "identity": "Becomes the target principal (mechanism unspecified).",
    "credentials": "Obtains credentials / tokens / a session of the target principal (keys, passwords, tokens, AssumeRole).",
    "workload_execution": "Runs code inside a workload that carries the target identity (passed role, attached SA/MI).",
    "impersonation": "Acts as the target through a delegation/impersonation API without holding its credentials.",
    "membership": "Becomes a member of the target group and inherits its grants.",
    "permission_grant": "The source's own permissions grow (policy/role edit or assignment); target is self or an entity.",
    "role_activation": "Activates/assigns a privileged role or permission set (PIM, Identity Center, Entra directory role).",
    "scope_control": "Gains IAM control of a scope (set IAM policy / role assignments) -> every principal of the scope.",
    "application_admin": "Becomes administrator of a managed service's own application plane (not an IAM principal).",
    "bounded_authority": "Evidence-bound effect on the exact non-principal target, defined only by the rule and verified facts; implies no IAM scope control, application administration, principal access, or further permissions.",
    "blocker_removal": "Lifts an enforcement control (target.removes_blockers) that gates other techniques; reaches no principal.",
}
ENTITY_OUTCOMES = ("permission_grant", "role_activation", "scope_control", "application_admin", "bounded_authority", "blocker_removal")
GROUP_TARGET_KINDS = {"aws_group", "gcp_group", "entra_group", "k8s_group"}
GENERIC_SELECTORS = {"target_id_glob", "target_name_glob", "exclude_target_id_glob"}
GENERIC_SOURCE_SELECTORS = {"source_id_glob"}
# Source selectors evaluated by the evaluator after every technique (graph closure), not by the provider model.
CHAIN_SOURCE_SELECTORS = {"source_reaches_kind"}
AZURE_REQUIREMENT_KINDS = ("action", "entra_permission", "entra_role", "graph_app_permission", "entra_owner_of",
                           "entra_pim_eligible_role", "entra_tenant_setting", "entra_group_member", "fabric_workspace_role",
                           "intune_permission", "entra_catalog_role")
ENTRA_TENANT_SETTINGS = ("guest_invites_allowed_for_source",)
# Fabric workspace roles, strongest first (a held role satisfies every weaker one).
FABRIC_WORKSPACE_ROLES = ("Admin", "Member", "Contributor", "Viewer")
# azure_host_linked_to_pivot values and azure_consumer_of_pivot binding kinds.
AZURE_HOST_LINKS = ("avd_session_host", "automation_hybrid_worker", "devtest_lab_compute_vm", "service_fabric_node_vmss")
AZURE_CONSUMER_BINDINGS = ("key_vault_reference", "storage_content", "app_configuration_reference", "queue_trigger",
                           "service_bus_trigger", "event_subscription")
PIM_GROUP_ACCESS = ("member", "owner")
# Selectors valid only on these target kinds (Azure extensions).
AZURE_SELECTOR_KINDS = {
    "azure_containerapp_create_uami_path": ("azure_managed_identity",),
    "azure_containerapp_exec_identity": ("azure_managed_identity",),
    "azure_containerapp_job_assignable_uami": ("azure_managed_identity",),
    "azure_containerapp_assignable_uami": ("azure_managed_identity",),
    "azure_confidential_ledger_admin_path": ("azure_dataplane_admin",),
    "azure_batch_shared_key_pool_identity": ("azure_managed_identity",),
    "azure_batch_pool_starttask_identity": ("azure_managed_identity",),
    "azure_batch_pool_assignable_uami": ("azure_managed_identity",),
    "azure_aci_assignable_uami": ("azure_managed_identity",),
    "azure_aci_exec_running_identity": ("azure_managed_identity",),
    "azure_aci_existing_write_identity": ("azure_managed_identity",),
    "azure_apim_restorable_backup": ("azure_managed_identity",),
    "azure_consumer_of_pivot": ("azure_managed_identity",),
    "azure_assignable_via_identity_holding": ("azure_managed_identity",),
    "azure_users_assigned_to_pivot": ("azure_user",),
    "attached_to_vm_joined_to_entra_domain_services": ("azure_managed_identity",),
    "azure_assignment_condition_uses_principal_attribute": ("azure_scope_owner", "azure_dataplane_admin"),
    "fabric_workspace_identity": ("azure_service_principal",),
    "entra_pim_group_eligible_for_source": ("entra_group",),
    "entra_resource_in_catalog": ("entra_group", "azure_service_principal", "entra_role"),
    "entra_access_package_auto_assignment_open_to_guest": ("entra_group", "azure_service_principal", "entra_role"),
    "intune_managed_device_user": ("azure_user",),
}
PLACEHOLDERS = {
    "target.resource", "target.policy_resource",
    "target.arn", "target.email", "target.id", "target.scope", "target.quota_project", "target.namespace", "target.name", "target.account", "target.region",
    "target.role_arn", "target.location_arn", "target.grant_arn",
    "target.project", "target.node", "target.client_id", "target.application_id",
    "target.resource_arn", "target.attached_resource_arn", "target.artifact_arn", "target.consumer_input_arn",
    "target.saml_provider_arn", "target.trust_anchor_arn", "target.oidc_provider_arn", "target.portfolio_arn",
    "target.rolesanywhere_profile_arn", "target.codebuild_sandbox_arn", "target.codebuild_running_sandbox_arn", "target.redshift_dbuser_arn",
    "target.amplifybackend_token_arn", "target.amplifybackend_backend_arn",
    "target.host_resource", "target.apim_api_resource", "target.apim_api_policy_resource",
    "target.apim_operation_policy_resource", "target.apim_product_policy_resource",
    "target.host_resource.content_storage", "target.composer_dag_managed_folder", "target.dataproc_init_managed_folder", "target.dataproc_init_object", "target.cloudbuild_source_object", "target.host_resource.workspace", "target.catalog",
    "target.domain_registration", "target.image_family_project",
    "source", "source.account", "source.partition", "source.arn", "source.id", "source.email", "source.namespace", "source.name",
    "source.scope", "source.attached_policy_arn", "source.group_arn", "source.assumable_role_arn",
    "source.assumable_role_attached_policy_arn",
    "source.controlled_user", "target.user",
    "pivot", "pivot.namespace",
    "account", "project", "scope", "namespace", "cluster",
    "admin_equivalent_clusterrole", "source_bound_clusterrole", "source_bound_role", "source_rolebound_clusterrole", "host_scc",
}
ENTRY_FIELDS = {"id", "provider", "service", "title", "source", "source_revision", "summary", "requires", "target",
                "conditions", "blockers", "confidence", "severity", "mitigation", "references", "notes",
                "pivot_resource_type", "source_kind", "source_selector", "preconditions"}
REQUIRED_FIELDS = ("id", "provider", "service", "title", "source", "summary", "requires", "target", "severity", "mitigation")
# Blockers the evaluator evaluates from snapshot facts; every other known blocker is reported
# in finding evidence as `blockers_not_evaluated` (it never silently removes or downgrades an edge).
# Blockers a provider model evaluates from optional snapshot facts (listed as not evaluated when the facts are absent).
MODEL_BLOCKERS = {"aws": {"ecr_tag_immutability", "lambda_code_signing_enforced"},
                  "gcp": {"org_policy_constraint", "vpc_sc_perimeter"},
                  "azure": {"aks_local_accounts_disabled", "aks_local_accounts_enabled", "aks_entra_integration_enabled", "aks_run_command_disabled"},
                  # Workload-admission blockers of techniques that create / patch pods (peaso.privesc.effective_permissions.k8s):
                  # 'blocked' only for definitive facts (PSA enforce label), 'possibly_blocked' (edge kept, conditional) for
                  # enforcing policies whose effect cannot be decided offline (CEL policies, webhooks, Kyverno, Gatekeeper).
                  "k8s": {"pod_security_admission", "pivot_namespace_psa_enforce_baseline_or_restricted", "admission_policy",
                          "admission_webhook", "kyverno_policy", "gatekeeper_constraint"}}
# A technique lifting the key blocker (target.removes_blockers) also lifts its aliases.
BLOCKER_ALIASES = {"pod_security_admission": {"pivot_namespace_psa_enforce_baseline_or_restricted"},
                   "pivot_namespace_psa_enforce_baseline_or_restricted": {"pod_security_admission"}}
# Placeholders that resolve on entity targets (account admin, scope owner, cluster-admin, ...). Any other
# {target.*} placeholder on an entity target can never resolve and would silently make every edge unknown.
ENTITY_TARGET_PLACEHOLDERS = {
    "gcp_verified_authority": {"target.scope", "target.resource", "target.policy_resource", "target.host_resource", "target.artifact_arn", "target.quota_project"},
    "aws_verified_authority": {"target.scope", "target.account", "target.resource_arn", "target.arn", "target.role_arn", "target.location_arn", "target.grant_arn"},
    "aws_account_admin": {"target.scope", "target.account"},
    "aws_identity_center_permission_set": {"target.scope", "target.account", "target.arn", "target.id"},
    "gcp_scope_owner": {"target.scope", "target.project", "target.id", "target.name"},
    "azure_scope_owner": {"target.scope"},
    "azure_dataplane_admin": {"target.scope"},
    "k8s_cluster_admin": {"target.scope", "target.cluster", "target.account", "target.name"},
    "k8s_verified_authority": {"target.scope", "target.namespace"},
    "aws_directory_domain_admin": {"target.scope", "target.account"},
    "aws_service_plane_admin": {"target.scope", "target.account", "target.region", "target.resource_arn", "target.arn",
                                "target.amplifybackend_token_arn", "target.amplifybackend_backend_arn"},
    "k8s_admission_control": {"target.scope", "target.cluster"},
    "entra_role": {"target.scope", "target.id", "target.name", "target.catalog"},
}
ENTITY_KINDS = {k for k, (_, role) in TARGET_KINDS.items() if role == "entity"}
EVALUATED_BLOCKERS = {"scp_or_boundary_deny", "scp_deny", "permission_boundary", "explicit_deny", "deny_policy",
                      "gcp_deny_policy", "azure_deny_assignment"}
KNOWN_BLOCKERS = EVALUATED_BLOCKERS | {
    "abac_condition", "restricted_management_au", "role_assignable_group_member_or_owner",
    "sp_lock_configuration_credentials", "ecr_tag_immutability", "lambda_code_signing_enforced",
    "scm_and_ftp_basic_auth_disabled", "service_principal_conditional_access_block", "glue_nonoverridable_arguments",
    "role_assignment_condition_is_allowlist", "pim_approval_required_by_other_principal",
    "target_upn_on_initial_onmicrosoft_domain", "aks_local_accounts_disabled", "aks_local_accounts_enabled", "aks_entra_integration_enabled", "aks_run_command_disabled",
    "pivot_namespace_psa_enforce_baseline_or_restricted", "vpc_sc_perimeter", "org_policy_constraint",
    "pod_security_admission", "admission_policy",
    # K8s admission enforcement lifted by k8s_admission_control techniques (target.removes_blockers).
    "admission_webhook", "kyverno_policy", "gatekeeper_constraint",
    # Azure / Entra approval controls (reported as not evaluated).
    "intune_multi_admin_approval_required", "access_package_approval_by_other_principal",
}
_ID = re.compile(r"^(aws|gcp|azure|k8s|entra)-[a-z0-9]+(?:-[a-z0-9]+)*$")
_PLACEHOLDER = re.compile(r"(?<!\$)\{([^{}]+)\}")
# Execution content is forbidden: entries describe preconditions, not steps.
_COMMANDS = re.compile(r"(^|\s)(aws|gcloud|az|kubectl|curl|wget|python3?|bash)\s+[a-z-]+\s+[a-z-]+", re.I)


@functools.lru_cache(maxsize=None)
def checkout_revision(root):
    """Commit sha of a hacktricks-cloud git checkout (read from .git, no git binary), or None."""
    git = Path(root) / ".git"
    try:
        head = (git / "HEAD").read_text().strip()
        if not head.startswith("ref:"):
            return head or None
        ref = head.split(":", 1)[1].strip()
        if (git / ref).is_file():
            return (git / ref).read_text().strip() or None
        for line in (git / "packed-refs").read_text().splitlines():
            if line.endswith(" " + ref):
                return line.split(" ", 1)[0]
    except OSError:
        return None
    return None


def revision_matches(entry_revision, checkout_rev):
    """True unless both revisions are known and differ (abbreviated shas compare by prefix)."""
    if not entry_revision or not checkout_rev:
        return True
    a, b = str(entry_revision).lower(), str(checkout_rev).lower()
    return a.startswith(b) or b.startswith(a)


class CatalogError(ValueError):
    pass


def _placeholders(value):
    return set(_PLACEHOLDER.findall(value)) if isinstance(value, str) else set()


def is_group(item):
    """True for a nested boolean node {all_of: [...]} / {any_of: [...]} (optionally with notes)."""
    return isinstance(item, dict) and len(set(item) & set(GROUP_KEYS)) == 1 and not set(item) - set(GROUP_KEYS) - {"notes"}

def _leaves(item):
    if is_group(item):
        key = "all_of" if "all_of" in item else "any_of"
        for child in item.get(key) or []:
            yield from _leaves(child)
    elif isinstance(item, list):
        for child in item:
            yield from _leaves(child)
    elif isinstance(item, dict):
        yield item

def flatten_requirements(requires):
    """Every leaf requirement of an entry's requires (all_of, any_of groups and nested groups), in order."""
    if not isinstance(requires, dict):
        return []
    out = []
    if isinstance(requires.get("all_of"), list):
        out.extend(_leaves(requires["all_of"]))
    if isinstance(requires.get("any_of"), list):
        for group in requires["any_of"]:
            out.extend(_leaves(group if isinstance(group, list) else [group]))
    return out

_requirements = flatten_requirements

def _dnf(item, cap):
    """Alternatives (lists of leaf requirements) of one node; raises CatalogError past `cap` alternatives."""
    if isinstance(item, list):
        alternatives = [[]]
        for child in item:
            sub = _dnf(child, cap)
            alternatives = [a + b for a in alternatives for b in sub]
            if len(alternatives) > cap:
                raise CatalogError(f"requirement expansion exceeds {cap} alternatives")
        return alternatives
    if is_group(item):
        if "all_of" in item:
            return _dnf(list(item.get("all_of") or []), cap)
        out = []
        for child in item.get("any_of") or []:
            out.extend(_dnf(child if isinstance(child, list) else [child], cap))
            if len(out) > cap:
                raise CatalogError(f"requirement expansion exceeds {cap} alternatives")
        return out
    return [[item]]

def expand_requires(requires, cap=MAX_ALTERNATIVES):
    """Disjunctive normal form of requires: a list of alternatives, each a list of leaf requirements that must
    all hold. v1 semantics are kept: all_of AND (one any_of group), with no any_of meaning just all_of. Nested
    {any_of}/{all_of} nodes multiply out (cartesian product), capped at `cap` alternatives."""
    requires = requires if isinstance(requires, dict) else {}
    base = _dnf(list(requires.get("all_of") or []), cap)
    groups = requires.get("any_of") or []
    if not groups:
        return base
    tail = []
    for group in groups:
        tail.extend(_dnf(group if isinstance(group, list) else [group], cap))
    out = [a + b for a in base for b in tail]
    if len(out) > cap:
        raise CatalogError(f"requirement expansion exceeds {cap} alternatives")
    return out

def _validate_items(items, provider, where, errors, depth=0):
    """Validate a list of requirement items (leaves or nested groups)."""
    for i, item in enumerate(items):
        here = f"{where}[{i}]"
        if isinstance(item, dict) and set(item) & set(GROUP_KEYS):
            if not is_group(item):
                errors.append(f"{here}: a nested group has exactly one of all_of/any_of (plus optional notes)")
                continue
            if depth + 1 > MAX_GROUP_DEPTH:
                errors.append(f"{here}: requirement groups nest deeper than {MAX_GROUP_DEPTH}")
                continue
            key = "all_of" if "all_of" in item else "any_of"
            children = item.get(key)
            if not isinstance(children, list) or not children:
                errors.append(f"{here}.{key}: must be a non-empty list")
                continue
            if key == "any_of":
                for j, child in enumerate(children):
                    if isinstance(child, list):
                        if not child:
                            errors.append(f"{here}.any_of[{j}]: empty conjunction")
                        _validate_items(child, provider, f"{here}.any_of[{j}]", errors, depth + 1)
                    else:
                        _validate_items([child], provider, f"{here}.any_of[{j}]", errors, depth + 1)
            else:
                _validate_items(children, provider, f"{here}.all_of", errors, depth + 1)
            continue
        _validate_requirement(item, provider, here, errors)

def _validate_request_context(value, provider, where, errors):
    if provider not in REQUEST_CONTEXT_PROVIDERS:
        errors.append(f"{where}: request_context is only evaluated for {REQUEST_CONTEXT_PROVIDERS}")
        return
    if not isinstance(value, dict) or not value:
        errors.append(f"{where}: request_context must be a non-empty mapping of condition key -> value")
        return
    choices = 1
    for key, val in value.items():
        if not isinstance(key, str) or not _CONTEXT_KEY.match(key) or "*" in key.split(":", 1)[0]:
            errors.append(f"{where}: request_context key {key!r} must be a condition key 'prefix:name'")
            continue
        if isinstance(val, str):
            continue
        if isinstance(val, list) and val and all(isinstance(x, str) for x in val):
            choices *= len(val)
            continue
        if isinstance(val, dict) and len(val) == 1:
            (kind, arg), = val.items()
            if kind in ("absent", "chosen") and arg is True:
                continue
            if kind == "source_principal" and arg is True and key.lower() in ("lambda:principal", "quicksight:iamarn"):
                continue
            if kind == "admin_managed_policy" and arg is True and key.lower() == "iam:policyarn":
                continue
            if kind == "values" and isinstance(arg, list) and arg and all(isinstance(x, str) for x in arg):
                continue
        errors.append(f"{where}: request_context {key}: value must be a string, a list of strings (the requester picks "
                      f"one), {{values: [..]}} (multi-valued key), {{absent: true}}, {{chosen: true}}, or "
                      f"{{admin_managed_policy: true}} for iam:PolicyARN, or "
                      f"{{source_principal: true}} for lambda:Principal or quicksight:IamArn")
    if choices > MAX_CONTEXT_CHOICES:
        errors.append(f"{where}: request_context has more than {MAX_CONTEXT_CHOICES} value combinations")
    bad = set().union(*(_placeholders(x) for v in value.values() for x in (v if isinstance(v, list) else [v])
                        if isinstance(x, str)))
    if provider == "aws":
        bad -= {"source.partition"}
    if bad:
        errors.append(f"{where}: request_context values cannot use placeholders ({sorted(bad)})")


def _validate_requirement(item, provider, where, errors):
    if not isinstance(item, dict):
        errors.append(f"{where}: requirement must be a mapping")
        return
    allowed = REQUIREMENT_FIELDS[provider]
    unknown = set(item) - allowed
    if unknown:
        errors.append(f"{where}: unknown requirement fields {sorted(unknown)}")
    if provider == "aws":
        if not isinstance(item.get("action"), str) or ":" not in item["action"]:
            errors.append(f"{where}: aws requirement needs action 'service:Action'")
        elif any(c in item["action"] for c in "*?"):
            errors.append(f"{where}: requirement action must be concrete (no wildcards)")
    elif provider == "gcp":
        permission = item.get("permission", item.get("action"))
        if not isinstance(permission, str) or permission.count(".") < 2 or "*" in permission:
            errors.append(f"{where}: gcp requirement needs a concrete permission 'service.resource.verb'")
    elif provider == "azure":
        kinds = [k for k in AZURE_REQUIREMENT_KINDS if k in item]
        if len(kinds) != 1 or not isinstance(item[kinds[0]], str) or not item[kinds[0]]:
            errors.append(f"{where}: azure requirement needs exactly one of {'/'.join(AZURE_REQUIREMENT_KINDS)}")
        if "data_action" in item and not isinstance(item["data_action"], bool):
            errors.append(f"{where}: data_action must be a boolean")
        if "entra_owner_of" in item and item.get("object_type") not in ("application", "servicePrincipal", "group"):
            errors.append(f"{where}: entra_owner_of needs object_type application|servicePrincipal|group")
        if "object_type" in item and "entra_owner_of" not in item:
            errors.append(f"{where}: object_type is only valid with entra_owner_of")
        if "entra_tenant_setting" in item and item["entra_tenant_setting"] not in ENTRA_TENANT_SETTINGS:
            errors.append(f"{where}: unknown entra_tenant_setting {item['entra_tenant_setting']!r}")
        if "fabric_workspace_role" in item and item["fabric_workspace_role"] not in FABRIC_WORKSPACE_ROLES:
            errors.append(f"{where}: fabric_workspace_role must be one of {FABRIC_WORKSPACE_ROLES}")
        for field, owner in (("fabric_workspace", "fabric_workspace_role"), ("catalog", "entra_catalog_role")):
            if field in item and owner not in item:
                errors.append(f"{where}: {field} is only valid with {owner}")
            elif field in item and (not isinstance(item[field], str) or not item[field]):
                errors.append(f"{where}: {field} must be a non-empty string ('*' = any)")
    elif provider == "k8s":
        verbs = [k for k in ("verb", "verb_prefix") if k in item]
        any_resource = "resource_match" in item
        if len(verbs) != 1 or not isinstance(item[verbs[0]], str) or not item[verbs[0]].strip():
            errors.append(f"{where}: k8s requirement needs exactly one of verb / verb_prefix")
        elif verbs[0] == "verb_prefix" and "*" in item["verb_prefix"]:
            errors.append(f"{where}: verb_prefix is a literal prefix (no '*')")
        if any_resource and item["resource_match"] not in K8S_RESOURCE_MATCH:
            errors.append(f"{where}: resource_match must be one of {K8S_RESOURCE_MATCH}")
        if any_resource and item.get("resource", "*") != "*":
            errors.append(f"{where}: resource_match any needs resource '*' or no resource")
        if any_resource and ("subresource" in item or "resource_name" in item):
            errors.append(f"{where}: resource_match any cannot be combined with subresource / resource_name")
        if not any_resource and not isinstance(item.get("resource"), str):
            errors.append(f"{where}: k8s requirement needs resource (or resource_match: any)")
        if "/" in str(item.get("resource", "")):
            errors.append(f"{where}: use subresource instead of resource 'a/b'")
    if "bind" in item:
        bind = item["bind"]
        if not isinstance(bind, str) or not _BIND.match(bind):
            errors.append(f"{where}: bind must be a snake_case name")
        else:
            names = {n for k, v in item.items() if k not in ("notes", "bind", "request_context") for n in _placeholders(v)}
            bad = sorted(n for n in names if n == "pivot" or n.startswith(("target", "pivot.")))
            if bad:
                errors.append(f"{where}: bound requirements must not depend on the target or pivot ({bad}); "
                              "use {source.account}/{account} or a literal pattern")
    if "request_context" in item:
        _validate_request_context(item["request_context"], provider, where, errors)
    for key, value in item.items():
        if key in ("notes", "request_context"):
            continue
        if not isinstance(value, (str, bool)):
            errors.append(f"{where}: field {key} must be a string or boolean")
        bad = _placeholders(value) - PLACEHOLDERS
        if bad:
            errors.append(f"{where}: unknown placeholders {sorted(bad)}")


def default_outcome(target):
    """Outcome used when an entry does not author target.outcome (inferred from kind and selector)."""
    target = target if isinstance(target, dict) else {}
    kind, selector = target.get("kind"), target.get("selector") or {}
    if kind in GROUP_TARGET_KINDS:
        return "membership"
    if kind in ("entra_role", "aws_identity_center_permission_set"):
        return "role_activation"
    if kind == "aws_service_plane_admin":
        return "application_admin"
    if kind == "k8s_admission_control":
        return "blocker_removal"
    if kind == "k8s_remote_cluster" or (kind == "cloud_identity" and isinstance(selector, dict)
                                        and "k8s_secret_holds_cloud_credential" in selector):
        return "credentials"
    if kind in ("aws_verified_authority", "gcp_verified_authority", "azure_verified_authority", "k8s_verified_authority"):
        return "permission_grant" if isinstance(selector, dict) and selector.get("same_as_source") else "bounded_authority"
    if kind in ENTITY_KINDS:
        return "permission_grant" if isinstance(selector, dict) and selector.get("same_as_source") else "scope_control"
    return "identity"

def _validate_outcome(target, kind, selector, where, errors):
    outcome = target.get("outcome")
    if outcome not in OUTCOMES:
        errors.append(f"{where}: target.outcome must be one of {sorted(OUTCOMES)}")
        return
    if kind not in TARGET_KINDS:
        return
    entity = TARGET_KINDS[kind][1] == "entity"
    self_target = isinstance(selector, dict) and selector.get("same_as_source") is True
    if outcome == "membership" and kind not in GROUP_TARGET_KINDS:
        errors.append(f"{where}: outcome membership needs a group target kind ({sorted(GROUP_TARGET_KINDS)})")
    elif outcome in ("identity", "credentials", "workload_execution") and (entity or kind in GROUP_TARGET_KINDS):
        errors.append(f"{where}: outcome {outcome} needs a principal (non-group) target kind, not {kind}")
    elif outcome == "impersonation" and entity:
        errors.append(f"{where}: outcome impersonation needs a principal or group target kind, not {kind}")
    elif outcome in ("permission_grant", "role_activation", "scope_control") and not (entity or self_target):
        errors.append(f"{where}: outcome {outcome} needs an entity target kind or selector same_as_source")
    elif outcome == "application_admin" and not entity:
        errors.append(f"{where}: outcome application_admin needs an entity target kind, not {kind}")
    elif outcome == "bounded_authority" and kind not in ("aws_verified_authority", "gcp_verified_authority", "azure_verified_authority", "k8s_verified_authority"):
        errors.append(f"{where}: outcome bounded_authority needs a verified-authority entity target kind, not {kind}")
    elif outcome == "blocker_removal" and kind != "k8s_admission_control":
        errors.append(f"{where}: outcome blocker_removal needs target kind k8s_admission_control")

def validate_entry(entry, *, expected_provider=None, hacktricks_root=None):
    """Return (errors, warnings) for one technique."""
    errors, warnings = [], []
    if not isinstance(entry, dict):
        return ["entry must be a mapping"], warnings
    ident = entry.get("id", "<missing id>")
    where = str(ident)
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{where}: missing field {field}")
    unknown = set(entry) - ENTRY_FIELDS
    if unknown:
        errors.append(f"{where}: unknown fields {sorted(unknown)}")
    if not isinstance(entry.get("id"), str) or not _ID.match(entry.get("id", "")):
        errors.append(f"{where}: id must be kebab-case and provider-prefixed")
    provider = entry.get("provider")
    if provider not in PROVIDERS:
        errors.append(f"{where}: provider must be one of {PROVIDERS}")
        return errors, warnings
    prefix = str(entry.get("id", "")).split("-", 1)[0]
    if prefix != provider and not (prefix == "entra" and provider == "azure"):
        errors.append(f"{where}: id prefix must match provider {provider}")
    if expected_provider and provider != expected_provider:
        errors.append(f"{where}: provider {provider} does not match catalog directory {expected_provider}")
    for field in ("service", "title", "summary", "mitigation", "source"):
        if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
            errors.append(f"{where}: {field} must be a non-empty string")
    for field in ("title", "summary", "mitigation", "notes"):
        if isinstance(entry.get(field), str) and _COMMANDS.search(entry[field]):
            warnings.append(f"{where}: {field} looks like it contains a command; entries must not contain how-to steps")
    source = entry.get("source")
    if isinstance(source, str):
        if not source.startswith("src/"):
            errors.append(f"{where}: source must be a hacktricks-cloud path starting with src/")
        root = Path(hacktricks_root) if hacktricks_root else HACKTRICKS_CLOUD
        # A checkout at another revision cannot judge the path (pages are added and moved upstream);
        # tests/test_peaso_privesc_catalog_sources.py verifies path + anchor against a matching checkout.
        if (root.is_dir() and not (root / source.split("#", 1)[0]).is_file()
                and revision_matches(entry.get("source_revision"), checkout_revision(root))):
            errors.append(f"{where}: source file not found in hacktricks-cloud: {source.split('#', 1)[0]}")
    requires = entry.get("requires")
    groups = 0
    alternatives = []
    if not isinstance(requires, dict) or set(requires) - {"all_of", "any_of"}:
        errors.append(f"{where}: requires must be a mapping with all_of/any_of")
    else:
        all_of = requires.get("all_of") or []
        any_of = requires.get("any_of") or []
        if not isinstance(all_of, list) or not isinstance(any_of, list):
            errors.append(f"{where}: all_of and any_of must be lists")
        else:
            _validate_items(all_of, provider, f"{where}.requires.all_of", errors)
            for i, group in enumerate(any_of):
                if not isinstance(group, list) or not group:
                    errors.append(f"{where}: any_of[{i}] must be a non-empty list of requirements")
                    continue
                _validate_items(group, provider, f"{where}.requires.any_of[{i}]", errors)
            groups = len(all_of) + len(any_of)
            try:
                alternatives = expand_requires(requires)
            except CatalogError as exc:
                errors.append(f"{where}: {exc}")
                alternatives = []
            binds = {}
            for alt in alternatives:
                for req in alt:
                    if isinstance(req, dict) and isinstance(req.get("bind"), str):
                        binds.setdefault(req["bind"], set()).add(id(req))
            for name, members in sorted(binds.items()):
                if len(members) < 2:
                    warnings.append(f"{where}: bind {name!r} is used by a single requirement (no effect)")
        if groups == 0 and not entry.get("source_kind"):
            errors.append(f"{where}: at least one requirement is needed (or a source_kind for intrinsic techniques)")
    target = entry.get("target")
    if not isinstance(target, dict):
        errors.append(f"{where}: target must be a mapping")
    else:
        unknown = set(target) - {"kind", "selector", "scope", "aggregate_as", "include_service_managed", "outcome", "grants",
                                 "removes_blockers"}
        if unknown:
            errors.append(f"{where}: unknown target fields {sorted(unknown)}")
        kind = target.get("kind")
        if kind not in TARGET_KINDS:
            errors.append(f"{where}: unknown target kind {kind!r}")
        elif not kind_allowed(kind, provider):
            errors.append(f"{where}: target kind {kind} is not a {provider} kind")
        selector = target.get("selector") or {}
        if not isinstance(selector, dict):
            errors.append(f"{where}: selector must be a mapping")
            selector = {}
        for key, value in selector.items():
            if key not in SELECTOR_KEYS:
                errors.append(f"{where}: unknown selector key {key!r}")
                continue
            providers, value_kind, _ = SELECTOR_KEYS[key]
            if provider not in providers:
                errors.append(f"{where}: selector {key} is not supported for {provider}")
            if value_kind == "bool_true" and value is not True:
                errors.append(f"{where}: selector {key} must be true")
            elif value_kind == "bool" and not isinstance(value, bool):
                errors.append(f"{where}: selector {key} must be a boolean")
            elif value_kind in ("string", "action", "namespace") and not isinstance(value, str):
                errors.append(f"{where}: selector {key} must be a string")
            elif value_kind == "glob_list" and not (isinstance(value, str) and value or (
                    isinstance(value, list) and value and all(isinstance(x, str) and x for x in value))):
                errors.append(f"{where}: selector {key} must be a glob string or list of glob strings")
            elif value_kind == "host_link" and value not in AZURE_HOST_LINKS:
                errors.append(f"{where}: selector {key} must be one of {AZURE_HOST_LINKS}")
            elif value_kind == "consumer_binding" and not (isinstance(value, (str, list)) and value and all(
                    x in AZURE_CONSUMER_BINDINGS for x in as_str_list(value))):
                errors.append(f"{where}: selector {key} must be one or a list of {AZURE_CONSUMER_BINDINGS}")
            elif value_kind == "pim_group_access" and value is not True and value not in PIM_GROUP_ACCESS:
                errors.append(f"{where}: selector {key} must be true or one of {PIM_GROUP_ACCESS}")
            elif value_kind == "service_plane" and value not in SERVICE_PLANES:
                errors.append(f"{where}: selector {key} must be one of {SERVICE_PLANES}")
            elif value_kind == "secret_provider" and not (value is True or (
                    isinstance(value, (str, list)) and value and all(x in SECRET_PROVIDERS for x in as_str_list(value)))):
                errors.append(f"{where}: selector {key} must be true or one/a list of {SECRET_PROVIDERS}")
            elif value_kind == "label_selector" and not (value is True or (
                    isinstance(value, (str, list)) and value and all(isinstance(x, str) and _LABEL_SEL.match(x) for x in as_str_list(value)))):
                errors.append(f"{where}: selector {key} must be true or 'key=value' / 'key' label selector(s)")
            elif value_kind == "string_or_list" and not (isinstance(value, str) or (
                    isinstance(value, list) and value and all(isinstance(x, str) for x in value))):
                errors.append(f"{where}: selector {key} must be a string or list of strings")
            bad = set().union(*(_placeholders(x) for x in (value if isinstance(value, list) else [value]))) - PLACEHOLDERS
            if bad:
                errors.append(f"{where}: selector {key} has unknown placeholders {sorted(bad)}")
            if value_kind == "glob_list" and any(_placeholders(x) for x in (value if isinstance(value, list) else [value])):
                errors.append(f"{where}: selector {key} globs are literal (no placeholders)")
        if target.get("scope", "any") not in SCOPES:
            errors.append(f"{where}: target scope must be one of {SCOPES}")
        if "aggregate_as" in target and not isinstance(target["aggregate_as"], str):
            errors.append(f"{where}: aggregate_as must be a string")
        if "include_service_managed" in target and not isinstance(target["include_service_managed"], bool):
            errors.append(f"{where}: include_service_managed must be a boolean")
        if "outcome" in target:
            _validate_outcome(target, kind, selector, where, errors)
        if kind == "aws_service_plane_admin" and "service_plane" not in selector:
            errors.append(f"{where}: aws_service_plane_admin targets need selector service_plane ({'|'.join(SERVICE_PLANES)})")
        if "service_plane" in selector and kind != "aws_service_plane_admin":
            errors.append(f"{where}: selector service_plane is only valid with target kind aws_service_plane_admin")
        aws_authority_selectors = (
            "aws_challenge_fact", "aws_s3_policy_self_grant", "aws_sqs_policy_self_grant", "aws_sns_policy_self_grant", "aws_dynamodb_policy_self_grant", "aws_s3_access_grants_self_grant",
            "aws_secretsmanager_policy_self_grant", "aws_efs_policy_self_grant",
            "aws_cases_tag_self_grant", "aws_sitewise_portal_self_grant")
        selected_authority = [key for key in aws_authority_selectors if selector.get(key)]
        if kind == "aws_verified_authority" and len(selected_authority) != 1:
            errors.append(f"{where}: aws_verified_authority needs exactly one reviewed authority selector")
        if kind != "aws_verified_authority" and any(selector.get(key) for key in aws_authority_selectors[1:]):
            errors.append(f"{where}: reviewed AWS self-grant selectors need aws_verified_authority")
        if str(entry.get("id", "")).startswith("aws-v3-") and not selector.get("aws_challenge_fact"):
            errors.append(f"{where}: AWS v3 challenge entries need an exact evidence selector")
        if kind == "aws_challenge_foothold":
            errors.append(f"{where}: aws_challenge_foothold is a source kind, not a target")
        if kind == "gcp_challenge_foothold":
            errors.append(f"{where}: gcp_challenge_foothold is a source kind, not a target")
        if kind == "azure_challenge_foothold":
            errors.append(f"{where}: azure_challenge_foothold is a source kind, not a target")
        for evidence_provider in ("azure", "k8s"):
            fact_key = evidence_provider + "_challenge_fact"
            if selector.get(fact_key):
                if selector[fact_key] != entry.get("id"):
                    errors.append(f"{where}: {fact_key} must equal the technique id")
                if entry.get("confidence") != "conditional":
                    errors.append(f"{where}: {fact_key} must remain conditional")
                if kind in ("azure_challenge_foothold",):
                    errors.append(f"{where}: {fact_key} needs a bounded target")
        if kind == "azure_storage_local_user" and (selector.get("azure_storage_local_credential") not in
                ("reset_password", "write_credential", "create_credential") or entry.get("confidence") != "conditional"):
            errors.append(f"{where}: storage local users need a supported credential selector and conditional confidence")
        if kind == "azure_verified_authority" and not selector.get("azure_challenge_fact"):
            errors.append(f"{where}: verified authority needs an exact evidence selector")
        if kind == "azure_external_principal" and not selector.get("azure_external_principal_evidence"):
            errors.append(f"{where}: azure_external_principal needs typed evidence")
        if selector.get("azure_external_principal_evidence"):
            from peaso.privesc.effective_permissions.azure_external_principal import CONTRACT
            contract = CONTRACT.get(entry.get("id"))
            expected_outcome = "credentials" if contract and contract[2] == "credential" else "identity"
            if (kind != "azure_external_principal"
                    or set(selector) != {"azure_external_principal_evidence", "azure_external_plane"}
                    or contract is None or selector.get("azure_external_plane") != contract[1]
                    or (entry.get("target") or {}).get("outcome") != expected_outcome
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: Azure external-principal evidence needs a registered action/plane, matching target outcome and conditional confidence")
        if kind == "gcp_verified_authority" and not (selector.get("gcp_challenge_fact") or selector.get("gcp_resource_self_grant")
                                                        or selector.get("gcp_bounded_access_gain") or selector.get("gcp_agentidentity_retrieve_path") or selector.get("gcp_agentidentity_update_path") or selector.get("gcp_hmac_storage_identity")
                                                        or selector.get("gcp_bounded_service_execution") or selector.get("gcp_bounded_workspace_oauth") or selector.get("gcp_agentregistry_skill_evidence")):
            errors.append(f"{where}: gcp_verified_authority needs an exact evidence selector")
        if selector.get("gcp_agentregistry_skill_evidence"):
            if (entry.get("id") != "gcp-agentregistry-skill-default-revision-replace"
                    or kind != "gcp_verified_authority"
                    or set(selector) != {"gcp_agentregistry_skill_evidence"}
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: Agent Registry Skill needs exact bounded execution evidence")
        if selector.get("gcp_hmac_storage_identity"):
            if (kind != "gcp_verified_authority" or set(selector) != {"gcp_hmac_storage_identity", "gcp_sa_in_scope_of_permission"}
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"
                    or entry.get("id") != "gcp-storage-hmackeys-create"):
                errors.append(f"{where}: HMAC authority needs its exact bounded target and project-local selector")
        if selector.get("gcp_bounded_service_execution"):
            service_by_entry = {
                "gcp-bigquery-transfers-scheduled-query-actas": "bigquery_scheduled_query",
                "gcp-bigquery-continuous-query-actas": "bigquery_continuous_query",
                "gcp-dataform-workflow-invocation-actas": "dataform_workflow",
                "gcp-apikeys-authorization-key-bound-sa": "apikeys_authorization_key",
            }
            if (kind != "gcp_verified_authority"
                    or set(selector) != {"gcp_bounded_service_execution", "gcp_actas_granted_on_target", "gcp_sa_in_scope_of_permission"}
                    or selector["gcp_bounded_service_execution"] != service_by_entry.get(entry.get("id"))
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"):
                errors.append(f"{where}: bounded service authority needs its exact mechanism and project-local actAs selector")
        if selector.get("gcp_bounded_workspace_oauth"):
            workspace_by_entry = {
                "gcp-workspace-dwd-keyless-signjwt": ("dwd", "workspace_dwd_delegation"),
                "gcp-workspace-dwd-key-create": ("dwd", "workspace_dwd_delegation"),
                "gcp-workspace-addons-deployment-update": ("addon", "workspace_addon_user"),
            }
            expected = workspace_by_entry.get(entry.get("id"))
            if (kind != "gcp_verified_authority" or set(selector) != {"gcp_bounded_workspace_oauth", "attached_to_service"}
                    or expected != (selector["gcp_bounded_workspace_oauth"], selector["attached_to_service"])
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"):
                errors.append(f"{where}: Workspace OAuth authority needs an exact mechanism and user attachment")
        if selector.get("gcp_resource_self_grant"):
            if (kind != "gcp_verified_authority" or selector.get("gcp_challenge_fact")
                    or (entry.get("target") or {}).get("outcome") != "permission_grant"
                    or not (entry.get("target") or {}).get("grants")
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: gcp_resource_self_grant needs verified-authority permission_grant, named grants and conditional confidence")
        if selector.get("gcp_agentidentity_retrieve_path"):
            if (entry.get("id") != "gcp-agentidentity-retrieve-credentials"
                    or kind != "gcp_verified_authority"
                    or set(selector) != {"gcp_agentidentity_retrieve_path"}
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: Agent Identity retrieval needs its exact bounded authorization target")
        if selector.get("gcp_agentidentity_update_path"):
            if (entry.get("id") != "gcp-agentidentity-update-token-url"
                    or kind != "gcp_verified_authority"
                    or set(selector) != {"gcp_agentidentity_update_path"}
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: Agent Identity endpoint change needs its exact bounded authorization target")
        if kind == "gcp_external_principal" and not selector.get("gcp_external_principal_evidence"):
            errors.append(f"{where}: gcp_external_principal needs typed external-principal evidence")
        if selector.get("gcp_external_principal_evidence"):
            if (kind != "gcp_external_principal" or set(selector) != {"gcp_external_principal_evidence", "gcp_external_plane"}
                    or not isinstance(selector.get("gcp_external_plane"), str)
                    or not selector["gcp_external_plane"].strip()
                    or (entry.get("target") or {}).get("outcome") != "credentials"
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: external-principal evidence needs an exact plane, credentials target and conditional confidence")
        if selector.get("gcp_bounded_access_gain"):
            if (kind != "gcp_verified_authority"
                    or set(selector) != {"gcp_bounded_access_gain", "gcp_bounded_mechanism"}
                    or selector.get("gcp_bounded_mechanism") not in (
                        "biglake_connection_table", "bigquery_remote_function",
                        "bigquery_authorized_routine", "bigquery_authorized_view",
                        "bigquery_authorized_dataset")
                    or (entry.get("target") or {}).get("outcome") != "bounded_authority"
                    or len((entry.get("target") or {}).get("grants") or []) != 1
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: bounded access needs one exact mechanism and named action on a conditional verified-authority target")
        if kind == "k8s_verified_authority" and not (selector.get("k8s_helm_values_rbac") or selector.get("k8s_verified_pivot") or selector.get("k8s_bound_role_gain") or selector.get("k8s_existing_rolebinding_gain") or selector.get("k8s_clusterrolebinding_gain") or selector.get("k8s_existing_clusterrolebinding_gain")):
            errors.append(f"{where}: k8s_verified_authority needs typed role-binding, Helm, or verified-pivot evidence")
        if selector.get("k8s_helm_values_rbac") and (kind != "k8s_verified_authority" or selector.get("k8s_challenge_fact")):
            errors.append(f"{where}: k8s_helm_values_rbac needs an exclusive k8s_verified_authority target")
        if selector.get("k8s_verified_pivot"):
            from peaso.privesc.effective_permissions.k8s_verified_pivots import KINDS
            if (selector["k8s_verified_pivot"] != entry.get("id")
                    or set(selector) != {"k8s_verified_pivot"}
                    or kind != KINDS.get(entry.get("id"))
                    or (entry.get("target") or {}).get("outcome") !=
                    ("permission_grant" if kind == "k8s_verified_authority" else "credentials")
                    or (kind == "k8s_verified_authority" and not (entry.get("target") or {}).get("grants"))
                    or entry.get("confidence") != "conditional"):
                errors.append(f"{where}: k8s_verified_pivot needs an exclusive matching typed target and conditional outcome")
        if str(entry.get("id", "")).startswith("gcp-v3-") and not selector.get("gcp_challenge_fact"):
            errors.append(f"{where}: GCP v3 challenge entries need an exact evidence selector")
        if selector.get("gcp_challenge_fact"):
            if selector["gcp_challenge_fact"] != entry.get("id"):
                errors.append(f"{where}: gcp_challenge_fact must equal the technique id")
            if kind not in ("gcp_service_account", "gcp_user", "gcp_workspace_user", "gcp_group",
                            "k8s_service_account", "gcp_verified_authority"):
                errors.append(f"{where}: gcp_challenge_fact needs a bounded identity or authority target")
            if entry.get("confidence") != "conditional":
                errors.append(f"{where}: gcp_challenge_fact must remain conditional")
        if selector.get("aws_challenge_fact") and selector["aws_challenge_fact"] != entry.get("id"):
            errors.append(f"{where}: aws_challenge_fact must equal the technique id")
        if selector.get("aws_challenge_fact"):
            if kind not in ("aws_role", "aws_user", "aws_verified_authority"):
                errors.append(f"{where}: aws_challenge_fact needs an IAM role/user or bounded authority target")
            if entry.get("confidence") != "conditional":
                errors.append(f"{where}: aws_challenge_fact must remain conditional")
            if entry.get("source_kind") == "aws_challenge_foothold" and not re.fullmatch(
                    r"aws_challenge_foothold:\*:(anonymous|runtime|local|application|endpoint)",
                    str((entry.get("source_selector") or {}).get("source_id_glob", ""))):
                errors.append(f"{where}: challenge foothold source must be restricted to one class")
        for key, wanted in (("k8s_secret_holds_cloud_credential", "cloud_identity"),
                            ("k8s_secret_holds_remote_cluster_credential", "k8s_remote_cluster"),
                            ("k8s_node_hosting_pod_of_source", "k8s_node"), ("k8s_sa_used_by_pending_pod", "k8s_service_account"),
                            ("k8s_sa_namespace_absent", "k8s_service_account"), ("k8s_sa_named_in_scc_users", "k8s_service_account"),
                            ("gcp_group_join_open_to_source", "gcp_group"), ("gcp_image_family_consumer", "gcp_service_account"),
                            ("gcp_workspace_super_admin_with_registered_domain", "gcp_workspace_user")):
            if key in selector and kind != wanted:
                errors.append(f"{where}: selector {key} needs target kind {wanted}")
        for key, wanted in AZURE_SELECTOR_KINDS.items():
            if key in selector and kind not in wanted:
                errors.append(f"{where}: selector {key} needs target kind {' or '.join(wanted)}")
        if kind == "k8s_remote_cluster" and not ({"k8s_secret_holds_remote_cluster_credential", "k8s_verified_pivot"} & set(selector)):
            errors.append(f"{where}: k8s_remote_cluster targets need a remote-cluster credential selector")
        removes = target.get("removes_blockers")
        if kind == "k8s_admission_control" and removes is None:
            errors.append(f"{where}: k8s_admission_control targets need removes_blockers (blocker ids the technique lifts)")
        if removes is not None:
            if kind != "k8s_admission_control":
                errors.append(f"{where}: removes_blockers is only valid with target kind k8s_admission_control")
            elif not (isinstance(removes, list) and removes and all(isinstance(x, str) for x in removes)):
                errors.append(f"{where}: removes_blockers must be a non-empty list of blocker ids")
            else:
                bad = sorted(x for x in removes if x not in KNOWN_BLOCKERS)
                if bad:
                    errors.append(f"{where}: removes_blockers has unknown blockers {bad} (known: {sorted(KNOWN_BLOCKERS)})")
        if "grants" in target and not (isinstance(target["grants"], list) and target["grants"]
                                       and all(isinstance(x, str) and x.strip() for x in target["grants"])):
            errors.append(f"{where}: target.grants must be a non-empty list of permission / role names")
        if kind in ENTITY_KINDS and isinstance(requires, dict):
            used = set().union(*(_placeholders(v) for r in _requirements(requires) for k, v in r.items() if k != "notes"))
            allowed = ENTITY_TARGET_PLACEHOLDERS.get(kind, {"target.scope"})
            bad = sorted(p for p in used if p.startswith("target.") and p not in allowed)
            if bad:
                errors.append(f"{where}: placeholders {bad} cannot resolve on entity target kind {kind} "
                              f"(only {sorted(allowed)}); use a source.* placeholder or a principal target kind")
        aws_v2 = "via_assumable_role_attached_policy_covered_by" in selector
        aws_uses = [r for r in _requirements(requires) if any(
            "source.assumable_role_attached_policy_arn" in _placeholders(v) for v in r.values())] if isinstance(requires, dict) else []
        aws_ph = bool(aws_uses) and all(r.get("resource") == "{source.assumable_role_attached_policy_arn}"
                                        and r.get("action") == "iam:CreatePolicyVersion" for r in aws_uses)
        if aws_v2 or aws_uses:
            expected = {"action": "iam:CreatePolicyVersion", "resource": "{source.assumable_role_attached_policy_arn}"}
            if not (aws_v2 and aws_ph and provider == "aws" and kind == "aws_account_admin"
                    and target.get("scope") == "same_account"
                    and selector.get("via_assumable_role_attached_policy_covered_by") == "iam:CreatePolicyVersion"
                    and any(all(r.get(k) == v for k, v in expected.items()) for r in _requirements(requires))):
                errors.append(f"{where}: assumable-role policy selector and CreatePolicyVersion placeholder requirement must occur together on aws_account_admin")
            if aws_v2 and any(r.get("action") == "iam:SetDefaultPolicyVersion" for r in _requirements(requires)):
                errors.append(f"{where}: SetDefaultPolicyVersion cannot satisfy the assumable-role policy selector")
            if aws_v2 and any(not any(r.get("action") == "iam:CreatePolicyVersion" and
                                      r.get("resource") == "{source.assumable_role_attached_policy_arn}"
                                      for r in alt) for alt in alternatives):
                errors.append(f"{where}: every alternative using the assumable-role policy selector needs its CreatePolicyVersion requirement")
        if "k8s_sa_used_by_running_pod" in selector and provider == "gcp":
            if kind != "k8s_service_account" or target.get("scope") != "cluster":
                errors.append(f"{where}: GCP running-pod KSA selector needs k8s_service_account in cluster scope")
            if {"k8s_sa_in_cluster", "k8s_sa_has_token_secret"} & set(selector):
                errors.append(f"{where}: GCP running-pod KSA selector cannot combine with other KSA selectors")
        if kind == "k8s_service_account" and provider == "gcp" and not {"k8s_sa_has_token_secret", "k8s_sa_in_cluster", "k8s_sa_used_by_running_pod", "gcp_challenge_fact"} & set(selector):
            errors.append(f"{where}: gcp k8s_service_account targets need selector k8s_sa_has_token_secret, k8s_sa_in_cluster, or k8s_sa_used_by_running_pod")
        rolebound_uses = [r for r in _requirements(requires) if any(
            "source_rolebound_clusterrole" in _placeholders(v) for v in r.values())] if isinstance(requires, dict) else []
        rolebound = bool(rolebound_uses)
        if rolebound:
            if not (provider == "k8s" and kind == "k8s_service_account" and target.get("scope") == "same_namespace"
                    and selector.get("k8s_sa_in_namespace") == "{target.namespace}"):
                errors.append(f"{where}: source_rolebound_clusterrole needs a same-namespace K8s SA target")
            if any(r.get("resource_name") != "{source_rolebound_clusterrole}"
                   or r.get("resource") != "clusterroles"
                   or r.get("api_group") != "rbac.authorization.k8s.io"
                   or r.get("namespace") != "*"
                   or r.get("verb") not in ("escalate", "update", "patch")
                   for r in rolebound_uses):
                errors.append(f"{where}: source_rolebound_clusterrole requires named clusterroles escalate/update/patch in cluster scope")
            for alt in alternatives:
                leaves = [r for r in alt if r.get("resource_name") == "{source_rolebound_clusterrole}"
                          and r.get("resource") == "clusterroles" and r.get("api_group") == "rbac.authorization.k8s.io"
                          and r.get("namespace") == "*"]
                if not (any(r.get("verb") == "escalate" for r in leaves)
                        and any(r.get("verb") in ("update", "patch") for r in leaves)):
                    errors.append(f"{where}: every alternative needs escalate and update/patch on the same rolebound ClusterRole")
                    break
        if kind == "k8s_service_account" and provider == "k8s" and isinstance(requires, dict):
            text = repr(requires) + repr(selector)
            if "{target.namespace}" not in text and "k8s_sa_in_namespace" not in selector and "k8s_aggregated_rolebinding_namespace" not in selector and target.get("scope") != "same_namespace":
                warnings.append(f"{where}: k8s service-account target without a namespace restriction reaches every namespace")
    source_kind = entry.get("source_kind")
    if source_kind is not None:
        kinds = source_kind if isinstance(source_kind, list) else [source_kind]
        for value in kinds:
            if value not in TARGET_KINDS or TARGET_KINDS[value][1] != "principal" or not kind_allowed(value, provider):
                errors.append(f"{where}: source_kind {value!r} is not a {provider} principal kind")
    source_selector = entry.get("source_selector")
    if source_selector is not None:
        if not isinstance(source_selector, dict):
            errors.append(f"{where}: source_selector must be a mapping")
        else:
            for key, value in source_selector.items():
                if key not in SOURCE_SELECTOR_KEYS:
                    errors.append(f"{where}: unknown source_selector key {key!r}")
                elif provider not in SOURCE_SELECTOR_KEYS[key][0]:
                    errors.append(f"{where}: source_selector {key} is not supported for {provider}")
                elif SOURCE_SELECTOR_KEYS[key][1] == "glob_list" and not (isinstance(value, str) and value or (
                        isinstance(value, list) and value and all(isinstance(x, str) and x for x in value))):
                    errors.append(f"{where}: source_selector {key} must be a glob string or list of glob strings")
                elif SOURCE_SELECTOR_KEYS[key][1] == "target_kind" and value not in TARGET_KINDS:
                    errors.append(f"{where}: source_selector {key} must be a target kind")
                elif SOURCE_SELECTOR_KEYS[key][1] == "bound_scope" and value not in (True, "cluster", "namespace"):
                    errors.append(f"{where}: source_selector {key} must be true or 'cluster'")
    pivot_type = entry.get("pivot_resource_type")
    uses_pivot = "{pivot}" in repr(requires) + repr((target or {}).get("selector") if isinstance(target, dict) else "")
    if pivot_type is not None and not isinstance(pivot_type, str):
        errors.append(f"{where}: pivot_resource_type must be a string")
    if uses_pivot and pivot_type is None:
        warnings.append(f"{where}: uses {{pivot}} without pivot_resource_type")
    conditions = entry.get("conditions", [])
    if not isinstance(conditions, list):
        errors.append(f"{where}: conditions must be a list")
    else:
        for i, condition in enumerate(conditions):
            if isinstance(condition, str):
                continue
            if not isinstance(condition, dict) or not isinstance(condition.get("id"), str) or set(condition) - {"id", "description"}:
                errors.append(f"{where}: conditions[{i}] must be {{id, description}}")
    preconditions = entry.get("preconditions", [])
    if not isinstance(preconditions, list):
        errors.append(f"{where}: preconditions must be a list")
    else:
        for i, pre in enumerate(preconditions):
            pid = pre if isinstance(pre, str) else pre.get("id") if isinstance(pre, dict) else None
            if not isinstance(pid, str) or (isinstance(pre, dict) and set(pre) - {"id", "description"}):
                errors.append(f"{where}: preconditions[{i}] must be an id or {{id, description}}")
            elif pid not in PRECONDITIONS:
                errors.append(f"{where}: unknown precondition {pid!r} (known: {sorted(PRECONDITIONS)})")
            elif provider not in PRECONDITIONS[pid][0]:
                errors.append(f"{where}: precondition {pid} is not supported for {provider}")
    blockers = entry.get("blockers", [])
    if not isinstance(blockers, list) or any(not isinstance(x, (str, dict)) for x in blockers):
        errors.append(f"{where}: blockers must be a list of strings")
    else:
        for blocker in blockers:
            name = blocker if isinstance(blocker, str) else blocker.get("id")
            if name not in KNOWN_BLOCKERS:
                warnings.append(f"{where}: unknown blocker {name!r} (reported as not evaluated)")
    for field, allowed in (("confidence", CONFIDENCES), ("severity", SEVERITIES)):
        if field in entry and entry[field] not in allowed:
            errors.append(f"{where}: {field} must be one of {allowed}")
    if "references" in entry and (not isinstance(entry["references"], list) or any(not isinstance(x, str) for x in entry["references"])):
        errors.append(f"{where}: references must be a list of URLs")
    if "notes" in entry and not isinstance(entry["notes"], str):
        errors.append(f"{where}: notes must be a string")
    return errors, warnings


def validate_excluded(items, where):
    errors = []
    if items is None:
        return errors
    if not isinstance(items, list):
        return [f"{where}: _excluded.yaml must be a list"]
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("source"), str) or not isinstance(item.get("reason"), str):
            errors.append(f"{where}[{i}]: excluded entries need source and reason strings")
    return errors


def catalog_files(catalog_dir=None):
    root = Path(catalog_dir) if catalog_dir else CATALOG_DIR
    return sorted(p for p in root.rglob("*.y*ml") if p.is_file())


def load_catalog(catalog_dir=None, *, strict=False, hacktricks_root=None):
    """Load every technique. Returns {entries, errors, warnings, files, excluded}.

    Invalid entries are dropped (never half-evaluated) and reported; strict mode
    raises CatalogError instead.
    """
    root = Path(catalog_dir) if catalog_dir else CATALOG_DIR
    entries, errors, warnings, files, excluded = [], [], [], [], 0
    seen = {}
    for path in catalog_files(root):
        rel = str(path.relative_to(root))
        provider = path.relative_to(root).parts[0] if len(path.relative_to(root).parts) > 1 else None
        try:
            # Always read the file again; only content-identical construction
            # is shared. Hash-bound callers still verify actual file bytes.
            data, candidate = _catalog_document(path.read_text())
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {str(exc).splitlines()[0]}")
            files.append({"file": rel, "entries": 0, "valid": 0})
            continue
        if path.name.startswith("_excluded"):
            excluded_errors = validate_excluded(data, rel)
            errors.extend(excluded_errors)
            if not excluded_errors:
                _remember_catalog_document(candidate)
            excluded += len(data or [])
            files.append({"file": rel, "entries": 0, "excluded": len(data or [])})
            continue
        if data is None:
            data = []
        if not isinstance(data, list):
            errors.append(f"{rel}: catalog file must be a YAML list")
            continue
        valid = 0
        error_count = len(errors)
        for index, entry in enumerate(data):
            entry_errors, entry_warnings = validate_entry(entry, expected_provider=provider if provider in PROVIDERS else None,
                                                          hacktricks_root=hacktricks_root)
            ident = entry.get("id") if isinstance(entry, dict) else None
            if ident in seen:
                entry_errors.append(f"{ident}: duplicate id (also in {seen[ident]})")
            elif ident:
                seen[ident] = rel
            errors.extend(f"{rel}[{index}] {e}" for e in entry_errors)
            warnings.extend(f"{rel}[{index}] {w}" for w in entry_warnings)
            if not entry_errors:
                item = dict(entry)
                item["_file"] = rel
                entries.append(item)
                valid += 1
        if len(errors) == error_count:
            _remember_catalog_document(candidate)
        files.append({"file": rel, "entries": len(data), "valid": valid})
    if strict and errors:
        raise CatalogError("; ".join(errors[:20]))
    return {"entries": entries, "errors": errors, "warnings": warnings, "files": files, "excluded": excluded}

# ---------------------------------------------------------------------------------------- JSON Schema export
JSON_SCHEMA_ID = "https://cloud.hacktricks.wiki/schemas/privesc-technique.schema.json"
JSON_SCHEMA_FILE = Path(__file__).resolve().parent / "privesc-technique.schema.json"

def _value_schema(value_kind):
    strings = {"type": "array", "minItems": 1, "items": {"type": "string"}}
    return {
        "bool_true": {"const": True},
        "bool": {"type": "boolean"},
        "string": {"type": "string"},
        "action": {"type": "string", "minLength": 1},
        "namespace": {"type": "string", "minLength": 1},
        "string_or_list": {"anyOf": [{"type": "string"}, strings]},
        "glob_list": {"anyOf": [{"type": "string", "minLength": 1},
                                {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}]},
        "service_plane": {"enum": list(SERVICE_PLANES)},
        "host_link": {"enum": list(AZURE_HOST_LINKS)},
        "consumer_binding": {"anyOf": [{"enum": list(AZURE_CONSUMER_BINDINGS)},
                                       {"type": "array", "minItems": 1, "items": {"enum": list(AZURE_CONSUMER_BINDINGS)}}]},
        "pim_group_access": {"anyOf": [{"const": True}, {"enum": list(PIM_GROUP_ACCESS)}]},
        "secret_provider": {"anyOf": [{"const": True}, {"enum": list(SECRET_PROVIDERS)},
                                      {"type": "array", "minItems": 1, "items": {"enum": list(SECRET_PROVIDERS)}}]},
        "label_selector": {"anyOf": [{"const": True}, {"type": "string", "pattern": _LABEL_SEL.pattern},
                                     {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": _LABEL_SEL.pattern}}]},
        "target_kind": {"enum": sorted(TARGET_KINDS)},
        "bound_scope": {"anyOf": [{"const": True}, {"const": "cluster"}, {"const": "namespace"}]},
    }[value_kind]

def _leaf_schema(provider):
    text = {"type": "string"}
    common = {"notes": {"type": "string"}, "bind": {"type": "string", "pattern": _BIND.pattern,
              "description": "Requirements with the same bind name must hold on ONE common resource the source picks."}}
    if provider == "aws":
        ctx_value = {"anyOf": [
            {"type": "string"},
            {"type": "array", "minItems": 1, "items": {"type": "string"}, "description": "The requester picks one value."},
            {"type": "object", "additionalProperties": False, "required": ["absent"], "properties": {"absent": {"const": True}}},
            {"type": "object", "additionalProperties": False, "required": ["chosen"], "properties": {"chosen": {"const": True}}},
            {"type": "object", "additionalProperties": False, "required": ["admin_managed_policy"],
             "properties": {"admin_managed_policy": {"const": True}}},
            {"type": "object", "additionalProperties": False, "required": ["source_principal"],
             "properties": {"source_principal": {"const": True}}},
            {"type": "object", "additionalProperties": False, "required": ["values"],
             "properties": {"values": {"type": "array", "minItems": 1, "items": {"type": "string"}}}}]}
        return {"type": "object", "additionalProperties": False, "required": ["action"], "properties": {
            "action": {"type": "string", "pattern": r"^[A-Za-z0-9-]+:[A-Za-z0-9]+$",
                       "description": "Concrete IAM action 'service:Action' (no wildcards)."},
            "resource": {**text, "description": "Resource ARN / pattern / placeholder the action must cover ('*' = any)."},
            "request_context": {"type": "object", "minProperties": 1,
                                "propertyNames": {"pattern": _CONTEXT_KEY.pattern},
                                "additionalProperties": ctx_value,
                                "description": "Condition-key values carried by the technique's own request."},
            **common}}
    if provider == "gcp":
        perm = {"type": "string", "pattern": r"^[^.*\s]+\.[^*\s]+\.[^.*\s]+$",
                "description": "Concrete permission 'service.resource.verb'."}
        return {"type": "object", "additionalProperties": False,
                "anyOf": [{"required": ["permission"]}, {"required": ["action"]}],
                "properties": {"permission": perm, "action": perm, "resource": text, **common}}
    if provider == "azure":
        kinds = list(AZURE_REQUIREMENT_KINDS)
        return {"type": "object", "additionalProperties": False,
                "oneOf": [{"required": [k], "not": {"anyOf": [{"required": [o]} for o in kinds if o != k]}} for k in kinds],
                "dependentRequired": {"object_type": ["entra_owner_of"], "entra_owner_of": ["object_type"],
                                      "fabric_workspace": ["fabric_workspace_role"], "catalog": ["entra_catalog_role"]},
                "properties": {
                    "action": {"type": "string", "minLength": 1, "description": "ARM action (or dataAction with data_action: true)."},
                    "data_action": {"type": "boolean"},
                    "scope": {**text, "description": "ARM scope / Entra directory scope ('*' = any)."},
                    "entra_permission": {"type": "string", "minLength": 1, "description": "microsoft.directory/... permission."},
                    "entra_role": {"type": "string", "minLength": 1, "description": "Entra directory role (name or template id)."},
                    "directory_scope": text,
                    "graph_app_permission": {"type": "string", "minLength": 1, "description": "Microsoft Graph application permission."},
                    "entra_owner_of": {"type": "string", "minLength": 1},
                    "object_type": {"enum": ["application", "servicePrincipal", "group"]},
                    "entra_pim_eligible_role": {"type": "string", "minLength": 1},
                    "entra_tenant_setting": {"enum": list(ENTRA_TENANT_SETTINGS)},
                    "entra_group_member": {"type": "string", "minLength": 1,
                                           "description": "Source is a (transitive) member of the Entra group (display name or object id)."},
                    "fabric_workspace_role": {"enum": list(FABRIC_WORKSPACE_ROLES),
                                              "description": "Fabric workspace role at least as strong as this one."},
                    "fabric_workspace": {**text, "description": "Fabric workspace id, '{target.host_resource}' or '*'."},
                    "intune_permission": {"type": "string", "minLength": 1,
                                          "description": "Intune RBAC resource action (e.g. Microsoft.Intune_DeviceConfigurations_Assign)."},
                    "entra_catalog_role": {"type": "string", "minLength": 1,
                                           "description": "Entitlement-management catalog role (display name or role definition id)."},
                    "catalog": {**text, "description": "Catalog id, '{target.catalog}' or '*'."},
                    **common}}
    return {"type": "object", "additionalProperties": False,
            "oneOf": [{"required": ["verb"], "not": {"required": ["verb_prefix"]}},
                      {"required": ["verb_prefix"], "not": {"required": ["verb"]}}],
            "anyOf": [{"required": ["resource"]}, {"required": ["resource_match"]}],
            "properties": {
        "verb": {"type": "string", "minLength": 1},
        "verb_prefix": {"type": "string", "pattern": r"^[^*]+$",
                        "description": "Any rule verb starting with this prefix matches (e.g. 'impersonate-on:user-info:')."},
        "resource_match": {"enum": list(K8S_RESOURCE_MATCH),
                           "description": "any: any resource (and API group unless api_group is set) the rule names."},
        "resource": {"type": "string", "pattern": r"^[^/]*$", "description": "Resource (use subresource for a/b)."},
        "subresource": text, "api_group": text, "resource_name": text,
        "namespace": {**text, "description": "'{target.namespace}', '{source.namespace}', '*' (cluster-wide) or a literal."},
        **common}}

def json_schema():
    """JSON Schema (draft 2020-12) of a catalog YAML file, generated from the registries of this module.

    It checks structure, vocabularies (kinds, selectors, scopes, preconditions, outcomes) and per-provider
    requirement shapes. schema.validate_entry stays the authority for cross-field rules (placeholder registry,
    entity-kind placeholders, outcome/kind consistency, bind rules, DNF size)."""
    defs = {}
    for provider in PROVIDERS:
        p = provider
        defs[f"{p}_requirement"] = _leaf_schema(p)
        defs[f"{p}_item"] = {"anyOf": [{"$ref": f"#/$defs/{p}_requirement"}, {"$ref": f"#/$defs/{p}_group"}]}
        defs[f"{p}_conjunction"] = {"type": "array", "minItems": 1, "items": {"$ref": f"#/$defs/{p}_item"}}
        defs[f"{p}_group"] = {"type": "object", "additionalProperties": False, "minProperties": 1,
                              "properties": {"notes": {"type": "string"},
                                             "all_of": {"$ref": f"#/$defs/{p}_conjunction"},
                                             "any_of": {"type": "array", "minItems": 1, "items": {"anyOf": [
                                                 {"$ref": f"#/$defs/{p}_item"}, {"$ref": f"#/$defs/{p}_conjunction"}]}}},
                              "oneOf": [{"required": ["all_of"]}, {"required": ["any_of"]}]}
        kinds = sorted(k for k in TARGET_KINDS if kind_allowed(k, p))
        principal_kinds = [k for k in kinds if TARGET_KINDS[k][1] == "principal"]
        selectors = {k: {**_value_schema(v[1]), "description": v[2]} for k, v in sorted(SELECTOR_KEYS.items()) if p in v[0]}
        source_selectors = {k: {**_value_schema(v[1]), "description": v[2]} for k, v in sorted(SOURCE_SELECTOR_KEYS.items())
                            if p in v[0]}
        pre_ids = sorted(k for k, v in PRECONDITIONS.items() if p in v[0])
        prefix = "(azure|entra)" if p == "azure" else p
        defs[f"{p}_technique"] = {
            "properties": {
                "id": {"pattern": f"^{prefix}-[a-z0-9]+(-[a-z0-9]+)*$"},
                "requires": {"type": "object", "additionalProperties": False, "properties": {
                    "all_of": {"type": "array", "items": {"$ref": f"#/$defs/{p}_item"}},
                    "any_of": {"type": "array", "items": {"$ref": f"#/$defs/{p}_conjunction"},
                               "description": "Alternative groups: at least one group must fully hold (with all_of)."}}},
                "target": {"properties": {"kind": {"enum": kinds},
                                          "selector": {"type": "object", "additionalProperties": False, "properties": selectors}}},
                "source_kind": {"anyOf": [{"enum": principal_kinds},
                                          {"type": "array", "minItems": 1, "items": {"enum": principal_kinds}}]},
                "source_selector": {"type": "object", "additionalProperties": False, "properties": source_selectors},
                "preconditions": {"type": "array", "items": {"anyOf": [
                    {"enum": pre_ids},
                    {"type": "object", "additionalProperties": False, "required": ["id"],
                     "properties": {"id": {"enum": pre_ids}, "description": {"type": "string"}}}]}},
            }}
    nonempty = {"type": "string", "pattern": r"\S"}
    technique = {
        "type": "object", "additionalProperties": False,
        "required": list(REQUIRED_FIELDS),
        "properties": {
            "id": {"type": "string", "pattern": _ID.pattern, "description": "Globally unique, kebab-case, provider-prefixed."},
            "provider": {"enum": list(PROVIDERS)},
            "service": nonempty, "title": nonempty, "summary": nonempty, "mitigation": nonempty,
            "source": {"type": "string", "pattern": "^src/", "description": "hacktricks-cloud page path (#anchor allowed)."},
            "source_revision": {"type": "string"},
            "requires": {"type": "object"},
            "target": {"type": "object", "additionalProperties": False, "required": ["kind"], "properties": {
                "kind": {"enum": sorted(TARGET_KINDS)},
                "selector": {"type": "object"},
                "scope": {"enum": list(SCOPES)},
                "aggregate_as": {"type": "string"},
                "include_service_managed": {"type": "boolean"},
                "outcome": {"enum": sorted(OUTCOMES), "description": "; ".join(f"{k}: {v}" for k, v in sorted(OUTCOMES.items()))},
                "grants": {"type": "array", "minItems": 1, "items": nonempty,
                           "description": "Permission / role names the outcome yields (documentation)."},
                "removes_blockers": {"type": "array", "minItems": 1, "items": {"enum": sorted(KNOWN_BLOCKERS)},
                                     "description": "k8s_admission_control: blocker ids the technique lifts."}}},
            "conditions": {"type": "array", "items": {"anyOf": [
                {"type": "string"},
                {"type": "object", "additionalProperties": False, "required": ["id"],
                 "properties": {"id": {"type": "string"}, "description": {"type": "string"}}}]},
                "description": "Documented caveats (not machine-checked; never change confidence)."},
            "preconditions": {"type": "array", "description": "Machine-checked preconditions (registry ids)."},
            "blockers": {"type": "array", "items": {"anyOf": [
                {"type": "string"},
                {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}, "description": {"type": "string"}}}]}},
            "confidence": {"enum": list(CONFIDENCES)},
            "severity": {"enum": list(SEVERITIES)},
            "references": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
            "pivot_resource_type": {"type": "string"},
            "source_kind": {},
            "source_selector": {"type": "object"},
        },
        "allOf": [{"if": {"properties": {"provider": {"const": p}}, "required": ["provider"]},
                   "then": {"$ref": f"#/$defs/{p}_technique"}} for p in PROVIDERS],
    }
    defs["technique"] = technique
    defs["excluded"] = {"type": "object", "required": ["source", "reason"],
                        "properties": {"source": {"type": "string"}, "reason": {"type": "string"},
                                       "technique": {"type": "string"}, "source_revision": {"type": "string"}}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": JSON_SCHEMA_ID,
        "title": "Cloud privilege-escalation technique catalog file",
        "description": ("A catalog YAML file is a list of techniques (or, for _excluded*.yaml, a list of {source, reason}). "
                        "Generated from peaso/privesc/schema.py; cross-field rules are enforced by validate_entry."),
        "anyOf": [{"type": "array", "items": {"$ref": "#/$defs/technique"}},
                  {"type": "array", "items": {"$ref": "#/$defs/excluded"}},
                  {"type": "null"}],
        "$defs": defs,
    }

def write_json_schema(path=None):
    import json
    target = Path(path) if path else JSON_SCHEMA_FILE
    target.write_text(json.dumps(json_schema(), indent=2, sort_keys=True) + "\n")
    return target

if __name__ == "__main__":  # python -m peaso.privesc.schema [--write-json-schema [path]]
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--write-json-schema":
        print(write_json_schema(sys.argv[2] if len(sys.argv) > 2 else None))
    else:
        print(json.dumps(json_schema(), indent=2, sort_keys=True))
