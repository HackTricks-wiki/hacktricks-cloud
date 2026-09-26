# Marketplace Commerce Analytics `StartSupportDataExport(roleNameArn)` review

## Verdict — retired PII export, not PassRole

`marketplacecommerceanalytics:StartSupportDataExport` was a genuine seller-side export of AWS
Marketplace Product Support Connection (PSC) customer contact and subscription data. It was not a
general role-execution primitive: the role was the pre-enrolled delivery role that let an AWS-owned
Marketplace account write the resulting CSV/metadata to S3 and publish status to SNS.

The target is now dead. AWS ended Product Support Connection and customer-contact sharing on November
30, 2022; current SDK/CLI models mark the operation deprecated and say PSC is no longer supported as of
December 2022. The broader Commerce Analytics Service remains available for seller usage, subscription,
and billing reports through `GenerateDataSet`, so only this support-contact operation is retired.

This is a reasoned exclusion from the public book. It cannot currently provide customer data, is not an
IAM PassRole escalation, and the lab is not enrolled in Commerce Analytics or equipped with the
historical delivery role. The still-active `GenerateDataSet` sibling should be reviewed separately if
seller-report delivery becomes in scope; its continued existence does not revive PSC contact exports.

## Caller authorization — no PassRole dependency

The current Service Authorization Reference defines the caller permission as:

```json
{
  "Effect": "Allow",
  "Action": "marketplacecommerceanalytics:StartSupportDataExport",
  "Resource": "*"
}
```

The service supports no resource ARN and no service-specific condition keys. Critically, the
authorization table lists no `iam:PassRole` dependent action. The archived official Seller Guide gives
the same one-action policy and instructs existing CAS users to reuse their CAS onboarding role. The
`roleNameArn` model match is therefore a cont.82 scanner false positive for PassRole.

The caller does not need direct `s3:PutObject`, `sns:Publish`, or `iam:GetRolePolicy`; those are
permissions of the delivery role assumed by AWS Marketplace. Seller enrollment and the discontinued PSC
product enrollment were separate service-side eligibility gates.

## Delivery-role trust and permissions

Current AWS onboarding documentation says that enrollment creates `MarketplaceCommerceAnalyticsRole` in
the seller account and that AWS Marketplace account `452565589796` uses it. The documented role actions
required by both `GenerateDataSet` and the former support export are:

- `s3:PutObject`
- `s3:GetBucketLocation`
- `sns:GetTopicAttributes`
- `sns:Publish`
- `iam:GetRolePolicy`

A least-privilege role policy therefore restricts `GetBucketLocation` to the enrolled bucket,
`PutObject` to the intended bucket/prefix, both SNS actions to the enrolled topic, and `GetRolePolicy` to
the delivery role itself. AWS troubleshooting documentation says the onboarding-generated inline policy
is limited to the exact bucket and topic selected during enrollment; changing either destination requires
editing that role policy.

The current public documentation identifies the trusted AWS account but does not publish the exact
generated assume-role policy or say whether it contains an external ID or another condition. No such role
exists in the lab to inspect. Therefore the verified trust boundary is account `452565589796` using a
seller-account role; an exact JSON trust policy beyond that would be fabrication. A future review of an
existing seller must capture the live trust document before making a confused-deputy or cross-account
claim.

This customer delivery role is not a credential vend: the API returns only a `dataSetRequestId`, and the
caller never receives the assumed-role credentials.

## Destination control and data-access boundary

The request directly selects:

- an S3 bucket name and optional prefix for the CSV and metadata JSON;
- an SNS topic ARN for completion/error notification; and
- up to five caller-defined key/value pairs echoed unchanged in the SNS notification and metadata.

Those parameters are only effective where the specified role is authorized. The normal onboarding role
is restricted to the enrolled bucket and topic, so a caller holding only
`StartSupportDataExport` cannot redirect data to an arbitrary external sink. Cross-account delivery would
also require a pre-existing role permission and target bucket/topic resource policy that permit it. The
archived guide explicitly recommended a separate S3 bucket for PSC contact data and required all intended
buckets to be present in the role policy.

The API has no seller-account, product-owner, or arbitrary query field. It historically returned only
contact changes for PSC-enabled products belonging to the eligible seller. The official workflow required
the same CAS role used by that seller. Cross-account role acceptance or another seller's data access is
not established by the docs and was not testable after retirement.

Thus the operation could cause data to be written without granting the caller direct S3 read access, but
the caller would only obtain the output if they already controlled or could read a role-authorized sink.
That is a seller-data delivery permission, not privilege escalation through the role.

## Historical data sensitivity

The real `customer_support_contacts_data` CSV contained changes from `fromDate` through roughly 15
minutes before the request, including:

- product ID and product code;
- customer and subscription GUIDs plus subscription start date;
- customer organization and AWS account ID;
- given name, surname, telephone number, email, and title;
- country code and ZIP code; and
- create/update/delete operation type and timestamp.

This was sensitive subscriber PII and commercial relationship data. Customers voluntarily provided the
contact details for support on PSC-enabled products. The alternative
`test_customer_support_contacts_data` contained static synthetic data in the same schema.

## Region, onboarding, cost, and cleanup

Commerce Analytics has only a `us-east-1` API endpoint, although the destination SNS topic shown by AWS
could be in another Region. Historical prerequisites were:

- AWS Marketplace seller registration and products;
- acceptance/enrollment in Commerce Analytics Service;
- an S3 destination and SNS notification topic;
- the portal-created delivery role; and
- PSC enrollment of the seller's products and customer opt-in to contact sharing.

The current docs do not list a separate per-request Commerce Analytics price. Normal S3 storage/request
and SNS charges apply, while seller registration, product publication, transactions, and listing fees are
a materially larger onboarding boundary. PSC enrollment can no longer be created.

The export was asynchronous and had no cancel/delete-request API. A successful test would leave an S3
CSV, metadata object, SNS delivery, request identifier, and audit history; objects could be deleted, but a
delivered notification and audit records could not be recalled. Because the target is retired and the
account has no enrolled role/resources, even a nonexistent-destination call could enqueue an irreversible
asynchronous request before later failing. No live start call was made.

## Read-only account inventory

Authorized account `228478051196`, profile `ht-admin`, 2026-09-26:

- No IAM role name contained Marketplace, Commerce Analytics, or CAS.
- No role trust policy referenced AWS Marketplace account `452565589796`.
- No S3 bucket or `us-east-1` SNS topic name suggested a Marketplace/CAS destination.
- `marketplace-catalog:ListEntities` for `AmiProduct` succeeded but returned no AMI seller products.
- CloudTrail Event History in `us-east-1` had no `StartSupportDataExport` or `GenerateDataSet` events.

This inventory is evidence of no CAS onboarding in the lab, not proof that the account has never begun a
seller registration workflow. No seller enrollment, product, role, policy, bucket, topic, export request,
or other AWS state was created or changed. Cleanup residue is zero.

## Logging

AWS's current EventBridge reference says Commerce Analytics events arrive through CloudTrail with
`eventSource=marketplace-commerce-analytics.amazonaws.com` and EventBridge source
`aws.marketplace-commerce-analytics`. A start request would therefore be a control-plane event to alert
on, followed—if the retired workflow still ran—by the delivery role's S3 write and SNS publish.

No current official example exposes the exact `StartSupportDataExport` CloudTrail request fields, and the
lab has no historical or live event. Do not claim that role ARN, bucket, prefix, topic, `fromDate`, or
customer-defined values are present or redacted without a real event. CloudTrail lookup found no recent
activity.

## Completed checks

- [x] Inspect AWS CLI 2.34.45 operation/input/output models and deprecation metadata.
- [x] Confirm lifecycle from the current document history and distinguish active CAS from retired PSC.
- [x] Confirm wildcard-only caller authorization, no condition keys, and no PassRole dependency.
- [x] Recover the historical official one-action caller policy and data/destination semantics.
- [x] Determine the AWS-owned role-using account and exact required role actions.
- [x] Separate caller-selected destination parameters from role-policy-effective destinations.
- [x] Inventory seller products, matching IAM roles/trust, candidate buckets/topics, and CloudTrail.
- [x] Decline an asynchronous validation call that could create a non-cancellable request.

## Revisit only if historical evidence is supplied

- [ ] Inspect an actual onboarding-generated role trust policy, including any external ID/conditions.
- [ ] Inspect the exact inline S3/SNS/IAM role policy and bucket/topic resource policies.
- [ ] Capture a sanitized pre-retirement CloudTrail event to establish request-parameter visibility.
- [ ] Do not attempt to reactivate PSC; it is no longer supported.

## Official sources

- <https://docs.aws.amazon.com/cli/latest/reference/marketplacecommerceanalytics/start-support-data-export.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_marketplacecommerceanalytics.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/document-history.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/on-boarding-guide.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/cas-troubleshooting.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/commerce-analytics-service.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/technical-documentation.html>
- <https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-marketplace-commerce-analytics.html>
- <https://pages.awscloud.com/rs/112-TZM-766/images/aws-marketplace-ug.pdf>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/user-guide-for-sellers.html>
- <https://docs.aws.amazon.com/marketplace/latest/userguide/listing-fees.html>
