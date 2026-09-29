# Cloud CLI Execution — open leads

- [x] Resolve the Preview service identifier and map anonymous tool discovery.
- [x] Verify the `mcp.tools.call` outer gate independently from downstream IAM.
- [x] Exercise safe `gcloud` and `bq` controls and bound the documented command/file guardrails.
- [ ] In an otherwise idle disposable project, briefly enable MCP Data Access logging and capture
      the exact method/resource fields for both tool calls; restore the original audit policy.
- [ ] Validate the execution-project/target-project split in an owned two-project fixture and test
      IAM Conditions on the execution-project `mcp.tools.call` grant.
- [ ] Recheck the Preview command denylist after releases. Treat any path that executes a blocked
      credential-producing command, shell primitive, or caller-token export as private-first.
- [ ] Map organization-policy and VPC Service Controls behavior for the execution API separately
      from the downstream APIs, without weakening controls on a shared project.
