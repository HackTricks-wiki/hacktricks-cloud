# AWS IoT Core — open ideas

- [x] IoT credential provider role-alias privesc (CreateRoleAlias/UpdateRoleAlias + PassRole) — DONE,
  VERIFIED end-to-end. See tested.md.
- [ ] **RegisterCertificateWithoutCA / RegisterCertificate** persistence — register an attacker CA/cert
  as a durable device identity independent of provisioning; pairs with an assume-capable policy for a
  standing credential-provider foothold. (Cheap to test; low incremental value over the role-alias
  finding — evaluate before writing.)
- [ ] **CreateProvisioningTemplate + fleet provisioning** — a provisioning template with a pre-baked
  role/policy could mint privileged device identities at scale; check whether the template's
  RoleArn/PolicyName is attacker-selectable (PassRole gate?). Potential persistence/privesc.
- [ ] **UpdateCertificate / UpdateCACertificate autoregistration** — flip a CA to auto-register unknown
  certs (SET_AS_ACTIVE) so attacker-signed device certs onboard automatically. Persistence.
- [ ] **AttachPolicy to an existing cert** granting broader iot data-plane / assume perms — lateral/priv
  expansion on already-provisioned identities without creating new certs.
