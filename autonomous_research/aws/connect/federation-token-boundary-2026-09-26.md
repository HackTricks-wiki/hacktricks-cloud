# Amazon Connect federation-token boundary — 2026-09-26

## Result

Verified expected attack path: `connect:GetFederationToken`, although classified as a Read action, returns a reusable Connect access token, refresh token, and sign-in URL for the Connect user mapped from the caller's IAM role session name. No Connect discovery or user-management action was needed.

This is expected SAML federation behavior and belongs in the public post-exploitation documentation, not in the private vulnerability directory.

## Fixture

The test created a disposable SAML-backed Connect instance in `us-east-1`, a Connect user named `htfederation` with the built-in `Admin` security profile, and an IAM role assumed with `RoleSessionName=htfederation`. Inbound and outbound calls were disabled. No calls, contacts, recordings, customer profiles, or real customer data existed.

The IAM role explicitly denied:

- `connect:ListUsers`
- `connect:DescribeUser`
- `connect:UpdateUserSecurityProfiles`

All three negative controls remained denied.

## Authorization matrix

The test instance was `ceee6dab-7f42-4f97-9885-50a31f4d5de7`; the Connect user ID was `71fca50f-5ce8-48ce-9c2d-a2c3bdad02be`.

| Allowed resource | Result |
| --- | --- |
| Exact instance ARN | Denied |
| Actual returned Connect user/agent ARN | Denied |
| `Resource: "*"` plus `connect:InstanceId=<exact instance ID>` | Success |

The denial exposed the resource against which IAM evaluated the call:

```text
arn:aws:connect:us-east-1:228478051196:instance/<instance-id>/user/<IAM-role-principal-id>:htfederation
```

That is neither the instance ARN nor the returned Connect user's `.../agent/<user-id>` ARN. It agrees with AWS's documented `.../user/${aws:userid}` SAML policy pattern. The current Service Authorization Reference's `instance` resource-type presentation is therefore easy to misread; the condition-scoped wildcard form is the clearest minimal stable policy.

Successful policy:

```json
{
  "Effect": "Allow",
  "Action": "connect:GetFederationToken",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "connect:InstanceId": "ceee6dab-7f42-4f97-9885-50a31f4d5de7"
    }
  }
}
```

## Credential result

The successful response contained all of:

- the exact expected Connect `UserId` and `UserArn`;
- a non-empty `SignInUrl`;
- a non-empty `AccessToken`;
- a non-empty `RefreshToken`;
- access-token and refresh-token expirations approximately 12 hours after issuance.

Only SHA-256 digests and presence booleans were retained. No token or URL value was stored or opened. Because the target user had the Admin security profile, the returned session represented a Connect administrator even though the IAM caller had only the federation action and was explicitly denied Connect user enumeration/management.

## Detection conclusion

`GetFederationToken` appeared as a default CloudTrail management event with `eventSource=connect.amazonaws.com`, `readOnly=true`, the instance ID in `requestParameters`, and `responseElements=null`. The two denied scope controls appeared with `errorCode=AccessDenied`; the successful condition-scoped call had no error. Its normal use in a SAML sign-in path makes the individual event medium-stealth rather than inherently anomalous. High-signal correlations are an unapproved IAM role, a privileged role-session-name mapping, an unusual source network, or a request for an unexpected instance.

Do not rely on response fields or application logs to inspect token contents. Treat both tokens and the sign-in URL as credentials and suppress them from terminal, CI, and ticket output.

## Cleanup verification

The harness deleted the IAM role and inline policy, deleted the Connect user, deleted the instance, waited until `DescribeInstance` returned not found, and independently listed matching instances and roles. Final inventory returned empty arrays for both. No telephony or customer-data resource was created.

## References

- https://docs.aws.amazon.com/connect/latest/APIReference/API_GetFederationToken.html
- https://docs.aws.amazon.com/connect/latest/adminguide/configure-saml.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnect.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonConnectReadOnlyAccess.html
