# PCA Connector for SCEP live challenge boundary — 2026-09-26

## Result

The existing book technique remains an **authorization-verified, documentation-supported** expected
attack, not a complete live enrollment proof in this lab. A disposable general-purpose Connector for
SCEP could not reach `ACTIVE` because the account does not have AWS RAM sharing with its AWS
Organization enabled. No password or certificate-enrollment behavior was claimed from these runs.

## Attempts and learned prerequisites

All attempts used unique `ht-scep-*` names in `us-east-1` and a general-purpose root AWS Private CA.

1. A CA certificate valid for exactly 365 days was accepted by Private CA but rejected by the SCEP
   connector moments later because less than one complete year remained. Use more than 365 days for
   a disposable connector fixture.
2. A 730-day CA passed that check, but the connector entered `FAILED` with
   `PRIVATECA_ACCESS_DENIED`. This confirmed that the service requires the documented AWS RAM share
   of the CA to `pca-connector-scep.amazonaws.com` with the blank end-entity certificate permission.
3. Creating that exact resource share failed with `OperationNotPermittedException`: the CA can only
   be shared within the AWS Organization and organization sharing is not enabled in this account.

Enabling organization sharing would be persistent account/organization configuration rather than a
disposable test prerequisite, so the live matrix stopped there. The public book already limits the
minimum-permission statement to the separately verified authorization boundary and cites AWS's SCEP
behavior; it must not be upgraded to “fully live verified” based on these attempts.

## Deferred live matrix

When an organization-enabled account is available:

- create a 730-day disposable general-purpose root CA and the required RAM share;
- create one general-purpose SCEP connector and one challenge;
- assume a role allowing only `pca-connector-scep:GetChallengePassword` on that exact challenge ARN,
  with connector enumeration, challenge creation and `acm-pca:IssueCertificate` denied;
- compare two reads to the password returned at challenge creation without retaining the plaintext;
- query the public connector endpoint with SCEP `GetCACert` without authenticating;
- do **not** enroll a certificate unless needed to validate a materially distinct hypothesis;
- collect CloudTrail evidence, then delete the challenge, connector, RAM share and role; disable and
  schedule-delete the CA with the seven-day minimum window.

Hypotheses to resolve: exact resource matching, whether the challenge remains static across reads,
whether the password is redacted from management logs, and whether unauthenticated `GetCACert` is
observable only when the Connector for SCEP data-event selector is enabled.

## Cleanup verification

Each created CA was disabled and scheduled for deletion. The final CA
`ea0dcd93-8cb7-47a4-9521-d0005b12b6c3` independently described as `DELETED`; AWS retains that
non-active tombstone during its mandatory seven-day restoration window. Final inventories showed:

- no SCEP connector;
- no challenge or test IAM role;
- no test RAM resource share;
- no `AWSServiceRoleForPCAConnectorSCEP` service-linked role;
- no active test CA.

The final failure occurred before resource-share creation, and the harness cleanup still removed the
CA. No test infrastructure remains active or billable.

## Cost note

AWS Private CA general-purpose CAs are currently billed monthly with partial-month proration, and
Connector for SCEP itself has no additional fee. Each CA existed only for minutes and was deleted;
the runs remained well under the authorized cost ceiling.

## References

- https://docs.aws.amazon.com/privateca/latest/userguide/c4scep-considerations-limitations.html
- https://docs.aws.amazon.com/privateca/latest/userguide/connector-for-scep-setting-up.html
- https://docs.aws.amazon.com/privateca/latest/userguide/logging-using-cloudtrail-c4scep.html
- https://aws.amazon.com/private-ca/pricing/
