# NetApp Volumes — open leads

## Recovery-point authorization
- [ ] With pre-existing disposable NetApp resources, test custom roles independently for
      snapshot-source volume creation and backup-source volume creation. Confirm the conditional
      evaluation of `netapp.backups.useReadOnly`, because the `CreateVolume` REST page lists only
      `netapp.volumes.create` even though the distinct source-use permission exists. Do not
      provision a storage pool solely for this test.
- [ ] Capture the audit `authorizationInfo` for both source types and determine whether the source
      recovery point is represented as a separately authorized resource.

## ONTAP proxy
- [ ] On a pre-existing ONTAP-mode pool, send a harmless read command and record the exact
      `protoPayload.methodName`, log name, audit category and resource type. Google's guide says all
      proxy requests are logged, but the public NetApp audit matrix does not enumerate them. Do not
      create an ONTAP-mode pool solely to fill this telemetry gap.
- [ ] Test representative denied paths from Google's published ONTAP filter boundaries and confirm
      whether denials are logged with the requested ONTAP path intact.

## Secret redaction
- [ ] If a disposable Active Directory policy already exists, call get/list with only their
      documented read permissions and verify whether `password` is absent or redacted. Keep the
      credential-disclosure idea out of the book unless plaintext return is reproduced. Do not
      create a domain or NetApp pool solely for this check.
