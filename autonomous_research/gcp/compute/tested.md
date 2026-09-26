
## compute.instantSnapshots (GA 2024) — annotated (not a new technique)
Zero prior wiki mention, but Instant Snapshots are the same disk-data-copy exfil family as the
documented regular-snapshot exfil (same-region, on-disk storage; cross-project exfil still routes
through a standard snapshot/disk/image conversion). Added a NOTE to the snapshot setIamPolicy exfil
section on gcp-compute-post-exploitation.md flagging compute.instantSnapshots.create /
.setIamPolicy as a distinct, faster/stealthier permission achieving the documented outcome — not a
new exfil path, so a note not a section (no-duplicate bar).
