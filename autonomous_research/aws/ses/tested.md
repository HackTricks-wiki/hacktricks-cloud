
## ses:PutIdentityPolicy / sesv2:PutEmailIdentityPolicy — cross-account sending-authorization backdoor (SHIPPED, doc+partial-verify)
- Gap: SES post-exploitation page had all send methods + inbound interception but NO section on identity resource-policy sending authorization (only a 1-line cross-account matrix row [28]).
- Attack: attach an identity policy authorizing an attacker-owned EXTERNAL account to ses:SendEmail/SendRawEmail from the victim's verified domain -> send as trusted domain (passes SPF/DKIM/DMARC), persists until policy removed, bounces hit victim reputation.
- Lab-tested validation stages (no verified identity available to finish send): malformed Resource -> InvalidPolicy: Invalid ARN; fake principal acct 111122223333 -> InvalidPolicy: Policy contains an invalid principal (delegate acct must be REAL); valid principal on unverified identity -> InvalidParameterValue: Invalid identity. Must be a verified email address or domain. => gate order = policy-syntax -> principal-validity -> identity-verified. Gated by ses:PutIdentityPolicy alone (no PassRole).
- Precondition for full send: a verified identity (needs DNS/mailbox control, unavailable) -> end-to-end send doc-grounded; mechanism is documented SES sending authorization.
- Residue: none (example-ht-test.com never registered; list-identities empty).
- Where: aws-ses-post-exploitation/README.md new section before inbound interception; refs [24][25].
