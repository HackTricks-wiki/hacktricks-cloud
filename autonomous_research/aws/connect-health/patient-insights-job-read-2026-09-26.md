# Connect Health Patient Insights job read boundary — 2026-09-26

## Result

Verified expected post-exploitation path: `health-agent:GetPatientInsightsJob` on one exact domain ARN plus one exact Patient Insights job ARN returned patient/workflow context and infrastructure locations without domain listing, job creation, S3, HealthLake, or other Connect Health permissions.

The original higher-severity hypothesis was **disproved**: the response model contains `inputDataConfig.fhirServer.oauthToken`, but both administrator and restricted responses omitted that member. No OAuth token was disclosed. This is not a zero-day.

The useful public-book technique is the remaining metadata read, especially because Patient Insights job calls are CloudTrail data events disabled by default.

## Final fixture

All data was synthetic. The final disposable fixture contained:

- Connect Health domain `dom-2mug1otbqso6qri6rjmup`;
- HealthLake SMART-on-FHIR datastore `2f0a83b762cb1a263fb3f6c0f262ac6e`;
- Patient `authorized-test-patient`, clinician `authorized-test-clinician`, and encounter reason `authorized security validation`;
- Patient Insights job `516da26b-ae6a-463b-a08c-18579f294a60`;
- empty versioned S3 output bucket;
- a token-validation Lambda and dedicated HealthLake read role;
- an exact-resource test caller.

The token-validation role required `healthlake:ReadResource`, `SearchWithGet`, `SearchWithPost`, and the newer separate `healthlake:SearchEverything` action because Connect Health reads `Patient/<id>/$everything`. Setup-only create/update permissions were removed before the job started.

## Restricted-caller proof

The caller allowed `health-agent:GetPatientInsightsJob` on both:

```text
arn:aws:health-agent:us-east-1:228478051196:domain/dom-2mug1otbqso6qri6rjmup
arn:aws:health-agent:us-east-1:228478051196:domain/dom-2mug1otbqso6qri6rjmup/patient-insights-job/516da26b-ae6a-463b-a08c-18579f294a60
```

It explicitly denied `health-agent:ListDomains`, `StartPatientInsightsJob`, `DeleteDomain`, `s3:GetObject`, `s3:ListBucket`, and `iam:PassRole`. Exercised domain-list and S3-list controls returned explicit-deny errors.

The exact-resource read succeeded after the job reached `SUCCEEDED` and returned/matched:

- patient ID;
- clinician/user ID;
- encounter reason;
- HealthLake FHIR endpoint;
- S3 output path;
- job status and request metadata.

The submitted date of birth was omitted, so the book does not claim it. The dummy OAuth token was also omitted for both administrator and restricted calls, and only its SHA-256 was ever retained by the harness.

## Failed iterations and reusable setup lessons

1. A generic HTTPS FHIR endpoint was rejected because Connect Health currently supports only HealthLake.
2. An AWS-auth HealthLake datastore plus dummy bearer token was rejected.
3. A SMART datastore accepted the validator token, but an empty store produced `Patient could not be found`.
4. A FHIR upsert initially failed until the setup role included the correct create/update actions and valid SMART v1 scope syntax (`system/*.*`).
5. Direct Patient reads then succeeded, but the job failed until `healthlake:SearchEverything` was added for `Patient/<id>/$everything`.
6. With that exact read action the job started and succeeded.

These were prerequisite/fixture failures, not service-security findings. Every iteration cleaned its unique resources before the next.

## Logging conclusion

CloudTrail Event History showed `CreateDomain` and `DeleteDomain` as default management events from `health-agent.amazonaws.com`, but no `StartPatientInsightsJob` or `GetPatientInsightsJob` events. AWS's current supported-data-event table identifies `AWS::HealthAgent::PatientInsightsJob` as the resource type for Connect Health job API activity. Those calls therefore need an opt-in advanced data-event selector and do not appear in Event History.

Known-ID metadata access has **High** stealth when the account has not enabled that selector.

## Cleanup verification

The final harness deleted the Connect Health domain and waited for absence, deleted the HealthLake datastore and waited for `DELETED`, deleted every S3 version/delete marker and the bucket, deleted the validation Lambda, and deleted all three roles and policies. Independent inventory returned empty arrays for domains, buckets, roles, functions and non-deleted HealthLake datastores.

Historical HealthLake `DELETED` records remain visible; they are terminal control-plane records, not billable active datastores.

## References

- https://docs.aws.amazon.com/connecthealth/latest/APIReference/API_GetPatientInsightsJob.html
- https://docs.aws.amazon.com/connecthealth/latest/APIReference/API_StartPatientInsightsJob.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_connecthealth.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html
- https://docs.aws.amazon.com/healthlake/latest/devguide/reference-fhir-operations-everything.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_healthlake.html
