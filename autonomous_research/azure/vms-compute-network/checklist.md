# VMs / Compute / Network — Candidate Attacks (not yet lab-fired)

- [ ] Live-fire **Run Command** (`virtualMachines/runCommand` / `runCommands/write`) as an identity
      with ONLY that action (no VM write) → confirm SYSTEM/root RCE + exact Activity Log event, and
      whether output is retrievable without `runCommands/read`.
- [ ] Confirm `reimage`-to-execute `customData`/cloud-init on a VMSS instance end-to-end.
- [ ] Test Network Watcher **packet capture** to attacker storage as a wiretap; record whether the
      capture start is the only logged event and whether stored pcap is data-plane (unlogged).
- [ ] Verify Serial Console access requires which exact role + boot-diagnostics storage, and whether
      GRUB single-user works on a stock Ubuntu marketplace image.
- [ ] `applications` (VM Applications) push as a lighter-weight RCE than Run Command — min perms + logs.
