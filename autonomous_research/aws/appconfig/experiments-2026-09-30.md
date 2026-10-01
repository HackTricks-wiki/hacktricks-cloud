# AWS AppConfig Experiments audit — 2026-09-30

## Result

Verified a new expected configuration-poisoning path through the September 2026 AppConfig experiment APIs. Experiment definitions store audience rules and control/treatment feature-flag values. A run overlays those values on an already deployed feature flag without creating a new hosted configuration version. The official AppConfig Agent applies the overlay for exposed or explicitly overridden entity IDs.

This is useful because `CreateExperimentDefinition` can introduce an alternate flag value without `CreateHostedConfigurationVersion`, while a later authorized start can activate it. It is not a deployment-authority bypass: `StartExperimentRun` and each state-changing `UpdateExperimentRun` perform a dependent `StartDeployment` authorization check.

## Live fixture and consumer proof

The test created one disposable AppConfig application, environment, hosted `AWS.AppConfig.FeatureFlags` profile, version `1`, and zero-duration deployment strategy. Version `1` defined one flag, `security_mode`, with `enabled: false` and was deployed successfully.

A restricted STS session with only `appconfig:CreateExperimentDefinition` on the exact application and configuration-profile ARNs created a definition whose treatment enabled the flag and whose control kept it disabled. It had no `CreateHostedConfigurationVersion`, environment, deployment, data-plane, or `iam:PassRole` permission.

The run started at 0% exposure. A second restricted session scoped `UpdateExperimentRun` to the exact application, definition and run plus the dependent deployment resources. Run `999` was denied. Two separate valid calls then:

1. mapped synthetic entity `victim-123` to treatment `t1`; and
2. increased exposure from 0% to 100%.

Supplying both fields in one call returned the secure validation error `Only one deployment attribute can be updated per request` and changed nothing.

After start plus the two updates, the environment contained four completed deployments: baseline plus one for each experiment mutation. Every deployment still named configuration version `1`, and `ListHostedConfigurationVersions` continued to return only version `1`.

The current official AppConfig Agent `2.x` container was started locally with temporary administrative retrieval credentials. Its entity-aware request returned:

```json
{"_variant":"__t1_override__","enabled":true}
```

for `Entity-Id: victim-123`, even though the only hosted version remained disabled. This confirms actual consumer-side treatment delivery, not merely control-plane acceptance.

## Authorization findings

### Create definition

An application-only session failed on the exact configuration-profile ARN. Application + configuration profile succeeded; no environment resource was required. The current Service Authorization Reference lists only `application` for `CreateExperimentDefinition`, so it understates the live resource checks. This drift is restrictive/beneficial, not a security vulnerability.

### Start run

`StartExperimentRun` on only the application and definition failed with an error naming missing `appconfig:StartDeployment` on the application. A successful start required:

- `appconfig:StartExperimentRun` on the exact application and definition; and
- `appconfig:StartDeployment` on the application, selected configuration profile, environment and `arn:aws:appconfig:<region>:<account>:deploymentstrategy/AppConfig.ServiceManaged`.

The simplified authorization metadata does not currently list `StartDeployment` as a dependent action. The live dependency prevents experiment start from bypassing ordinary deployment authority. `AppConfig.ServiceManaged` appeared in every experiment-generated `StartDeployment` event even though `ListDeploymentStrategies` did not return it.

### Update run

`UpdateExperimentRun` required application + definition + exact run, and each successful exposure/override update also required the same dependent `StartDeployment` resources. An exact run-1 policy denied run 999.

No `CreateHostedConfigurationVersion`, `UpdateConfigurationProfile`, `iam:PassRole`, or caller-side AppConfig Data permission was needed.

## Impact boundaries

- The feature flag must already be deployed to the selected environment.
- The workload must use an AppConfig Agent version that supports experiments and request the flag with entity/context information.
- Treatment attributes remain constrained by the selected flag's declared schema.
- The overlay affects only the chosen application/profile/environment/flag and ends when the run stops.
- Application consequences are consumer-defined. Enabling a flag can be critical, but the AWS APIs do not inherently produce code execution, IAM credentials, or access to unrelated configuration.
- Starting the run starts hourly billing until it is stopped.

## Telemetry

All experiment control-plane operations and their dependent deployments are management events logged by default. AppConfig Data retrieval remains opt-in data-event telemetry. Agent treatment-assignment logs are emitted only when `EXPERIMENT_ASSIGNMENT_LOG_DESTINATION` is configured and contain the entity ID and treatment key.

Event History initially waited for ingestion, then indexed the full chain as default management events under `appconfig.amazonaws.com`:

- `CreateExperimentDefinition` retained the application/profile/environment, flag key, audience rule, and complete enabled/disabled treatment/control values; its response was null.
- `StartExperimentRun` retained 0% exposure and returned the full definition snapshot, including assigned `t1`/`c` keys and values.
- The override `UpdateExperimentRun` masked `requestParameters.treatmentOverrides` as `HIDDEN_DUE_TO_SECURITY_REASONS`, but its response returned `treatmentOverrides.inline.victim-123 = t1` in clear. The later exposure update also echoed the override map and full definition snapshot.
- Each mutation's `StartDeployment` used `deploymentStrategyId: AppConfig.ServiceManaged`, configuration version `1`, and a description containing the exact experiment-run ARN. Stop generated another service-managed restoration deployment.
- `StopExperimentRun` returned the final 100% exposure, override and snapshot; `DeleteExperimentDefinition` recorded `deleteType: DESTROY`.

Run events independently recorded `RUN_STARTED`, `OVERRIDES_UPDATED`, and `EXPOSURE_UPDATED`, including the synthetic entity override and 100% exposure. AppConfig Data calls remain opt-in data events.

Overall stealth: **Low**. No hosted version is added, but definition/run writes plus one deployment per state change are conspicuous.

## Failed branches and cleanup

Four guarded fixtures were used:

1. Application-only definition creation failed on the missing profile resource. The first cleanup removed environment/strategy but initially left a hosted version/profile/application; independent inventory caught it, and the exact version, profile and parent were then deleted.
2. Definition creation succeeded with application + profile, but start without the dependent `StartDeployment` action was denied. Cleanup completed.
3. Start succeeded with the full dependency set; the combined exposure+override update failed validation. Cleanup completed.
4. Separate override and exposure updates succeeded, and the official Agent confirmed the delivered treatment. Cleanup completed.

Final AppConfig application and experiment-definition inventories are empty in `us-east-1` and application inventory is empty in `eu-west-1`. No custom deployment strategies remain. The exact local Agent container is absent, and its newly pulled image was removed. No IAM role/policy, Lambda, EC2, ECS/EKS, CloudWatch alarm, KMS key, extension, external source, secret, bucket, parameter, domain or network resource was created.

## Classification

Expected functionality plus restrictive authorization-reference drift. No AWS vulnerability report was created.

## Sources

- https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-experimentation-about.html
- https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-experimentation-about-controls-and-treatments.html
- https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-retrieving-experiment-treatments.html
- https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-experimentation-creating-prerequisites.html
- https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/API_CreateExperimentDefinition.html
- https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/API_StartExperimentRun.html
- https://docs.aws.amazon.com/appconfig/2019-10-09/APIReference/API_UpdateExperimentRun.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appconfig.html
