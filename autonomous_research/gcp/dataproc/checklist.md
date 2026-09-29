# Dataproc — open ideas

- [x] Map the 16 live global/regional MCP tools and identify the undocumented
      `analyze_batch_service` addition.
- [x] Verify Viewer-level batch get against a synthetic failure and separately deny Logging and
      Storage output access.
- [x] Run Viewer-level `AnalyzeBatch` through MCP and confirm the synthetic driver canary is not
      transited into its diagnostic response.
- [ ] Re-test `AnalyzeBatch` on a purpose-built workload with a known supported performance issue
      to characterize recommendation/insight detail and retention without using customer data.
- [ ] Diff global and regional MCP tool schemas each release; watch for job submit, session-template
      or Spark-application tools that would add new code-execution or data-read paths.
- [ ] On a pre-existing disposable Serverless workload, live-verify which documented custom-image
  dependency/environment hooks execute before user code and which driver/runtime logs expose them.
  Do not create a billable cluster solely for this telemetry check.
- [ ] If a pre-existing Component Gateway cluster is available, correlate Knox/Jupyter records with
  a harmless notebook action and the resulting target-service audit entry.
- [ ] Recheck runtime 3.x role prerequisites when Google retires the compatibility Worker-role path.
