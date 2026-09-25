# Azure ML — Candidate Attacks (gap-analysis 2026-09-25)

Wiki: `az-machine-learning-privesc.md` (thorough + lab-verified).

- [x] `listNotebookKeys/read` + `listNotebookAccessToken/read` — DONE (documented, lab-verified; see tests-done #1).
- [ ] `workspaces/computes/updateDataMounts/action` — attach an attacker/victim datastore as a data mount
      on a compute → data staging/exfil onto attacker-controlled compute. (needs a compute instance = cost; keep min.)
- [ ] `workspaces/computes/applicationaccess/action` (+ `applicationaccessuilinks/action`) — CI app access;
      check whether it reaches ANOTHER user's assigned compute instance (cross-user code-exec) or only your own.
- [ ] (residue) Pin the exact notebook-service download wire-path behind `notebooks/storage/download/action`
      (proprietary API — studioservice route rejected guessed forms). Low priority; the credential-leak +
      stealth story is already documented without it.
- [ ] (residue) If a Reader test principal ever becomes mintable, fire listNotebookKeys AS Reader to close
      the last verification gap on the min-perms claim.
