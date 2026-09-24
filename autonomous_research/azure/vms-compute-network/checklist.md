# VMs / Compute / Network — Candidate Attacks (not yet lab-fired)

- [ ] Confirm `reimage`-to-execute `customData`/cloud-init on a VMSS instance end-to-end.
- [ ] Test Network Watcher **packet capture** to attacker storage as a wiretap; record whether the
      capture start is the only logged event and whether stored pcap is data-plane (unlogged).
- [ ] Verify Serial Console access requires which exact role + boot-diagnostics storage, and whether
      GRUB single-user works on a stock Ubuntu marketplace image.
- [ ] `applications` (VM Applications) push as a lighter-weight RCE than Run Command — min perms + logs.
