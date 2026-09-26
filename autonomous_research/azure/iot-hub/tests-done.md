# IoT Hub / DPS — Tests Done

Wiki: IoT Hub privesc/post/persistence, unauth `az-iot-hub-dps-unauth`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Leaked enrollment-GROUP symmetric key → derive keys for unlimited arbitrary device IDs (fleet forgery) via global DPS endpoint | none (leaked group key + idScope) | **WORKS** — lab-verified 2026-09-24 |
| 2 | Device-SAS reuse | leaked device key | DOC-ONLY |
| 3 | Hub-level policy-key escalation ladder (registryRead→registryReadWrite→service→iothubowner) | leaked policy key | DOC-ONLY |
| 4 | `iotHubs/Write` omnibus: SAS-policy backdoor, rogue route exfil, file-upload storage hijack, auth/net rollback, MI attach | `iotHubs/write` | DOC-ONLY |
| 5 | `consumerGroups/Write` covert consumer (persistence) | that action | DOC-ONLY |
| 6 | `certificates/Write` + DPS rogue X.509 CA | those actions | DOC-ONLY |

**Honest negatives:** no anon MQTT; TPM attestation not a mass-forgery vector (unlike group key).

**Lab record (test #1, 2026-09-24):** RG `htrc-iotforge`, F1 hub `htrchub10935` (free) + DPS `htrcdps28354`.
Created symmetric enrollment group `forgegroup`, retrieved its primary key + `idScope=0ne012D9954`.
Derived a device key for a never-enrolled ID `ceo-laptop-forged-16363` via `compute-device-key`, then
`az iot device registration create --enrollment-group-id forgegroup` → `status: assigned`,
`assignedHub: htrchub10935.azure-devices.net`. Forged device showed **enabled** / `sas` in the hub
registry; `send-d2c-message` with the derived key → accepted (live DeviceConnect foothold). **Teardown:**
`az group delete htrc-iotforge` (removes hub + DPS + enrollment group). No standing residue.
