# AWS IoT Core — tested

## IoT credential provider role-alias privesc — VERIFIED END-TO-END (cont.65) [net-new]

- **Technique:** `iot:CreateRoleAlias`/`UpdateRoleAlias` (+ `iam:PassRole`) points a role alias at any
  `credentials.iot.amazonaws.com`-trusting IAM role. An attacker-minted X.509 cert with a policy
  allowing `iot:AssumeRoleWithCertificate` on the alias then fetches the role's FULL temp creds from
  `https://<prefix>.credentials.iot.<region>.amazonaws.com/role-aliases/<alias>/credentials` (mutual TLS).
- **End-to-end VERIFIED:** target role (perm = only s3:ListAllMyBuckets) vended creds ->
  get-caller-identity = assumed-role/ht-iotcp-target/<certid>; s3:ListAllMyBuckets OK; iam:ListUsers
  DENIED -> creds carry the ROLE's own policy, NO session-policy narrowing by the credential provider.
- **PassRole gate VERIFIED:** CreateRoleAlias passing a role not allowed by iam:PassRole ->
  "not authorized to perform: iam:PassRole". Two-perm requirement confirmed.
- **Min perms:** iot:CreateRoleAlias|UpdateRoleAlias + iam:PassRole (role trusting
  credentials.iot.amazonaws.com) + iot:CreateKeysAndCertificate + iot:CreatePolicy + iot:AttachPolicy
  (an existing assume-capable device cert removes the last three).
- **Persistence angle:** the held cert keeps re-vending fresh role creds from the internet-facing
  endpoint with no further control-plane calls; the vend itself produces NO CloudTrail event.
- **Teardown:** role alias, cert (INACTIVE+force-delete), policy, target role, probe roles ALL deleted
  and verified (ResourceNotFoundException / NoSuchEntity). Zero residue.
- **Wiki:** aws-iot-core-enum.md new section "Privilege escalation: iot:CreateRoleAlias + iam:PassRole
  -> vend any IAM role via the IoT credential provider". Refs [20][21][22].
