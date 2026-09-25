# Confidential Ledger — Tests Done

Wiki: `az-confidential-ledger-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `ledgers/write` data-plane security-principal self-grant | `ledgers/write` (+read) | **WORKS — lab-verified 2026-09-25 (full chain incl. data-plane)** |
| 2 | `filesExport/action` exfil (append-only tamper caveat) | that action | **UNVERIFIED** |

**Lab record (test, 2026-09-25 — control-plane→data-plane self-grant, full chain):** RG `htrc-clself`,
ledger `htclself18211` (Public/Standard, AmdSevSnp), `ledgerUri https://htclself18211.confidential-ledger.azure.com`.
Created via **control-plane `ledgers/write` only**, naming our SP (`oid 4e4b1002-…`) as `Administrator` in
`aadBasedSecurityPrincipals`. Confirmed the grant is NOT Azure RBAC: `az role assignment list --scope <ledgerId>`
= **empty**, and the data-plane token (`--resource https://confidential-ledger.azure.com`) decoded to
`oid=<our SP>`, **`roles: None`**. Data-plane proof: fetched the CCF TLS cert from
`https://identity.confidential-ledger.core.azure.com/ledgerIdentity/<ledger>` (`ledgerTlsCertificate`) as CA,
then `POST <uri>/app/transactions?api-version=2022-05-13` with the Bearer token → **HTTP 200,
`x-ms-ccf-transaction-id: 2.43`**; `GET .../app/transactions/2.43` read the entry back intact
(`"state":"Ready"`, contents preserved). Also confirmed the **update path**: `az confidentialledger update`
(a plain `ledgers/write`) added a *second* arbitrary principal (Reader) to the running ledger — the
"compromise an existing victim ledger" path. So `ledgers/write` alone (create-seed or in-place update) =
full confidential-data admin, no data-plane grant. Prior wiki note (2026-09-24) had verified only the
control-plane mutation; this adds the data-plane half. **Teardown:** `az group delete htrc-clself`.
Cost: Standard ledger provisioned+deleted within ~20 min — under the $5/30min gate.
