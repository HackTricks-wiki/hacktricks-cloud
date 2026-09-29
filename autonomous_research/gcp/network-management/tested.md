# Network Management / Network Intelligence Center — tested

## 2026-09-29 — stored Connectivity Test result authorization and remote MCP

- The live unauthenticated Network Management MCP schema exposed exactly four tools: create, get, list and delete Connectivity Tests. Anonymous execution was rejected.
- Created one isolated VPC, subnet, explicit TCP/443 egress deny and no-service-account micro VM, then stored a single VM-to-public-IP Connectivity Test. Its result named the VM, internal IP, interface, project, VPC and exact firewall rule/action/priority/drop cause.
- A fresh principal with Network Management Viewer and no Compute read role successfully recovered the complete stored result through both direct get and list. A control `compute.instances.get` failed, confirming that the current post-October-2024 stored-result boundary is independent of underlying Compute resource access.
- MCP execution first failed on `mcp.tools.call`, then returned the same trace after MCP Tool User propagation. The separate wrapper authorization layer is enforced; no defect was found.
- The reduced principal was denied `networkmanagement.connectivitytests.delete`. Default audit queries showed the always-on create and denied delete events, but no successful direct read or MCP wrapper record with Data Access disabled.
- Deleted the Connectivity Test, VM/disk, firewall, subnet and VPC; removed every IAM grant, key, service account and isolated gcloud configuration; trashed local artifacts; and restored the Network Management API to its original disabled baseline. Exact residue checks were zero.

## Retained public technique

- Stored or newly generated Connectivity Test results as internal path, reachability and enforcement intelligence, explicitly separating high-stealth reads from noisy create/rerun operations.

## Rejected as standalone techniques

- Deleting a stored Connectivity Test is logged and removes diagnostic history, but by itself is too weak to retain as a separate defense-evasion technique.
- Generic public Network Intelligence Center dashboards are not an attack without victim-specific resource visibility.
