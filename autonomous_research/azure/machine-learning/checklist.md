# Azure ML — Candidate Attacks (gap-analysis 2026-09-25, not yet lab-fired)

Wiki: `az-machine-learning-privesc.md` is thorough & lab-verified for compute-as-identity RCE,
datastore/connection listSecrets, endpoint key theft, workspace linked-resource keys.
These `*/action` ops are present in the provider but **NOT documented** — verify-first each:

- [ ] `workspaces/notebooks/storage/download/action` — pull ALL workspace notebooks from the backing
      file share = source code + frequently hardcoded creds/tokens exfil. `upload/action` plants a
      malicious notebook another workspace user opens/runs (code-exec-as-victim). Real disclosure +
      code-plant primitive; workspace itself is free to create (no compute needed to test the file API).
      Find the REST shape (likely `POST .../workspaces/<ws>/notebooks/...` or the notebook file-store SAS).
- [ ] `workspaces/computes/updateDataMounts/action` — attach an attacker datastore (or a victim
      datastore) as a data mount on a compute → data staging/exfil onto compute the attacker controls.
- [ ] `workspaces/computes/applicationaccess/action` (+ `applicationaccessuilinks/action`) — obtain
      access to a compute instance's apps (Jupyter/VS Code/RStudio). Check whether it yields access to
      ANOTHER user's assigned CI (cross-user code-exec) or only your own; ties into the SSO note.

Cost note: AML workspace = free; compute instance/cluster costs — keep min-0 AmlCompute or avoid compute
for the notebook/file-store tests; tear down the workspace after.
