# Integration Connectors — open ideas

- [ ] With an existing disposable connection, compare `BASIC` and `FULL` response fields for a
  viewer and confirm whether any credential material beyond Secret Manager resource references is
  returned. Treat unexpected secret plaintext as a private vulnerability report.
- [ ] Verify the exact audit entries and principal attribution for v2 action, SQL, entity and
  event-listener calls under minimum permissions. Test only synthetic data and owned backends.
- [ ] Review `endUserAuthentications` and the newer connection toolspec-override methods for
  privilege boundaries, credential exposure and resource-IAM scoping as their public IAM
  documentation matures.
- [ ] Test whether connector-specific generic URL, SQL, filter or action parameters can escape the
  administrator's configured destination or authorization boundary. Use only owned receivers and
  report a cross-tenant or credential-exfiltration bypass privately before public documentation.
