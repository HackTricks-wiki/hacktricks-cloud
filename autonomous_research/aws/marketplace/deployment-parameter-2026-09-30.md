# Marketplace Deployment parameter poisoning — 2026-09-30

## Outcome

Documented `aws-marketplace:PutDeploymentParameter` as a conditional seller-to-buyer supply-chain
primitive. A seller can create or update a named AWS Marketplace-managed secret in the agreement
acceptor's Secrets Manager account. Supported real-world values include API keys, OAuth credentials
and discovery URLs, external IDs, license keys, and dynamic endpoint parameters.

Expected functionality only. No AWS defect or private report.

## Security model

The request is keyed by catalog, seller product ID, buyer agreement ID, and parameter name. Reusing a
name for the same buyer/product updates the deployment parameter. The buyer must already have created
`AWSServiceRoleForMarketplaceDeployment`; AWS Marketplace uses it to manage the buyer-side secret.
The managed secret must be updated through Marketplace rather than directly through Secrets Manager.

This prevents arbitrary targeting: the caller needs a seller-owned product and a valid agreement.
The write does not itself execute or update CloudFormation. Security impact depends on the approved
Quick Launch template or product integration later consuming the replaced value.

The minimum IAM action is `aws-marketplace:PutDeploymentParameter` on:

```text
arn:aws:aws-marketplace:<region>:<seller-account>:DeploymentParameter:catalogs/AWSMarketplace/products/<product-id>/*
```

`aws-marketplace:TagResource` is required only if optional tags are supplied. Buyer credentials,
Secrets Manager/KMS access, CloudFormation permissions and PassRole are not caller prerequisites.

## Safe live authorization proof

Authorized seller-side test account: `228478051196`; Region: `us-east-1`.

Used an inline STS session policy allowing only `PutDeploymentParameter` on one impossible synthetic
product wildcard. The request used a synthetic product, agreement, name, and non-secret string:

- allowed product: `ResourceNotFoundException` naming the nonexistent product, proving IAM passed;
- alternate product: `AccessDeniedException` because the STS policy did not cover its ARN;
- `TagResource` on the allowed product wildcard: `AccessDeniedException`, proving it is not inherited.

No real product/agreement was referenced and no deployment parameter or secret was created. The API
has no delete operation, so an end-to-end fixture was deliberately not created. The STS policy was
ephemeral and cleanup was vacuous.

## Impact boundaries

Potential outcomes include authentication/endpoint redirection, attacker-selected OAuth or API
credentials, external-ID replacement, poisoned CloudFormation configuration, durable vendor-side
access, or denial of service. None is automatic: the affected buyer must consume the parameter and
the result is bounded by its template/integration semantics.

## Telemetry

Official EventBridge metadata assigns Marketplace Deployment:

- `source: aws.deployment-marketplace`
- `eventSource: deployment-marketplace.amazonaws.com`

After propagation, Event History contained both failed `PutDeploymentParameter` calls as management
writes with `readOnly:false`. CloudTrail retained product ID, `AWSMarketplace` catalog, client token,
agreement ID, and deployment-parameter name, but replaced `secretString` with `***`. It stored the
service/IAM failure message under `responseElements.message`.

Correlate seller `PutDeploymentParameter` with buyer service-linked-role Secrets Manager changes,
replication/read, Quick Launch/CloudFormation activity, and product authentication/endpoint traffic.
Successful buyer-side secret activity was not tested and remains deliberately unclaimed.

## Primary sources

- https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-deployment_PutDeploymentParameter.html
- https://docs.aws.amazon.com/marketplace/latest/APIReference/deployment-api-access-control.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_marketplace-deployment.html
- https://docs.aws.amazon.com/marketplace/latest/userguide/saas-product-settings.html
- https://docs.aws.amazon.com/marketplace/latest/userguide/integrating-api-ai-agents-tools.html
- https://docs.aws.amazon.com/marketplace/latest/buyerguide/quick-launch.html
- https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_how-services-use-secrets_marketplace-deployment.html
- https://docs.aws.amazon.com/eventbridge/latest/ref/events.html
