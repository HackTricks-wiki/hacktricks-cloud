# AWS Security Agent / Continuum foundational audit (2026-09-30)

## Scope and live inventory

- Reviewed the current 2026 Agent Space API, CLI model, Service Authorization table and CloudTrail contract.
- Read-only inventory succeeded in both `us-east-1` and `eu-west-1`.
- Both Regions returned zero agent spaces, applications and integrations. No resource, third-party OAuth flow, target domain, pentest, application, IAM role or KMS key was created.
- AWS documents every Security Agent API action as a CloudTrail event.
- Live `ListAgentSpaces` calls in both Regions appeared as `readOnly:true`, `managementEvent:true` events under `securityagent.amazonaws.com`. Empty calls recorded null request/response elements and a wildcard regional `AWS::SecurityAgent::AgentSpace` resource ARN.

## Public techniques and corrections

### Sensitive assessment material

- `GetArtifact` on an exact Agent Space returns full artifact contents for uploaded text, Markdown, JSON/YAML, images, PDFs and Office documents.
- `BatchGetFindings` on an exact Agent Space can return attack scripts, verification-script URL/instructions, environment-variable names and values, code locations, reasoning, customer notes, repository names and remediation diff/PR links.
- `ListArtifacts` / `ListFindings` are optional when exact IDs are recovered from CloudTrail, exported reports, tickets, repository state or the Continuum web application.
- Current authorization dependencies differ: `GetArtifact` lists no dependent action, while `BatchGetFindings`/`ListFindings` list `kms:Decrypt` for customer-managed space encryption.

### Code remediation boundary correction

- `StartCodeRemediation` creates pull requests for selected existing findings from a pentest or code-review job.
- The API does not accept caller-supplied patch content. Impact is trusted generated branch/PR creation, reviewer/CI churn and possible downstream merge—not guaranteed arbitrary code injection or direct execution.
- The exact Agent Space action is sufficient at the Security Agent layer; customer-managed encryption adds `kms:Decrypt` and `kms:GenerateDataKey`. Provider authorization/capability must already allow PR creation.

### Intrusive job and evidence tampering

- `StartPentestJob` sends real payloads only within the existing pentest's verified/configured target boundaries; it is not an arbitrary Internet scanner. Customer-managed encryption adds `kms:Decrypt` and `kms:GenerateDataKey`.
- `UpdateFinding` can downgrade status/risk, and `BatchDeletePentests` destroys pentest records. Both are exact Agent Space writes and list `kms:Decrypt` for a customer-managed space key.
- All techniques now have explicit minimum permissions, impact, stealth and expandable telemetry tables.

## API/version observations

- Installed AWS CLI: `2.34.45`. It exposes the core artifact, pentest, finding, membership and integration commands.
- The current API/authorization references expose newer design-review, code-review, threat-model, validation-run, security-requirement and private-connection operations not all present in the installed command list.
- The public enumeration page now warns researchers to compare the installed model with the current API after the 2026 Agent Instance-to-Agent Space migration.

## Deferred expected-technique tests

1. `CreateMembership`: determine the exact Identity Center/user identifier boundary and whether exact-space permission alone creates durable service access for a controlled existing identity.
2. `CreateOneTimeLoginSession`: this exact-Agent-Space permission-only/current-table action lacks a stable public API page; determine bearer/session output, lifetime, replay, and CloudTrail redaction without exposing tokens.
3. `UpdateIntegratedResources`: test whether exact Agent Space **and** exact Integration permissions are both enforced, and which repository capabilities (code review/remediation/pentest context) can be enabled or removed.
4. `InitiateProviderRegistration`: verify CSRF-state binding, redirect lifetime/replay and whether provider registration can be completed only by the initiating AWS identity/session.
5. `UpdatePrivateConnectionCertificate`: test destination/certificate binding and whether replacement can intercept authenticated traffic or only cause an outage.

## Potential unexpected-defect hypotheses

- One-time login or provider-registration material redeemable by a different principal/session or replayable after intended use.
- Cross-agent-space IDOR on artifact/finding/job batch getters when IDs from one space are supplied with another space.
- Repository/integration IDOR through `UpdateIntegratedResources`, or capability enablement without authorization to both required resource ARNs.
- Presigned verification-script URL or environment-value leakage into CloudTrail despite the documented control-plane logging boundary.

No fixture was available for safe validation, so these remain private hypotheses rather than findings. No AWS vulnerability report was created.

## Cleanup

Empty inventory was rechecked after the read-only sweep. Cleanup was empty by construction.
