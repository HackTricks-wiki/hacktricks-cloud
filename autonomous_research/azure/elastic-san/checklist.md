# Elastic SAN — Candidate Attacks (not yet lab-fired)

Cost note: Elastic SAN has a minimum provisioned base capacity that bills hourly — likely OVER the
$5/30min gate. Verify base-unit cost first; prefer DOC-ONLY unless a cheap window exists.

- [ ] If affordable: snapshot a volume, export it, re-mount via iSCSI from an attacker VM to confirm
      block-level exfil with only Snapshot Exporter/Volume Importer roles (UNVERIFIED). Then delete.
