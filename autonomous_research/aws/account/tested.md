# AWS Account Management (account:) — tested

## VERIFIED live (lab 228478051196, us-east-1) — 2026-09-25  [SHIPPED aws-account-management-enum.md]
### account:PutAlternateContact — hijack SECURITY/OPS/BILLING contact
- GetAlternateContact SECURITY -> ResourceNotFoundException (none set) => captured original state.
- PutAlternateContact SECURITY -> attacker email accepted (rc 0); GetAlternateContact confirmed stored.
- DeleteAlternateContact SECURITY -> restored to none. Zero residue.
- Min-perm: account:PutAlternateContact. Self-account no accountId; member acct via mgmt/delegated-admin.
- Impact: intercept AWS security/abuse/compromise notifications + operational alerts; credential-independent persistence/evasion (lives in account metadata).

## Doc-grounded (NOT live-fired — destructive/root-restricted)
### account:StartPrimaryEmailUpdate + AcceptPrimaryEmailUpdate = ROOT EMAIL TAKEOVER
- StartPrimaryEmailUpdate sends OTP to the NEW email (attacker-controlled) -> AcceptPrimaryEmailUpdate with that OTP repoints root sign-in email -> root "forgot password" flow = full root, no root pw/MFA needed.
- account:PutContactInformation = rewrite primary contact -> AWS Support account-recovery hijack / BEC.
- GATE: standalone/mgmt account restricts several of these to ROOT user (not delegable to IAM). Member accounts: mgmt/delegated-admin CAN do it on the member => mgmt-access -> own member root. Treat these 3 as root-equivalent.
- Not tested: changing lab account root email is destructive + needs OTP; irreversible-primitive caution.

### account:EnableRegion / DisableRegion
- EnableRegion opens an opt-in Region often outside org CloudTrail/GuardDuty/Config/SCP-region-conditions => blind spot for mining/C2/staging. DisableRegion = disruption. Doc-grounded.

## Prior coverage
- account:GetContactInformation (read, social-eng recon) — pre-existing on enum page. Write side was the gap; now filled.
