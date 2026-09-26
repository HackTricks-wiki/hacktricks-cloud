# Stream Analytics — Candidate Attacks (not yet lab-fired)

- [ ] Live-fire `locations/SampleInput/action` as the low-priv **Query Tester** role to prove a
      job-less outbound connection to an attacker endpoint (SSRF/cred-validation proxy) + logs.
- [ ] Confirm `functions/Write` ML-UDF endpoint repoint exfils tuple data to an attacker HTTP endpoint.
- [ ] Verify MI-attach via `streamingjobs/Write` yields a usable token to a confused-deputy input.
