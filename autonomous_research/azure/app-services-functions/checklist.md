# App Services / Functions — Candidate Attacks (not yet lab-fired)

Prefer Consumption Function App (Web quota = 0).

- [ ] Test one env-var loader hook (NODE_OPTIONS=--require or PYTHONPATH+sitecustomize) end-to-end on
      the Consumption app to prove RCE from a single config write; then delete the app.
- [ ] Determine whether `Microsoft.Web/staticSites/config/write` can drive a loader-hook or equivalent
      code-execution path in managed Static Web Apps Functions. Validate file staging/sandbox constraints;
      do not publish the inferred App Service parity until reproduced.
