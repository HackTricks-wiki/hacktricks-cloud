# Secrets Manager documentation audit — 2026-09-26

Scope: existing post-exploitation page. This pass checked AWS documentation only; it did not create resources or make test API calls.

| Claim checked | Result | Source |
| --- | --- | --- |
| `BatchGetSecretValue` hides per-secret reads from CloudTrail | Rejected. AWS documents a `GetSecretValue` event for each requested secret in addition to the batch event. Corrected the book's detection guidance. | [BatchGetSecretValue API](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_BatchGetSecretValue.html), [CloudTrail entries](https://docs.aws.amazon.com/secretsmanager/latest/userguide/cloudtrail_log_entries.html) |
| Changing a secret's KMS key makes every existing version permanently unreadable | Rejected. When permissions allow re-encryption, labeled versions retain copies under the previous key; other versions can still depend on that key. Corrected impact and recovery guidance. | [Change the encryption key](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_update-encryption-key.html) |
| Force deletion is synchronous | Rejected. It skips the recovery window, but permanent deletion runs asynchronously. Corrected timing language. | [DeleteSecret API](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_DeleteSecret.html) |
| Restore, resource-policy deletion, and version-stage changes have CloudTrail entries | Confirmed from AWS's event catalog. Added per-technique impact, logging tables, and detectability labels. | [CloudTrail entries](https://docs.aws.amazon.com/secretsmanager/latest/userguide/cloudtrail_log_entries.html) |

No new attack technique or AWS service defect was established in this pass. No infrastructure was launched; cleanup is not applicable.
