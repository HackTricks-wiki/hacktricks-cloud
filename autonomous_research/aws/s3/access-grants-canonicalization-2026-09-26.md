# S3 Access Grants target canonicalization, 2026-09-26

## Hypothesis

`s3:GetDataAccess` might parse its requested `Target` differently from the S3 session policy it
generates. A dot-segment, repeated separator, encoded separator, backslash, or Unicode separator
could then match an `allowed/*` grant while producing credentials usable against a sibling
`denied/*` key. If that occurred, it would be a private AWS security issue rather than a public-book
technique.

## Result — secure behavior (not a vulnerability)

A disposable Access Grants instance registered one bucket containing only
`allowed/sentinel.txt` and `denied/sentinel.txt`. An IAM user whose only identity permission was
`s3:GetDataAccess` received a `READ` grant for `allowed/*`. The location role itself could read both
objects, ensuring that any isolation came from the Access Grants session policy rather than its base
role policy.

The matrix tested both `Minimal` and `Default` privilege with:

- an exact allowed object and an exact denied object;
- `allowed/../denied/...`, `allowed/./../denied/...`, and `allowed//../denied/...`;
- `%2e%2e`, encoded slash, and double-encoded dot/slash variants;
- backslash and Unicode full-width slash variants; and
- a traversal-shaped wildcard target.

The exact allowed target vended credentials and could read only the allowed sentinel. The exact
denied target, encoded-slash-before-prefix variants, backslash, and Unicode separator variants were
denied. Several strings that lexically began with `allowed/` vended credentials, but they remained
safe:

- `Minimal` returned the traversal-shaped string verbatim as `MatchedGrantTarget`; those credentials
  could read neither the normal allowed sentinel nor the denied sibling.
- `Default` returned `allowed/*`; those credentials read the allowed sentinel and were denied on the
  denied sibling.
- A traversal-shaped wildcard target was rejected as `InvalidRequest`.

There was no target that produced credentials able to read `denied/sentinel.txt`. Do not publish this
matrix as an attack technique; retain it to avoid repeating the same parser probe.

## Setup notes and cleanup

The first setup attempt reached `CreateAccessGrantsLocation` before the new role had propagated and
returned `InvalidIamRole`. The retry run treated that response as eventual consistency and completed
the matrix. Both attempts used `finally` teardown. The access grant, location, Access Grants instance,
access key, IAM user/policy, location role/policy, both objects, and bucket were deleted. Final probes
returned `AccessGrantsInstanceNotExistsError`, S3 `404`, and IAM `NoSuchEntity` for the user and role.

