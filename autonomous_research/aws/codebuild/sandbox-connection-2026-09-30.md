# CodeBuild `StartSandboxConnection` interactive access — 2026-09-30

## Outcome

Added a distinct privilege-escalation path for `codebuild:StartSandboxConnection`. The API returns a
Session Manager session ID, encrypted token, and stream URL that an authorized client uses to open an
interactive SSH/Session Manager shell in a running CodeBuild sandbox.

This complements `StartCommandExecution`: the latter submits one command through CodeBuild, while
`StartSandboxConnection` vends an interactive connection into the live container. Both can reach the
project role and in-container source/secrets without project mutation or caller-side PassRole.

Expected functionality only; no AWS defect or private report.

## Minimum authorization

The AWS Service Authorization Reference maps the API to
`codebuild:StartSandboxConnection` on the required sandbox resource type:

```text
arn:aws:codebuild:<region>:<account>:sandbox/<sandbox-id>
```

No dependent action is listed. The caller needs a known running sandbox ID/ARN. For a successful
connection, the image needs a functional SSM Agent and the project's CodeBuild service role/config
must allow the documented SSM session establishment. The caller does not need sandbox list/get/start,
command execution, SSM, or PassRole permissions.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`:

- Admin `ListSandboxes` projected to a count and returned **0**.
- Assumed `ChackBotAdministratorRole` with an inline STS session policy allowing only
  `codebuild:StartSandboxConnection` on one synthetic exact sandbox ARN.
- The allowed ARN returned `InvalidInputException: No sandbox found with specified ID`, proving that
  the action passed its IAM gate.
- A second sandbox ARN returned `AccessDeniedException` because no session policy allowed it.
- `ListSandboxes` under the same constrained session returned `AccessDeniedException`.

No CodeBuild project, sandbox, IAM role/policy, or SSM resource was created. The STS session policy is
ephemeral, so cleanup was vacuous.

## Impact and telemetry

A successful connection can expose checked-out source, environment variables, credentials, mounted
filesystems, caches, artifacts, and an interactive execution context carrying the project role's
effective permissions.

The Service Authorization Reference classifies `StartSandboxConnection` as Write, but CloudTrail
recorded both failed probes as `eventCategory: Management` with `readOnly: true`. The allowed exact-ARN
probe retained `sandboxId` and `jupyterNotebookServer:false`; the IAM-denied alternate used
`requestParameters:null`. Both had `responseElements:null`.

Commands typed in the shell are not each CloudTrail API calls, but downstream AWS calls use the
project-role session. The service may also produce SSM/session-channel telemetry during connection
establishment. Successful response logging was not tested, so the token and stream URL must be
treated as sensitive without asserting a specific CloudTrail redaction behavior.

## Primary sources

- https://docs.aws.amazon.com/codebuild/latest/APIReference/API_StartSandboxConnection.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_codebuild.html
- https://docs.aws.amazon.com/codebuild/latest/userguide/debug-builds.html
- https://docs.aws.amazon.com/codebuild/latest/userguide/sandbox-troubleshooting.html
