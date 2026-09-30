# MediaConvert — tested

## VERIFIED live two-sided (lab 228478051196, us-east-1) — 2026-09-25  [SHIPPED ml-dataaccess table]
### mediaconvert:CreateJob + iam:PassRole — confused-deputy S3 read/exfil as the passed Role
- Two-sided probe: target role trusting mediaconvert.amazonaws.com; attacker role (CreateJob only, no PassRole).
- NEG: create-job --role <target> -> AccessDeniedException "not authorized to perform: iam:PassRole on resource <target>".
- POS: add scoped iam:PassRole -> create-job ACCEPTED and SUBMITTED (returned Job ARN). Input bucket bogus -> job -> ERROR (no output, no transcoding cost).
- Min-perms: mediaconvert:CreateJob + iam:PassRole over a mediaconvert-trusting role. Job Role reads input S3 (any bucket role can read) + writes output to caller-chosen S3 => read data caller can't + exfil to attacker bucket.
- Teardown: cancel-job (job already ERROR terminal); deleted both IAM roles; verified gone. Endpoint = account-agnostic https://mediaconvert.us-east-1.amazonaws.com.
