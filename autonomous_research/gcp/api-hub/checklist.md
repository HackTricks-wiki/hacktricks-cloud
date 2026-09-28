# API Hub — open ideas

## Plugin-instance authorization

- [ ] In an already-provisioned disposable API Hub project, create a synthetic custom plugin and
      instance. Give a restricted updater `apihub.plugininstances.update` but not
      `apihub.plugininstances.applyConfig`; PATCH `authConfig`, `additionalConfig`,
      `actions.serviceAccount` and wildcard `*`. Secure results are an invalid update mask or an
      `applyConfig` denial. A credential/config mutation with update alone is private-first.
- [ ] Use a zero-role target account and synthetic Secret Manager value. First give the plugin
      hosting account neither Token Creator nor Secret Accessor; then add each documented grant as a
      positive control. Merely accepting a resource reference is expected. The finding threshold is
      actual secret resolution or target-token use without hosting-account delegation.
- [ ] Test cross-project target service accounts and secrets only between controlled projects.
      Confirm authorization on the referenced target resource rather than trusting `sourceProjectId`,
      which is metadata rather than an access boundary.

## Callback and parser boundaries

- [ ] With a synthetic receiver, record only method/path, header names, marker hashes and decoded
      token issuer/audience/principal—never raw tokens or secret values. Determine callback identity
      and payload anatomy for instance create, execute, enable/disable and delete.
- [ ] Compare public HTTPS, HTTP, non-443, odd-userinfo URLs, controlled 302/307 cross-origin
      redirects and private Cloud Run. A public callback is intended; report only internal/private
      reachability or credential/body forwarding across an origin boundary. Do not probe metadata or
      other unowned endpoints.
- [ ] Make a controlled receiver private and independently grant invoker to the API Hub service
      identity or hosting account. Identify which principal actually invokes it and whether custom
      plugin callbacks otherwise have verifiable authentication.

## Auditability and cleanup

- [ ] Query every `protoPayload.serviceName="apihub.googleapis.com"` record after plugin and instance
      create/update/execute/delete, enable/disable action and manage-source-data. Do not filter only
      on guessed method names. Correlate Cloud Run, Secret Manager, IAM Credentials and Scheduler
      evidence. Confirmed absent control-plane logs are a detection gap, not automatic escalation.
- [ ] As API Hub Viewer, inspect plugin instances for resolved values. Resource names, account emails,
      client IDs and non-secret strings are expected; raw secrets or bearer tokens are not.
- [ ] Cleanup order: delete instance and await its LRO, delete plugin, delete receiver, remove hosting
      account grants, delete synthetic secret/accounts/custom role, then verify plugin/instance lists,
      Cloud Run, IAM, Secret Manager, build artifacts and Cloud Asset. Never provision API Hub solely
      for testing unless the seven-day Apigee soft-delete/cooldown residue is explicitly acceptable.
