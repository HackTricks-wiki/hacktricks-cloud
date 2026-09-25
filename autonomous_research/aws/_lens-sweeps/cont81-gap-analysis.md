# cont.81 gap-analysis (botocore 423 services vs wiki) — 2026-09-25
Method: diff all botocore service dirs against the wiki corpus.

## ⚠️ METHOD BUG CORRECTED (cont.82)
The first pass used a bash `**` glob **without `shopt -s globstar`**, which only
matches ONE directory level → an incomplete corpus → FALSE "zero mention" results.
Re-run with `rg -qi -- "$svc" src/pentesting-cloud/aws-security/` (recursive) instead.
See [[aws-wiki-gap-analysis-method]].

## SHIPPED (valid)
- mediaconvert:CreateJob + iam:PassRole -> ml-dataaccess table (verified two-sided). LEGITIMATELY NEW (confirmed via rg: only prior mention is an unauth-recon endpoint URL).

## FALSE POSITIVES from the buggy glob — ALREADY COVERED, do NOT re-tread
- opensearchserverless (aoss:CreateAccessPolicy self-grant): fully documented at
  aws-privilege-escalation/aws-opensearch-serverless-privesc/README.md. My re-probe was redundant; NO duplicate written.
- eks-auth:AssumeRoleForPodIdentity + eks:CreatePodIdentityAssociation/UpdatePodIdentityAssociation:
  fully documented in aws-eks-privesc/README.md (incl. the undocumented iam:GetRole requirement and the eks-auth.amazonaws.com event source).

## Reliable true-zero-mention list (rg-based): 130 services -> /tmp/real_gaps.txt
Most are data-plane runtimes, billing/marketplace, legacy, or read-only (no IAM privesc surface).
Role-bearing (PassRole) candidates to vet are extracted in cont82-role-scan.md.
