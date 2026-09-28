# Dataproc — open ideas

- [ ] On a pre-existing disposable Serverless workload, live-verify which documented custom-image
  dependency/environment hooks execute before user code and which driver/runtime logs expose them.
  Do not create a billable cluster solely for this telemetry check.
- [ ] If a pre-existing Component Gateway cluster is available, correlate Knox/Jupyter records with
  a harmless notebook action and the resulting target-service audit entry.
- [ ] Recheck runtime 3.x role prerequisites when Google retires the compatibility Worker-role path.
