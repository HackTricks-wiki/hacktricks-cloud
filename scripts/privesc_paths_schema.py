"""Privilege-escalation catalog loader and strict schema validator.

The registries in this module are the single source of truth for which target
kinds, selector keys, scopes, requirement fields and placeholders the evaluator
implements. The validator rejects anything the evaluator would not understand,
so an unknown selector key can never silently widen or narrow a target set.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

import yaml

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
    "gcp_scope_owner": ("gcp", "entity"),
    "gcp_verified_authority": ("gcp", "entity"),
    "gcp_challenge_foothold": ("gcp", "principal"),
    "azure_managed_identity": ("azure", "principal"),
    "azure_service_principal": ("azure", "principal"),
    "azure_user": ("azure", "principal"),
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
    "azure_challenge_fact": (("azure",), "string", "Exact reviewed Azure technique/source/target/scope evidence; never a definite path."),
    "k8s_challenge_fact": (("k8s",), "string", "Exact reviewed Kubernetes technique/source/target/scope evidence."),
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
    # ---- AWS -------------------------------------------------------------
    "aws_challenge_fact": (("aws",), "string",
        "Exact externally verified technique/source/target evidence from aws_privesc_challenge_evidence. "
        "Missing or incomplete evidence is unresolved; a different source or target never matches."),
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
        "Value {source.arn}: the source is an EC2 container-instance role and the target task role runs (or, without "
        "placement facts, may run: unknown) on an EC2 container instance carrying the source's instance profile."),
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
        "aws_account_admin target is an organization member account (not the management account); unknown without organization_account."),
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
    "gcp_actas_granted_on_target": (("gcp",), "bool_true",
        "Source holds iam.serviceAccounts.actAs on the target SA (SA policy or project/folder/org inheritance)."),
    "gcp_sa_in_scope_of_permission": (("gcp",), "bool_true",
        "Requirements with resource '*' must hold on the target SA's project (or the SA / an ancestor)."),
    "gcp_implicit_delegation_chain": (("gcp",), "bool_true",
        "Target SA is one a delegate chain can mint credentials for: the source holds iam.serviceAccounts.implicitDelegation "
        "on delegate D1, each Di holds implicitDelegation on Di+1 (transitively), and some Dk holds getAccessToken, signBlob "
        "or signJwt on the target. Delegates are not targets themselves (implicitDelegation does not yield their own token)."),
    "gcp_custom_role_bound_to_source": (("gcp",), "bool_true",
        "Target scope (gcp_scope_owner) is one where the source has a binding to a custom role defined in that scope "
        "or an ancestor (projects/<p>/roles/* or organizations/<o>/roles/*)."),
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
    "k8s_node_schedulable": (("k8s",), "bool_true", "Node is not cordoned (spec.unschedulable is not true)."),
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
        "account suffices). The pivot itself is excluded; roles in other accounts are included."),
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
    "azure_challenge_fact": "azure_privesc_challenge_evidence with exact TechniqueId, SourceId, TargetKind, TargetId, TargetScope, EvidenceRef, Status and VerifiedPreconditions",
    "k8s_challenge_fact": "k8s_privesc_challenge_evidence with exact TechniqueId, SourceId, TargetKind, TargetId, TargetScope, EvidenceRef, Status and VerifiedPreconditions",
    "gcp_challenge_fact": "gcp_privesc_challenge_evidence with TechniqueId, SourceId, TargetKind, TargetId, "
                          "TargetScope, Status and VerifiedPreconditions for the exact exploit preconditions",
    "aws_challenge_fact": "aws_privesc_challenge_evidence with exact TechniqueId, SourceArn, TargetKind, TargetId, TargetAccount, Status and VerifiedPreconditions",
    "via_resource_type": "AWS: per-type workload inventories carrying the role (ecs task definitions, glue jobs, sagemaker, ...), "
                         "fully collected in every region: imagebuilder_pipeline (imagebuilder:ListImagePipelines + "
                         "ListInfrastructureConfigurations {instanceProfileName}), sagemaker_user_profile (sagemaker:ListUserProfiles + "
                         "DescribeUserProfile {UserSettings.ExecutionRole} / DescribeDomain DefaultUserSettings.ExecutionRole), "
                         "sagemaker_cluster (sagemaker:ListClusters + DescribeCluster {InstanceGroups[].ExecutionRole})",
    "via_artifact_type": "AWS: artifact consumer mapping (S3 object / ECR repo / SSM document -> consuming role)",
    "consumer_input_writable_via": "AWS: workload input mapping (ECR repo / S3 object -> consuming role); Image Builder: "
                                   "imagebuilder_pipeline (ListImagePipelines + ListInfrastructureConfigurations) in every region",
    "cognito_user_pool_covered_by": "AWS: cognito_identity_pool Roles {Roles, RoleMappings} (cognito-identity:GetIdentityPoolRoles) + "
                                    "Configuration.CognitoIdentityProviders (DescribeIdentityPool) in every region",
    "cognito_user_pool_group_role_covered_by": "AWS: cognito_user_pool Groups {GroupName, RoleArn} (cognito-idp:ListGroups) in every region",
    "codedeploy_group_instance_role_covered_by": "AWS: codedeploy_deployment_group {ec2TagFilters, ec2TagSet, autoScalingGroups} "
                                                 "(codedeploy:BatchGetDeploymentGroups) + instance {Tags, IamInstanceProfile} in the same region",
    "ecs_task_role_on_ec2_capacity": "AWS: ecs_task_definition {taskDefinitionArn, taskRoleArn, compatibilities} + ecs_cluster "
                                     "{registeredContainerInstancesCount} in every region (ecs:DescribeTaskDefinition, ecs:DescribeClusters)",
    "ecs_container_instance_role_in_cluster_covered_by": "AWS: ecs_cluster ContainerInstances {containerInstanceArn, ec2InstanceId} "
                                                         "(ecs:ListContainerInstances + DescribeContainerInstances) and Tasks {taskDefinitionArn, "
                                                         "launchType, containerInstanceArn, overrides.taskRoleArn} (ecs:ListTasks + DescribeTasks)",
    "ecs_task_colocated_with_source_container_instance": "AWS: ecs_cluster ContainerInstances {containerInstanceArn, ec2InstanceId} + Tasks "
                                                         "{taskDefinitionArn, launchType, containerInstanceArn, overrides.taskRoleArn} + instance IamInstanceProfile",
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
                                            "Composer / Dataproc / Cloud Build staging bucket) - not collected",
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
    "ec2_instance_running": (("aws",), "target",
        "The target role is attached (instance profile) to at least one EC2 instance in state pending/running.",
        "AWS: instance {InstanceId, State, IamInstanceProfile} in every region + iam_role InstanceProfileList"),
    "ssm_managed_instance": (("aws",), "target",
        "At least one running EC2 instance of the target role is registered with Systems Manager (PingStatus Online).",
        "AWS: ssm_managed_instance (ssm:DescribeInstanceInformation {InstanceId, PingStatus}) in every region + instance"),
    "ecs_container_instance_exists": (("aws",), "target",
        "An ECS cluster in the target's account has registered EC2 container instances (StartTask needs a host).",
        "AWS: ecs_cluster with describe_clusters {registeredContainerInstancesCount} in every region"),
    "ecs_task_definition_exists": (("aws",), "target",
        "At least one ECS task definition exists in the target's account (the technique overrides an existing one).",
        "AWS: ecs_task_definition in every region"),
    "eks_cluster_exists": (("aws",), "target",
        "At least one EKS cluster exists in the target's account (the technique attaches to an existing cluster).",
        "AWS: eks_cluster (eks:ListClusters) in every region"),
    "source_in_org_management_account": (("aws",), "source",
        "The source lives in the organization management account (only it can call the API).",
        "AWS: organization_account Arn (organizations:ListAccounts) to identify the management account"),
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
REQUEST_CONTEXT_SPECIAL = ("absent", "chosen", "values")
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
    "blocker_removal": "Lifts an enforcement control (target.removes_blockers) that gates other techniques; reaches no principal.",
}
ENTITY_OUTCOMES = ("permission_grant", "role_activation", "scope_control", "application_admin", "blocker_removal")
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
    "target.arn", "target.email", "target.id", "target.scope", "target.namespace", "target.name", "target.account",
    "target.project", "target.node", "target.client_id", "target.application_id",
    "target.resource_arn", "target.attached_resource_arn", "target.artifact_arn", "target.consumer_input_arn",
    "target.saml_provider_arn", "target.trust_anchor_arn", "target.oidc_provider_arn", "target.portfolio_arn",
    "target.rolesanywhere_profile_arn", "target.codebuild_sandbox_arn", "target.redshift_dbuser_arn",
    "target.amplifybackend_token_arn", "target.amplifybackend_backend_arn",
    "target.host_resource", "target.host_resource.content_storage", "target.host_resource.workspace", "target.catalog",
    "target.domain_registration", "target.image_family_project",
    "source", "source.account", "source.arn", "source.id", "source.email", "source.namespace", "source.name",
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
MODEL_BLOCKERS = {"aws": {"ecr_tag_immutability"},
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
    "aws_verified_authority": {"target.scope", "target.account", "target.resource_arn", "target.arn"},
    "aws_account_admin": {"target.scope", "target.account"},
    "aws_identity_center_permission_set": {"target.scope", "target.account", "target.arn", "target.id"},
    "gcp_scope_owner": {"target.scope", "target.project", "target.id", "target.name"},
    "azure_scope_owner": {"target.scope"},
    "azure_dataplane_admin": {"target.scope"},
    "k8s_cluster_admin": {"target.scope", "target.cluster", "target.account", "target.name"},
    "aws_directory_domain_admin": {"target.scope", "target.account"},
    "aws_service_plane_admin": {"target.scope", "target.account", "target.resource_arn", "target.arn",
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
    "target_upn_on_initial_onmicrosoft_domain", "aks_local_accounts_disabled", "aks_entra_integration_enabled",
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
            if kind == "values" and isinstance(arg, list) and arg and all(isinstance(x, str) for x in arg):
                continue
        errors.append(f"{where}: request_context {key}: value must be a string, a list of strings (the requester picks "
                      f"one), {{values: [..]}} (multi-valued key), {{absent: true}} or {{chosen: true}}")
    if choices > MAX_CONTEXT_CHOICES:
        errors.append(f"{where}: request_context has more than {MAX_CONTEXT_CHOICES} value combinations")
    bad = set().union(*(_placeholders(x) for v in value.values() for x in (v if isinstance(v, list) else [v])
                        if isinstance(x, str)))
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
        if kind == "aws_verified_authority" and not selector.get("aws_challenge_fact"):
            errors.append(f"{where}: aws_verified_authority needs selector aws_challenge_fact")
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
        if kind == "azure_verified_authority" and not selector.get("azure_challenge_fact"):
            errors.append(f"{where}: verified authority needs an exact evidence selector")
        if kind == "gcp_verified_authority" and not selector.get("gcp_challenge_fact"):
            errors.append(f"{where}: gcp_verified_authority needs selector gcp_challenge_fact")
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
        if kind == "k8s_remote_cluster" and "k8s_secret_holds_remote_cluster_credential" not in selector:
            errors.append(f"{where}: k8s_remote_cluster targets need selector k8s_secret_holds_remote_cluster_credential")
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
            if "{target.namespace}" not in text and "k8s_sa_in_namespace" not in selector and target.get("scope") != "same_namespace":
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
                elif SOURCE_SELECTOR_KEYS[key][1] == "bound_scope" and value not in (True, "cluster"):
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
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: YAML parse error: {str(exc).splitlines()[0]}")
            files.append({"file": rel, "entries": 0, "valid": 0})
            continue
        if path.name.startswith("_excluded"):
            errors.extend(validate_excluded(data, rel))
            excluded += len(data or [])
            files.append({"file": rel, "entries": 0, "excluded": len(data or [])})
            continue
        if data is None:
            data = []
        if not isinstance(data, list):
            errors.append(f"{rel}: catalog file must be a YAML list")
            continue
        valid = 0
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
        "bound_scope": {"anyOf": [{"const": True}, {"const": "cluster"}]},
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
