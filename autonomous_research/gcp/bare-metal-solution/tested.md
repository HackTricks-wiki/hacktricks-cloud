# Bare Metal Solution security research ledger

## 2026-09-28 — official-documentation, discovery, and local SDK audit

This pass used current official Bare Metal Solution, IAM, Cloud KMS, and Cloud Audit Logs
documentation, the live public v2 discovery document, predefined-role metadata, Google Cloud SDK
586.0.0 help, and the installed `gcloud bms nfs-shares update` source. No BMS, KMS, NFS, Compute,
network, IAM, or other cloud resource was created, changed, or deleted.

### Retained techniques

1. **Initial-password recovery (privilege escalation).** The standard `Instance.loginInfo` path
   points to a Secret Manager credential (usually `customeradmin`) and the Google-provided customer
   credential-access service account. A principal with direct `secretmanager.versions.access`, or
   `iam.serviceAccounts.getAccessToken` on that service account, can retrieve a still-valid initial
   password; `baremetalsolution.instances.get` is necessary only to discover the instructions when
   the identifiers are not already known. The optional Preview `LoadInstanceAuthInfo` path returns
   `root`/`customeradmin` encrypted initial passwords and their KMS key versions; it requires
   `baremetalsolution.instances.loadAuthInfo` plus
   `cloudkms.cryptoKeyVersions.useToDecrypt`. Both branches cross from Google API authorization to
   OS access only for the affected server, only while the initial password remains valid, only with
   network reachability, and subject to local OS/SSH login policy.
2. **NFS allowlist expansion (post-exploitation).** `UpdateNfsShare` can add a routed client CIDR
   with read-only or read-write access. The supported gcloud helper first gets the existing share and
   then patches the complete allowed-client list, so its minimum is `nfsshares.get` + `.update`;
   `operations.get` is needed only when the helper polls instead of using `--async`.

### Removed or rejected claims

- **Project SSH-key registration gives root on every server:** false. Registering an SSH-key
  resource does not install it on existing servers. Server login keys are selected during Linux
  provisioning or reimage and map to `customeradmin`; project keys also authenticate the separate
  interactive serial-console transport.
- **Serial-console enablement alone gives OS access:** unsupported. The documented action enables
  the transport. It does not promise an OS-authentication bypass. A known local credential or a
  separate OS/boot weakness remains necessary.
- **No-root-squash plus SUID automatically gives root on a BMS server:** false. These settings
  preserve client UID 0 and allow set-user-ID semantics on the export. They do not create a victim
  execution path.
- **Snapshot restore provides an offline disk copy:** false. The v2 method restores the snapshot to
  its parent volume in place. Snapshot metadata and LUN descriptions do not expose block content.
- **Reset, stop, detach, delete, evict, or restore as post-exploitation techniques:** removed under
  the no-garbage taxonomy because their supported effect is availability loss, deletion, or rollback.
- **Generic on-host credential grep:** removed as a generic consequence after OS compromise, not a
  distinct BMS control-plane technique.
- **Patch SSH keys onto a live server:** the public schema exposes `ssh_keys`, but official product
  guidance supports setting them during provisioning or reimage. Reimage overwrites boot
  configuration and is not a non-destructive access-injection primitive.
- **Attach a victim volume for offline reading:** IAM metadata contains historical/current
  `instances.attachVolume` permissions, but the public v2 discovery surface has no attach method.
  The documented console workflow is not enough to publish an exact callable primitive.

### Permission and telemetry corrections

- The standard password route can emit BMS `GetInstance` (`ADMIN_READ`), IAM Credentials
  `GenerateAccessToken` (`ADMIN_READ`), and Secret Manager `AccessSecretVersion` (`DATA_READ`). The
  Preview route emits `LoadInstanceAuthInfo` (`ADMIN_READ`) and Cloud KMS `AsymmetricDecrypt`
  (`DATA_READ`). All are Data Access and disabled by default.
- `GetNfsShare` is Data Access `ADMIN_READ` and `UpdateNfsShare` is Data Access `DATA_WRITE`, not
  always-on Admin Activity. This materially changes the stealth rating.
- The NFS REST method and CLI return an operation, but the official BMS audit catalog marks
  `UpdateNfsShare` as non-LRO and lists `GetOperation` as producing no audit log. The book therefore
  does not promise a start/completion audit pair.
- NFS reads and OS logins are not BMS API audit methods. Customer endpoint, NFS, bastion, VPN, or
  network telemetry can still detect them; no claim of global invisibility is made.
- Current IAM role output did not expose `instances.loadAuthInfo` in an expanded predefined-role
  permission list even though the API and audit catalog name the permission. The book states the
  exact permission and intentionally does not claim a particular predefined role includes it.
- Reciprocal review caught the missing standard `loginInfo`/Secret Manager recovery branch and an
  overbroad password-rotation claim. The published boundary now distinguishes discovery from
  credential access and treats a recovered password as useful only while still valid; it does not
  promise that direct `root` login is enabled.

### Read-only inspection performed

- `gcloud bms ssh-keys add --help`
- `gcloud bms instances enable-serial-console --help`
- `gcloud alpha bms instances auth-info --help`
- `gcloud alpha bms instances update --help`
- `gcloud bms nfs-shares update --help`
- `roles/baremetalsolution.admin` and `roles/baremetalsolution.editor` metadata
- `https://baremetalsolution.googleapis.com/$discovery/rest?version=v2`
- Installed SDK source for the NFS-share update helper, confirming its preliminary Get and optional
  operation polling
