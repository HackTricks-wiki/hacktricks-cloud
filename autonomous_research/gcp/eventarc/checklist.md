# Eventarc follow-up checklist

Last updated: 2026-09-28

## Documentation audit

- [x] Reduce the post-exploitation page to distinct, useful Standard/Advanced primitives.
- [x] Give every retained H3 exact prerequisites, bounded Potential Impact, categorical Stealth,
      and an expandable logs table.
- [x] Correct Standard default-service-account behavior and distinguish trigger identity,
      Eventarc/provider service agents, and destination runtime permissions.
- [x] Replace inferred publishing telemetry with the dedicated current Eventarc Publishing audit
      catalog.
- [x] Retain the one genuine Eventarc credential-persistence chain and update the service
      enumeration page.
- [x] Record why audience-bound Standard OIDC capture and Google-channel CMEK changes are not
      standalone book techniques.
- [x] Remove the false Standard-trigger runtime-identity persistence claim and keep route hijacking
      in post-exploitation rather than persistence.
- [x] Verify gcloud 586.0.0 update helpers (`Get` before `Patch`) and distinguish their `.get`
      requirement from the direct API minimum.
- [x] Add IAM Credentials token-mint telemetry and the default-`NONE` Advanced platform-logging
      boundary to every retained OAuth-token technique.
- [x] Enforce the Advanced same-region rule and same-project enrollment/pipeline rule while
      preserving documented cross-project bus support.

## Safe live validation frontier

- [ ] In a disposable project where Eventarc is already enabled, create a token-authenticated
      pipeline as an administrator, then give a second principal only `eventarc.pipelines.update`.
      Test whether a destination-only PATCH that preserves the authentication service account
      requires a fresh `iam.serviceAccounts.actAs` check. Keep a true boundary failure private.
- [ ] Validate the Standard omitted-service-account path under a minimum custom role and confirm
      that attaching the default Compute Engine service account still enforces `actAs`.
- [ ] Capture the exact request fields and principal attribution for Standard create/update,
      Advanced pipeline/enrollment LRO start/completion, and Eventarc service-agent delivery.
- [ ] Compare message-bus `Publisher.Publish` with the documented no-log channel and
      channel-connection methods under explicitly enabled Data Write logging.
- [ ] Test VPC Service Controls, organization policy, and egress behavior for an Advanced public
      HTTPS destination; do not describe an external receiver as a perimeter bypass without proof.
- [ ] Capture an OAuth-authenticated delivery at a disposable external HTTPS receiver and verify
      that the service does not enforce the documented `*.googleapis.com` recommendation as a
      hostname restriction; record token lifetime, scope, and `GenerateAccessToken` attribution.
- [ ] Validate cross-project `messageBuses.use` and pipeline-project versus bus-project audit
      placement with a harmless event and exact resource-level grants.

## Cleanup contract for every live fixture

- [ ] Delete enrollments before their pipelines and buses.
- [ ] Delete every Standard trigger and verify its managed Pub/Sub subscription/topic state.
- [ ] Delete attacker receiver workloads and logs/captures containing bearer tokens.
- [ ] Remove every temporary service account, role binding, custom role, network attachment, topic,
      and destination resource.
- [ ] Restore Eventarc/Eventarc Publishing and any provider APIs to their original enabled state;
      verify Cloud Asset Inventory, IAM, Eventarc, Pub/Sub, Run, and Workflows contain no fixture ID.
