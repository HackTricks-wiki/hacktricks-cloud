# Access Context Manager — open ideas

Open ideas — Access Context Manager / VPC-SC.

- [ ] **`replaceAll`×2 → `policies.delete` full-teardown chain (UNVERIFIED).** On a DISPOSABLE test
  access policy (never the org's real one), confirm the 3-call sequence empties all access levels and
  service perimeters then deletes the policy, and record which role(s) allow each call. This is a
  destructive-primitive test — use a throwaway policy only, tear it down, and document as
  defense-evasion/DoS, not privesc.
