# VMware Engine security research ledger

## 2026-09-28 — official documentation, public API schema, IAM, and local SDK audit

This pass used current official VMware Engine IAM, REST, audit-logging, permission-model,
management-appliance, network, and syslog documentation; the public v1 discovery document;
predefined-role metadata; and installed Google Cloud SDK 586.0.0 help/source. No VMware Engine,
vCenter, NSX, network, IAM, logging, or other cloud resource was created, changed, or deleted.

### Retained techniques

1. **Show generated vCenter/NSX credentials (privilege escalation).**
   `privateClouds.showVcenterCredentials` and `.showNsxCredentials` return a `Credentials` object,
   crossing from Google Cloud IAM into the VMware management plane. The effect is bounded by the
   default `Cloud-Owner-Role` for vCenter and Enterprise Admin for NSX, plus network reachability.
   A directly changed appliance password can make Google's stored value stale. In that case, a
   reset followed by show is a valid compound chain, but reset alone does not disclose the new
   password.
2. **Private-cloud IAM self-grant (privilege escalation).**
   `privateClouds.setIamPolicy` can add `roles/vmwareengine.admin` to one private-cloud resource,
   then the caller can use the credential-show methods. The documented stable gcloud group lacks
   `add-iam-policy-binding`; the book now uses the supported REST policy methods and preserves
   existing bindings, conditions, policy version, and `etag`.
3. **vCenter VM clone for offline data access (post-exploitation).** The default CloudOwner role
   has documented VM clone/snapshot, datastore, disk/file, device, console, and power privileges.
   A powered-off copy can be inspected without logging into or executing inside the original guest.
4. **NSX segmentation/MITM abuse (post-exploitation).** The generated NSX admin's Enterprise Admin
   authority can change gateway/distributed firewall policy, routing, NAT, load balancing, and
   segments. The book keeps the impact bounded to the objects/flows under the compromised NSX
   authority and explicitly accounts for appliance logs.

### Removed or corrected claims

- **Credential show is Admin Activity and always logged:** false. Both show methods are
  `ADMIN_READ` Data Access and are disabled by default.
- **CloudOwner is full/unrestricted vCenter Administrator:** false. Google retains full
  administrative authority. CloudOwner receives the documented, powerful but restricted
  `Cloud-Owner-Role`.
- **Reset returns a fresh password:** false as a standalone claim. The reset methods return an LRO;
  the replacement is read with the corresponding show method. Reset-only custom permission is not
  a privilege-escalation technique.
- **`gcloud vmware private-clouds add-iam-policy-binding`:** removed because that stable command
  does not exist. The private-cloud REST IAM methods are supported.
- **`govc guest.run` bypasses guest authentication:** false. The shown command itself supplied a
  guest username/password. Guest-operation privileges do not automatically provide guest OS
  credentials. Offline clone/reconfiguration is the defensible no-guest-login path.
- **Every vCenter/NSX action is invisible:** overbroad. These actions are outside VMware Engine
  Cloud Audit Logs, but they generate appliance evidence and can be centrally visible when vCenter,
  ESXi, or NSX syslog is forwarded and ingested.
- **Raw VMDK download command guarantees full-disk exfiltration:** removed. The old command could
  select only a descriptor, encounter powered-on locks, or behave differently on vSAN. The retained
  technique uses the explicitly documented clone/file/disk privileges without promising that one
  path works for every datastore layout.
- **Create external address/rule as post-exploitation:** removed from this page because it creates
  reachability rather than directly yielding sensitive data and duplicates the persistence page.
  The old command paths/flag names were also invalid in the current SDK.
- **Private-cloud/cluster deletion:** removed under the no-garbage taxonomy because it is a
  destructive availability action, not sensitive-data post-exploitation.

### Permission and telemetry corrections

- `ShowVcenterCredentials` and `ShowNsxCredentials` are Data Access `ADMIN_READ`, non-LRO, and not
  logged by default. This makes a direct show high stealth when Data Access is not enabled.
- `ResetVcenterCredentials` and `ResetNsxCredentials` are Admin Activity `ADMIN_WRITE` LROs. A
  reset is always logged and usually has start/completion entries; it is a noisy prerequisite only
  when a shown credential is stale.
- `GetIamPolicy` is Data Access `ADMIN_READ`; `SetIamPolicy` is Admin Activity `ADMIN_WRITE`.
- Current role metadata places the show/reset permissions in VMware Engine Admin, VMware Engine
  Editor, VMware Engine Service Admin, and basic Editor/Owner. Neither current viewer role carries
  them. `privateClouds.setIamPolicy` is also present in IAM Security Admin but not either Editor.
- VMware-plane login, task, clone, datastore, firewall, routing, and NSX Policy API actions are not
  `vmwareengine.googleapis.com` Cloud Audit events. vCenter/ESXi/NSX logs are separate and must be
  forwarded/ingested for centralized visibility.

### Read-only inspection performed

- `gcloud iam roles describe` for VMware Engine viewer/editor/admin, Service Viewer/Admin, basic
  Editor, and IAM Security Admin
- `gcloud vmware private-clouds vcenter credentials describe --help`
- `gcloud vmware private-clouds vcenter credentials reset --help`
- Current external-address, external-access-rule, and network-policy SDK help
- Installed SDK implementation for credential reset, confirming it returns/waits on an operation
- `https://vmwareengine.googleapis.com/$discovery/rest?version=v1`
- Official VMware Engine audit catalog and REST method references
- Official vSphere permission-model, security, management-appliance, networking, and syslog guides
