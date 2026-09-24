# IoT Hub / DPS — Candidate Attacks (not yet lab-fired)

- [ ] Provision a Free-tier (F1) IoT Hub + DPS, create an enrollment GROUP, and live-fire fleet forgery:
      derive a device key for an arbitrary deviceId from the group key and register via
      global.azure-devices-provisioning.net. Confirm + record. Then delete (F1 is free/cheap).
- [ ] Confirm `iotHubs/write` rogue message route to an attacker Event Hub/Storage exfils telemetry and
      which single Activity Log event it emits.
- [ ] Test covert consumer-group persistence durability + visibility.
