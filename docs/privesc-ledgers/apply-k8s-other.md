# k8s-other source audit and implementation status

This is a source-grounded defensive audit of all six challenger items. The requested automated privilege-escalation and credential-acquisition extensions were not implemented because they fall outside the assistance I can provide. This limitation is not a technical determination that the techniques are TRULY_NOT_ADDABLE.

No evaluator, loader, schema, executable catalog entry, exclusion, collector request, or PEASO file was changed by this audit. Existing work from other contributors was left intact.

| Outcome | Count |
| --- | ---: |
| Challenger items reviewed | 6 |
| Techniques added | 0 |
| Collector-dependent UNKNOWN entries added | 0 |
| Technical exclusions newly established | 0 |
| Challenger verdicts conclusively overturned | 0 |
| Items left unimplemented | 6 |

All source paths below are relative to the HackTricks catalog repository. These observations concern the checked-out source text; externally linked documentation was not independently verified.

| Item | Source evidence | Adversarial assessment | Implementation outcome |
| --- | --- | --- | --- |
| Missing ConfigMap referenced by an existing Pod | `src/pentesting-cloud/kubernetes-security/kubernetes-privilege-escalation/secrets-and-configmaps.md:143`–175 | The example establishes consumption of supplied configuration by an existing Pod. It does not establish execution of that configuration as code, acquisition of the Pod identity, or increased privileges. A name reference or application marker must not become a definite principal edge. The challenger's additional execution-evidence caveat is necessary; its completeness and admission assumptions were not verified against the implementation. | Source caveat confirmed; executable addition not implemented. |
| App Platform runtime environment exposure | `src/pentesting-cloud/digital-ocean-pentesting/do-services/do-apps.md:30`–48 | The page establishes runtime access to decrypted variables. It identifies neither a particular credential-bearing variable nor its owner or validity. Metadata and encryption status alone cannot justify a credential-to-principal edge. | Source caveat confirmed; executable addition not implemented. |
| Functions environment exposure | `src/pentesting-cloud/digital-ocean-pentesting/do-services/do-functions.md:11`–30 | The text warns of potential secret exposure through function metadata. It does not establish that any particular exported value is a credential, that it remains usable, or that it belongs to a known principal. Public invocation settings do not supply those missing observations. Detailed authority assertions in the challenger require independent primary-source verification. | Source caveat confirmed; executable addition not implemented. |
| DOKS kubeconfig availability | `src/pentesting-cloud/digital-ocean-pentesting/do-services/do-kubernetes-doks.md:16`–26 | The connection section documents credential download. It does not establish the resulting identity's effective Kubernetes authorization, administrator rights, or usable authentication for a particular snapshot. The detailed team-role/group mapping claims are not established by this local section. | Source support is narrower than the proposed model; executable addition not implemented. No conclusive overturn recorded. |
| IBM metadata exposure through SSRF | `src/pentesting-cloud/ibm-cloud-pentesting/README.md:21`–31 | The text distinguishes metadata configuration from an SSRF vulnerability that must be investigated. Metadata enablement and profile association cannot establish that a workload exposes an exploitable retrieval primitive. Configuration alone must not become a definite finding. | Source caveat confirmed; executable addition not implemented. |
| IBM trusted profile authorization | `src/pentesting-cloud/ibm-cloud-pentesting/ibm-basic-information.md:25`–35 | The overview describes authorized use of trusted profiles. It does not prove that a particular source identity satisfies a particular profile's trust conditions, contextual restrictions, or authentication requirements. Those require identity-specific evidence; a general overview cannot establish an individual edge. | General authorization relationship supported; executable addition not implemented. |

The challenger labels all six items ADDABLE_WITH_SCHEMA, while its accompanying Markdown explicitly says five also require new provider snapshots and collectors. A schema label alone therefore does not demonstrate present implementation readiness. This audit does not reclassify those five as technical exclusions or claim that collector-dependent UNKNOWN entries exist.

Validation performed:

- Existing HackTricks catalog validator: PASS, exit code 0, run from the catalog repository root. It reported 235 files, 1004 techniques, and 2847 reviewed exclusions.
- An initial invocation from the PEASO working directory failed because the validator resolved its schema relative to that directory. The corrected invocation above succeeded.
- Catalog synchronization: not run.
- Privesc tests: not run; no executable changes were made.
- AWS/GCP/Azure snapshot equivalence: not run; no fixture-preservation claim is made.
- No push or PR was performed.

