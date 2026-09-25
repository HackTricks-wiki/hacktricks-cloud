# App Services / Functions — Candidate Attacks (not yet lab-fired)

Prefer Consumption Function App (Web quota = 0).

- [ ] Provision a Consumption Function App and live-fire `WEBSITE_RUN_FROM_PACKAGE=<attacker URL>` with
      ONLY `sites/config/write`: confirm remote package deploy + RCE, capture exact Activity Log entry.
- [ ] On the same app, confirm `hostruntime` ARM-proxy returns the master key and that anonymous
      function invoke works when authLevel=anonymous.
- [ ] Test one env-var loader hook (NODE_OPTIONS=--require or PYTHONPATH+sitecustomize) end-to-end on
      the Consumption app to prove RCE from a single config write; then delete the app.
