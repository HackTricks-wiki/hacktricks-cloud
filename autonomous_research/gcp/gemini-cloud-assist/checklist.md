# Gemini Cloud Assist — open ideas

## Current public coverage

- [x] Map all six current MCP tool schemas and the separate wrapper permission.
- [x] Document saved investigation and immutable revision harvesting with exact audit classes.
- [x] Live-verify direct Cloud Storage object list/get from only
      `roles/geminicloudassist.user`, including its known-bucket limitation.
- [x] Record App Design Center and App Hub mutation permissions as predefined-role review hazards,
      without promoting low-impact design-artifact edits to standalone techniques.
- [x] Remove all synthetic IAM, Storage, API, credential, configuration and local test state.

## Entitled-project authorization matrix

- [ ] In an explicitly Private-Preview-entitled disposable project, repeat each tool with the exact
      underlying permission set, then with `roles/mcp.toolUser`; distinguish wrapper, agent and
      downstream-service denials. Do not infer behavior from the current project's entitlement
      failure.
- [ ] For mutative prompts, verify that human confirmation and downstream IAM are both enforced for
      GKE apply/patch, App Design Center changes and Cloud Operator workflows. Keep any execution
      beyond caller authority private-first.
- [ ] Test server-side-apply conflict forcing only against a synthetic zero-cost namespaced object;
      export the original object, restore it immediately and delete the namespace.

## Scope and information-boundary candidates

- [ ] In an owned multi-project App Hub fixture with synthetic logs/metrics/source, compare
      project-scoped and application-scoped investigations. Treat evidence from a service project
      outside the documented application/caller boundary as private-first.
- [ ] Measure list-response field reduction for a caller with only
      `geminicloudassist.investigations.list`, and confirm revision access remains independently
      denied. Use synthetic investigation content only.
- [ ] Test known-bucket object reads across project, folder, managed-folder, IAM Condition, deny and
      VPC Service Controls boundaries. Expected behavior is ordinary Storage IAM enforcement; any
      cross-boundary read is private-first.
- [ ] Re-diff predefined Gemini Cloud Assist roles on every release. Pay particular attention to
      new non-`geminicloudassist.*` writes or data reads that are not apparent from the role name.
