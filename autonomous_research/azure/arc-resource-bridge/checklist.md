# Azure Arc Resource Bridge — Candidate Attacks

## Expected functionality / book candidates

- [x] Identify credential-returning `Microsoft.ResourceConnector` operations and their documented
      response fields. **SOURCE-VALIDATED 2026-09-26:** `listKeys/action` returns customer
      kubeconfigs, SSH material, and artifact profiles; `listClusterUserCredential/action` returns
      partner kubeconfigs and hybrid-connection configuration.
- [x] Enumerate current built-in roles containing either export Action. **PASS 2026-09-26:** Arc
      VMware Private Clouds Onboarding contains `listClusterUserCredential`; Azure Stack HCI
      Administrator, Azure Stack HCI Device Management Role, and Azure Resource Bridge Deployment
      Role contain both.
- [ ] Invoke each Action with only its exact custom-role permission and retain the 200/403 controls.
      Requires a disposable, functioning Arc Resource Bridge and on-premises substrate.
- [ ] Trace `az arcappliance get-credentials` with an exact-Action role to identify any preliminary
      `appliances/read` or other helper permissions required by the wrapper but not the raw Action.
- [ ] Decode every returned kubeconfig and measure `kubectl auth can-i --list`; do not infer
      `cluster-admin` from the API or credential name.
- [ ] Test customer SSH key/certificate reachability and principal scope without modifying the
      appliance. Record whether SSH is enabled and which account/key type is accepted.
- [ ] Determine whether each artifact profile embeds a bearer token/SAS, its expiry, allowed verbs,
      object-prefix isolation, and whether it permits read/list as well as upload. First enumerate
      supported nonempty `artifactType` values; the SDK states that an empty value returns no
      artifact endpoint.
- [ ] Measure Azure Activity Log records and appliance Kubernetes/SSH/relay telemetry for retrieval
      and subsequent credential use.

## Potential security vulnerabilities (private until proven)

- [ ] Authorization mapping mismatch on the legacy
      `2022-04-15-preview/listClusterCustomerUserCredential` route: test whether it is protected by
      the modern `listKeys/action`, another Action, or an unintended generic permission.
- [ ] Returned kubeconfig is more privileged than the nominal customer/partner role or grants
      access across a sibling Resource Bridge.
- [ ] Exported SSH key/certificate authenticates beyond the target appliance or to a more privileged
      principal than intended.
- [ ] Hybrid Listener token is replayable outside its intended endpoint, appliance, tenant, or
      lifetime, or has an overly broad audience/scope.
- [ ] Artifact upload endpoint permits cross-appliance object access, arbitrary overwrite,
      read/list, path traversal, or use after expected credential rotation/expiry.
- [ ] Deleting/recreating a bridge with the same name leaves old exported credentials valid against
      the replacement.

Do not report any item in this section or add it to HackTricks as a vulnerability until a live,
reproducible authorization or scope failure is demonstrated.
