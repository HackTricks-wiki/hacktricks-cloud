# Privileged Access Manager — tested

Privileged Access Manager (PAM). 4 pages (enum/privesc/persistence/post-exp).

## VERIFIED LIVE — standalone-privesc hypothesis DISPROVEN, reframed
- Anti-delegation guard: `entitlements.create/update` offering role R requires the caller ALREADY hold
  `setIamPolicy` for R → PAM is NOT standalone privesc; it is persistence / attribution-laundering.
- Legacy basic `roles/owner` rejected in entitlements. No-approval entitlement auto-activates in
  seconds via a conditional binding titled "Created by: PAM".
- `grants.create` is not an IAM permission — conferred by entitlement `eligibleUsers` membership.
- Attribution laundering CONFIRMED: `PAMActivateGrant` is a `system_event` with NO principal; the
  escalating `SetIamPolicy` is attributed to the PAM service agent, not the attacker.
