# IoT Hub / DPS — Tests Done

Wiki: IoT Hub privesc/post/persistence, unauth `az-iot-hub-dps-unauth`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Leaked enrollment-GROUP symmetric key → derive keys for unlimited arbitrary device IDs (fleet forgery) via global DPS endpoint | none (leaked group key) | DOC-ONLY (unauth) |
| 2 | Device-SAS reuse | leaked device key | DOC-ONLY |
| 3 | Hub-level policy-key escalation ladder (registryRead→registryReadWrite→service→iothubowner) | leaked policy key | DOC-ONLY |
| 4 | `iotHubs/Write` omnibus: SAS-policy backdoor, rogue route exfil, file-upload storage hijack, auth/net rollback, MI attach | `iotHubs/write` | DOC-ONLY |
| 5 | `consumerGroups/Write` covert consumer (persistence) | that action | DOC-ONLY |
| 6 | `certificates/Write` + DPS rogue X.509 CA | those actions | DOC-ONLY |

**Honest negatives:** no anon MQTT; TPM attestation not a mass-forgery vector (unlike group key).
