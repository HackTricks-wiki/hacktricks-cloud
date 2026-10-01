# Amazon Recycle Bin snapshot restoration audit — 2026-09-30

## Result

Verified a useful EC2/EBS post-exploitation path: `ec2:ListSnapshotsInRecycleBin` enumerates deleted snapshots and exact-snapshot `ec2:RestoreSnapshotFromRecycleBin` resurrects one without `DescribeSnapshots`. The restored snapshot retains the same ID and becomes an ordinary completed snapshot that can be mounted, read through EBS direct APIs, copied, or shared when the caller also has those downstream permissions.

## Service boundaries

- Recycle Bin rule management uses `rbin.amazonaws.com` and the `rbin:*` namespace.
- Deleted-resource inventory and restore use EC2 actions and `ec2.amazonaws.com`, not `rbin:*`.
- `rbin:ListRules` and the three `ec2:List{Volumes,Snapshots,Images}InRecycleBin` actions are wildcard-only.
- `ec2:RestoreSnapshotFromRecycleBin` supports the accountless snapshot ARN `arn:aws:ec2:<region>::snapshot/<id>`.
- When the snapshot genuinely existed in Recycle Bin, a session limited to its exact accountless ARN restored it successfully. A session without `DescribeSnapshots` remained unable to describe it.
- DryRun against a nonexistent ID evaluated authorization against `arn:aws:ec2:<region>::snapshot/*`; do not use that synthetic behavior to claim exact live resources are unscopable.

## Live test

Preflight returned no rules or recycled volumes/snapshots/images. The final controlled cycle used:

- one unlocked Region-level one-day snapshot retention rule;
- one unattached 1 GiB `gp3` volume;
- one unencrypted empty snapshot tagged `Owner=HackTricksResearch`.

After snapshot completion, the source volume was deleted, then the snapshot was deleted into Recycle Bin. A restricted session had only:

```json
{
  "Effect": "Allow",
  "Action": "ec2:RestoreSnapshotFromRecycleBin",
  "Resource": "arn:aws:ec2:us-east-1::snapshot/snap-0efb8dc1aa761a120"
}
```

That session restored the live retained snapshot successfully. In the preceding full-flow cycle, a session with list access plus restore on the Region snapshot wildcard enumerated the retained ID, was denied `DescribeSnapshots`, and restored it. Administrator readback reached `completed` and preserved the original source volume ID, 1 GiB size, description, unencrypted state, and user tag.

## Negative and edge branches

| Branch | Result |
| --- | --- |
| Exact live accountless snapshot ARN | Succeeded |
| Account-qualified snapshot ARN | Wrong ARN form; denied |
| Exact nonexistent snapshot ARN in DryRun | Authorization evaluated against the Region snapshot wildcard |
| `DescribeSnapshots` absent | Restore still succeeded; Describe was denied |
| First tag-rule attempt | Snapshot was permanently deleted instead of retained despite rules reporting available, consistent with documented first-rule eventual consistency; no restore conclusion drawn |
| Region-level rule after activation delay | Snapshot reliably entered Recycle Bin |
| Metadata/tags after restore | Source volume ID, size, description, encryption flag, ID and user tag preserved |
| Locking a retention rule | Not tested: minimum unlock delay is 7 days and would intentionally violate cleanup requirements; generic cost/retention DoS was not strong enough for separate book coverage |

The first failed retention attempt is important operationally: rule `available` is not proof the first rule has propagated. Do not delete a valuable validation resource until a safe sacrificial control confirms retention.

## Impact boundary

Restore alone recovers the snapshot object. Reading plaintext additionally requires one of the ordinary snapshot-consumption paths, such as volume creation/attachment or EBS direct APIs, plus applicable KMS authorization for encrypted snapshots. This is expected AWS functionality, not a private vulnerability, but it defeats the assumption that an ordinary deletion has immediately destroyed data while a retention rule still applies.

## Telemetry

- `CreateRule`/`DeleteRule`: default management events from `rbin.amazonaws.com`.
- `DeleteSnapshot`, `ListSnapshotsInRecycleBin`, and `RestoreSnapshotFromRecycleBin`: default management events from `ec2.amazonaws.com`.
- Event History showed restricted-session list/restore attempts and DryRun authorization probes after indexing delay.
- Subsequent `CreateVolume`/`AttachVolume` calls are default management events. EBS direct `ListSnapshotBlocks`/`GetSnapshotBlock` require optional snapshot data-event logging.

## Cleanup

No rule was ever locked. Every unlocked primer/tag/Region rule from all three cycles was deleted. Every test volume and active/restored snapshot was deleted after its rule was removed. Final independent inventories returned:

- zero `EBS_VOLUME`, `EBS_SNAPSHOT`, and `EC2_IMAGE` retention rules;
- zero `Owner=HackTricksResearch` volumes and snapshots;
- zero HackTricks-described snapshots in Recycle Bin;
- exact final active and recycled counts of zero for each test snapshot.

No AMI, instance, attachment, KMS key, role, bucket, or other persistent fixture was created.
