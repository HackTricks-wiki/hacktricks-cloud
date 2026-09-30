# AWS Marketplace Discovery API audit — 2026-09-30

## Outcome

The new buyer-facing Discovery API is a distinct Marketplace post-exploitation surface. It exposes
public catalog metadata and every private purchase option visible to the calling account, including
pricing and legal terms before agreement acceptance. The expected technique was published in the
existing Marketplace enum and post-exploitation pages. No AWS defect was confirmed and nothing was
written to the private vulnerability-report directory.

Authorized account: `228478051196`. Region: `us-east-1`. Bootstrap profile:
`hacktricks-training`; role: `ChackBotAdministratorRole`. No subscription, purchase, agreement,
offer, product, deployment, bucket, or other billable resource was created.

## Live results

| Probe | Result | Conclusion |
|---|---|---|
| `SearchListings --max-results 2` | Returned two of 43,761 public listings | API is live and provides broad catalog recon. |
| Unsigned `SearchListings` | `AccessDeniedException: Missing Authentication Token` | Not an unauthenticated catalog endpoint. |
| `ListPurchaseOptions` with `VISIBILITY_SCOPE=PRIVATE` | Success, zero results | Private inventory is buyer/account contextual; this account has no fixture. |
| Product-scoped `ListPurchaseOptions` | Returned a public Fortinet offer | Product-to-offer discovery works without purchase. |
| `GetOffer` | Returned pricing type, agreement proposal ID and product relationship | Offer metadata is a separate exact-resource read. |
| `GetOfferTerms` | Returned five term types, prices and a presigned custom-EULA URL | Legal-document access is vended directly; no customer S3 permission is involved. URL was not redeemed. |
| `ListFulfillmentOptions` | Returned AMI versions, OS, recommended instance type, release notes and usage instructions | Deployment metadata can include operational defaults and endpoints. |
| Least-privilege role | `ListPurchaseOptions` and exact-offer `GetOfferTerms` succeeded; `SearchListings` was denied | Documented resource scoping is enforced. |

The temporary role `ht-marketplace-discovery-probe-260930-a` and its inline policy were deleted.
`GetRole` independently confirmed absence after the test.

## Authorization model

- Service/CLI: `marketplace-discovery`; IAM prefix: `aws-marketplace`.
- `ListPurchaseOptions` requires
  `arn:aws:aws-marketplace:::catalog/AWSMarketplace/purchaseOption/*`.
- `SearchListings` and `SearchFacets` use the catalog listing wildcard.
- `GetOffer` and `GetOfferTerms` support exact offer ARNs; `GetOfferSet` supports exact offer-set
  ARNs; product/fulfillment reads support exact product ARNs.
- The service defines no service-specific condition keys.
- Current public Regions: `us-east-1`, `us-west-2`, and `eu-west-1`.

## Telemetry

Six successful calls were observed in CloudTrail Event History. They were read-only management
events from `discovery-marketplace.amazonaws.com`:

- `SearchListings` recorded `maxResults`.
- `ListPurchaseOptions` recorded the full product or `VISIBILITY_SCOPE=PRIVATE` filter.
- `GetOffer` and `GetOfferTerms` recorded the exact offer ID and an
  `AWS::MarketplaceDiscovery::Offer` resource.
- `ListFulfillmentOptions` recorded the product ID and an
  `AWS::MarketplaceDiscovery::Product` resource.
- Successful `responseElements` were `null`; returned pricing, instructions, legal terms and the
  presigned URL were not copied into the CloudTrail event.

## Publication decision

Published one post-exploitation technique because it clears the usefulness threshold: a compact
permission set can reveal negotiated, unaccepted or future-dated private offers, prices, payment and
renewal structure, custom legal documents, buyer notes and replacement-agreement plans. This is
sensitive procurement intelligence, not IAM privilege escalation or persistence.

Public catalog browsing by itself is not a separate attack technique. It remains enumeration context.

## Candidate backlog

1. With an explicitly authorized buyer fixture, verify a synthetic private offer and offer set,
   including buyer notes, custom EULA, future date and replacement agreement.
2. With two authorized buyer accounts, verify wrong-buyer known-offer and offer-set IDs fail before
   returning any metadata or document URL. Keep this as a private IDOR hypothesis until proven.
3. Measure presigned legal-document expiration, single/multi-use behavior, revocation after offer
   expiry, and whether document access produces any seller-visible audit signal.
4. Test global SigV4a endpoint routing and whether CloudTrail Region/source attribution remains
   deterministic.
5. Confirm exact-resource authorization for `GetOffer`, `GetOfferSet`, `GetProduct` and
   `ListFulfillmentOptions` with synthetic private content.

## Cleanup proof

- Private/public offers, agreements, subscriptions and purchases created: none.
- Legal-document URLs redeemed or downloaded: none.
- Marketplace resources changed: none.
- Temporary IAM roles/policies remaining: zero.
- Cost-bearing infrastructure created: none.

## Primary sources

- https://docs.aws.amazon.com/marketplace/latest/developerguide/discovery-apis.html
- https://docs.aws.amazon.com/marketplace/latest/developerguide/discovery-api-access-control.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_marketplace-discovery.html
- https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-discovery_ListPurchaseOptions.html
- https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-discovery_GetOfferTerms.html
- https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-discovery-marketplace.html
