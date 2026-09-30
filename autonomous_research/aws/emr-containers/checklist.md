# EMR on EKS (emr-containers) — checklist (parked / compute-gated)

- [ ] **`emr-containers:GetManagedEndpointSessionCredentials` execution-role credential vend.** The op
      takes a REQUIRED `executionRoleArn` and returns `credentials` (a session for that role) to use a
      managed endpoint (Jupyter/Livy) on EMR-on-EKS. If iam:PassRole is not enforced (or is enforceable
      by an attacker), this directly vends a chosen execution role's credentials — stronger than the
      documented StartJobRun+PassRole (which only runs a job).
      - **Probe result (2026-09-25):** with a bogus virtual-cluster/endpoint, the service returns
        `AccessDeniedException ... not authorized to perform: emr-containers:GetManagedEndpointSessionCredentials`
        **with no "because" clause and no "on resource"** even when the caller holds `emr-containers:*` +
        `iam:PassRole:*`. => service-side RESOURCE-MASKING: a non-existent virtual cluster is reported as
        AccessDenied, not NotFound. So the two-sided PassRole probe is INCONCLUSIVE without a real
        virtual cluster + managed endpoint.
      - **Gating:** requires an EKS cluster + EMR virtual cluster + a running managed endpoint to test →
        compute-gated (>$5/30min + setup). Deferred to a compute-authorized run. Do NOT ship unverified.
      - Distinct from the documented `emr-serverless:StartJobRun`/`emr-containers:StartJobRun` + PassRole
        RCE technique (aws-emr-serverless-privesc). This is a direct-credential-vend variant.
