# Aurora DSQL authentication-token binding — 2026-09-26

## Outcome

Negative / secure boundary result. Aurora DSQL rejected every cluster, action, Region, IAM-scope,
database-role-mapping, mutation, expiry, and revocation bypass. Unchanged replay before expiration is
documented behavior and worked. No AWS vulnerability report was created.

The public DSQL page already contained the useful expected techniques (`DbConnectAdmin`, `DbConnect`,
and `PutClusterPolicy`). This audit filled their missing impact, explicit stealth, and expandable logs
tables, and added verified token/revocation semantics.

## Fixture and minimum principals

- Two empty single-Region Aurora DSQL clusters in `us-east-1`; public managed endpoints; no customer
  KMS key, VPC endpoint, or multi-Region peer/witness.
- `admin-both`: `dsql:DbConnectAdmin` and `dsql:DbConnect` on exact cluster ARNs A and B.
- `user-a`: `dsql:DbConnect` on exact cluster ARN A only; mapped to database role `ht_reader` on A
  and B so the B denial isolated IAM cluster scope rather than mapping absence.
- `unmapped`: `dsql:DbConnect` on exact cluster ARN A with no database-role mapping.
- `ht_reader WITH LOGIN` existed on both clusters. `admin-both` was additionally mapped to it on A
  for action/parser cases.
- PostgreSQL 16 client over TLS `verify-full` using Amazon Root CA 1.

## Live matrix

| Case | Observed result |
| --- | --- |
| Admin token A -> A as `admin` | Success; `current_user=admin` |
| Same admin token -> A as `ht_reader` | Rejected: wrong user/action (`DbConnectAdmin`) |
| User token A -> A as mapped `ht_reader` | Success |
| Same user token -> A as `admin` | Rejected: wrong user/action (`DbConnect`) |
| Exact-A IAM role without mapping -> A as `ht_reader` | Rejected |
| Admin token signed for A -> B as `admin` | Rejected despite IAM admin permission on both clusters |
| `user-a` token signed for B -> B mapped `ht_reader` | Rejected by exact-A IAM scope |
| Token for A signed with `us-west-2` scope | Rejected: credential scoped to invalid Region |
| Same untouched user token, multiple new A connections | Each succeeded before expiry; expected replay |
| `DbConnect` token action changed to `DbConnectAdmin` | Signature mismatch; rejected |
| Duplicate trailing `Action=DbConnectAdmin` | Original `DbConnect` remained effective; admin login rejected |
| One-character signature mutation | Signature mismatch; rejected |
| `X-Amz-Security-Token` removed | Invalid security token; rejected |
| Token hostname A changed to B | Signature mismatch; rejected |
| 60-second token before expiry | Success |
| Same token after 75 seconds | Rejected as expired |
| Mapping revoked while token still valid | Next connection rejected immediately |
| Same mapping restored | Same still-valid token connected again |
| IAM `DbConnect` policy deleted while token still valid | Next connection rejected immediately |

The decisive results are that token generation is only local signing—not authorization—and that each
new connection re-evaluates the signed request, current IAM authorization, and current database-role
mapping. Token possession alone did not preserve revoked access.

## Telemetry

- Token generation performed no AWS API call and produced no CloudTrail event.
- `DbConnect` and `DbConnectAdmin` are optional data events on `AWS::DSQL::Cluster`; default Event
  History did not contain the connection matrix.
- SQL statements are not CloudTrail API events.
- `CreateCluster`, `GetCluster`, and `DeleteCluster` were default management events. Event History
  contained both fixture `CreateCluster` and both `DeleteCluster` events after propagation.
- A paid data-event selector/trail was not created solely for this negative test.

## Cleanup

Mappings and the disposable database role were removed best-effort before cluster deletion. Both
clusters reached not-found after asynchronous deletion, all three IAM roles and their inline policies
were deleted, and the service-linked role did not exist afterward (it also did not pre-exist). Final
independent inventory returned no matching DSQL cluster, IAM role, or Aurora DSQL service-linked role.
