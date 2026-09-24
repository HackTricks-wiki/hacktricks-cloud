# VMs / Compute / Network — Tests Done

Wiki: `az-vms-and-network-privesc.md`, `az-vms-and-network-post-exploitation.md`, persistence.

**LAB-VERIFIED (control-plane, all isDataAction=false):**
| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | OS-disk swap onto attacker-controlled disk | `virtualMachines/write`+`disks/write` | **WORKS** |
| 2 | Private DNS A-record hijack | `privateDnsZones/A/write` | **WORKS** |
| 3 | NIC `enableIPForwarding=true` (traffic intercept prep) | `networkInterfaces/write` | **WORKS** |
| 4 | Public-IP attach (expose a private VM) | `publicIPAddresses/write`+`networkInterfaces/write` | **WORKS** |
| 5 | Gallery image-version from captured snapshot | `galleries/images/versions/write` | **WORKS** |

**DOC-ONLY (docs + confirmed ops, not fired):** Serial Console GRUB takeover; VMSS model tampering;
Network Watcher packet-capture wiretap; DES/CMK revocation DoS; reimage-to-execute `customData`.

**Public-DNS / traffic-MITM sections (phase 6, catalog-confirmed):** subdomain takeover via
`dnszones/CNAME|A/write` (Stealth High), ACME/DV cert issuance via TXT, MX inbound hijack, SPF/DKIM/DMARC
spoof, foreign-tenant domain-verification TXT takeover, NS delegation hijack, DNS Private Resolver
forwarding-rule hijack; Front Door/CDN origin repoint, rules-engine, App Gateway, Traffic Manager,
Load Balancer backend/NAT.

**Teardown:** `htrc-rg` (VM/gallery) deleted. No residue.

**Lab record (test #4, 2026-09-24):** Run Command re-confirmed. RG `htrc-vmrun`, B1s Ubuntu VM
`htrcvm11931` (no public IP, no NSG). `az vm run-command invoke --command-id RunShellScript` ran as
**root** (uid=0, read `/etc/shadow`) purely via the ARM plane — no SSH, no public IP. Min perm =
`Microsoft.Compute/virtualMachines/runCommand/action` (catalog isDataAction=false) + `virtualMachines/read`.
Activity Log: the `runCommand/action` event IS logged (Started+Accepted, caller), but the executed
**script body/output is NOT** in the Activity Log. Matches the wiki page (`az-virtual-machines-and-network-privesc.md`
lines 511-560, already "verified in lab") — no wiki change. **Teardown:** `az group delete htrc-vmrun`.
