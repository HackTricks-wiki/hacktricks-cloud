# AI Search — Candidate Attacks (not yet lab-fired)

- [ ] Provision a Free/Basic search service and live-fire `debugSessions` skillset execution to confirm
      a custom Web API skill can be pointed at attacker infra (SSRF) and whether the service MI token is
      reachable (UNVERIFIED). Free tier keeps cost near zero.
- [ ] Confirm `indexes/write` vectorizer-repoint sends embedding calls (with any attached key/MI) to an
      attacker endpoint (UNVERIFIED).
- [ ] Test `searchServices/write` disableLocalAuth flip + network open as an exposure primitive + logs.
