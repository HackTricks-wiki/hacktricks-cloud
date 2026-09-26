# Lambda — checklist (untested / parked ideas)

- [ ] Cross-account fn hijack via resource-policy (`lambda:AddPermission`) granting Invoke to an
      attacker principal on a fn bound to a privileged role — invoke path only (no role change).
      Likely already covered by AddPermission technique; confirm no repoint gap.
- [ ] `lambda:PutFunctionEventInvokeConfig` destination abuse (async invoke result → SNS/SQS/EventBridge
      the attacker controls) as exfil channel. Low novelty — verify not already noted.
- [ ] EventSourceMapping onto an attacker-writable stream as a persistence trigger (auto-invoke as the
      execution role). Check vs existing CreateEventSourceMapping technique.
- [ ] `lambda:UpdateFunctionConfiguration` VPC/subnet/SG repoint to relocate a fn into a target VPC for
      lateral movement (needs ec2 perms too). Compute-gated to prove end-to-end.
- [ ] SnapStart / recursion-loop abuse for cost or persistence — likely garbage-tier, deprioritize.
