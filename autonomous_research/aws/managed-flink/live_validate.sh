#!/usr/bin/env bash
set -euo pipefail

export AWS_DEFAULT_OUTPUT=json
export AWS_DEFAULT_REGION=us-east-1
export AWS_REGION=us-east-1
export AWS_PAGER=''

account_id=228478051196
region=us-east-1
suffix="$(date +%s)"
app_name="ht-mf-audit-${suffix}"
bucket="ht-mf-audit-${account_id}-${suffix}"
role_name="ht-mf-audit-${suffix}"
role_arn="arn:aws:iam::${account_id}:role/${role_name}"
app_arn="arn:aws:kinesisanalytics:${region}:${account_id}:application/${app_name}"
log_group="/aws/kinesis-analytics/${app_name}"
log_stream="audit-stream"
log_stream_arn="arn:aws:logs:${region}:${account_id}:log-group:${log_group}:log-stream:${log_stream}"

read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN < <(
  aws sts assume-role \
    --profile hacktricks-training \
    --role-arn arn:aws:iam::228478051196:role/ChackBotAdministratorRole \
    --role-session-name ht-managed-flink-setup \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
)
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

cleanup() {
  set +e
  printf 'CLEANUP app=%s bucket=%s role=%s\n' "$app_name" "$bucket" "$role_name"
  app_status="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationStatus' --output text 2>/dev/null)"
  if [[ "$app_status" == "RUNNING" || "$app_status" == "STARTING" || "$app_status" == "UPDATING" ]]; then
    aws kinesisanalyticsv2 stop-application --application-name "$app_name" --force >/dev/null 2>&1
    aws kinesisanalyticsv2 wait application-stopped --application-name "$app_name" >/dev/null 2>&1
  fi
  create_ts="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.CreateTimestamp' --output text 2>/dev/null)"
  if [[ -n "$create_ts" && "$create_ts" != "None" ]]; then
    aws kinesisanalyticsv2 delete-application --application-name "$app_name" --create-timestamp "$create_ts" >/dev/null 2>&1
  fi
  aws s3api delete-object --bucket "$bucket" --key original.jar >/dev/null 2>&1
  aws s3api delete-object --bucket "$bucket" --key replacement.jar >/dev/null 2>&1
  aws s3api delete-bucket --bucket "$bucket" >/dev/null 2>&1
  aws iam delete-role-policy --role-name "$role_name" --policy-name exact-code-read >/dev/null 2>&1
  aws iam delete-role --role-name "$role_name" >/dev/null 2>&1
  aws logs delete-log-group --log-group-name "$log_group" >/dev/null 2>&1
}
trap cleanup EXIT INT TERM

aws s3api create-bucket --bucket "$bucket" >/dev/null
aws s3api put-object --bucket "$bucket" --key original.jar --body /usr/lib/jvm/java-21-openjdk-amd64/lib/jrt-fs.jar >/dev/null
aws s3api put-object --bucket "$bucket" --key replacement.jar --body /usr/share/java/libintl-0.21.jar >/dev/null
aws logs create-log-group --log-group-name "$log_group"
aws logs create-log-stream --log-group-name "$log_group" --log-stream-name "$log_stream"

vpc_id="$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)"
subnet_id="$(aws ec2 describe-subnets --filters Name=vpc-id,Values="$vpc_id" --query 'Subnets[0].SubnetId' --output text)"
security_group_id="$(aws ec2 describe-security-groups --filters Name=vpc-id,Values="$vpc_id" Name=group-name,Values=default --query 'SecurityGroups[0].GroupId' --output text)"

aws iam create-role \
  --role-name "$role_name" \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"kinesisanalytics.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
aws iam put-role-policy \
  --role-name "$role_name" \
  --policy-name exact-code-read \
  --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::${bucket}/*\"},{\"Effect\":\"Allow\",\"Action\":[\"logs:DescribeLogStreams\",\"logs:PutLogEvents\"],\"Resource\":\"${log_stream_arn}\"},{\"Effect\":\"Allow\",\"Action\":[\"ec2:CreateNetworkInterface\",\"ec2:DescribeNetworkInterfaces\",\"ec2:CreateNetworkInterfacePermission\",\"ec2:DeleteNetworkInterface\",\"ec2:DescribeVpcs\",\"ec2:DescribeSubnets\",\"ec2:DescribeSecurityGroups\",\"ec2:DescribeDhcpOptions\"],\"Resource\":\"*\"}]}"
sleep 10

create_out="$(aws kinesisanalyticsv2 create-application \
  --application-name "$app_name" \
  --application-description 'disposable stopped security audit' \
  --runtime-environment FLINK-1_20 \
  --service-execution-role "$role_arn" \
  --application-mode STREAMING \
  --application-configuration "{\"ApplicationCodeConfiguration\":{\"CodeContent\":{\"S3ContentLocation\":{\"BucketARN\":\"arn:aws:s3:::${bucket}\",\"FileKey\":\"original.jar\"}},\"CodeContentType\":\"ZIPFILE\"},\"EnvironmentProperties\":{\"PropertyGroups\":[{\"PropertyGroupId\":\"secrets\",\"PropertyMap\":{\"api.password\":\"HT-MF-SENSITIVE-MARKER\",\"endpoint\":\"db.internal.example:5432\"}}]},\"ApplicationSnapshotConfiguration\":{\"SnapshotsEnabled\":false}}" \
  --tags Key=purpose,Value=ht-managed-flink-audit)"
printf 'CREATE_STATUS=%s\n' "$(jq -r '.ApplicationDetail.ApplicationStatus' <<<"$create_out")"

printf 'DESCRIBE_ADMIN_SELECTED_FIELDS\n'
aws kinesisanalyticsv2 describe-application --application-name "$app_name" \
  --query 'ApplicationDetail.{Status:ApplicationStatus,Role:ServiceExecutionRole,Code:ApplicationConfigurationDescription.ApplicationCodeConfigurationDescription.CodeContentDescription.S3ApplicationCodeLocationDescription,Properties:ApplicationConfigurationDescription.EnvironmentPropertyDescriptions.PropertyGroupDescriptions,Vpcs:ApplicationConfigurationDescription.VpcConfigurationDescriptions,Logs:CloudWatchLoggingOptionDescriptions}'

read_policy="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"kinesisanalytics:DescribeApplication\",\"kinesisanalytics:ListApplicationVersions\",\"kinesisanalytics:DescribeApplicationVersion\",\"kinesisanalytics:ListApplicationOperations\"],\"Resource\":\"${app_arn}\"},{\"Effect\":\"Deny\",\"Action\":[\"s3:GetObject\",\"iam:PassRole\"],\"Resource\":\"*\"}]}"
read -r READ_ACCESS READ_SECRET READ_TOKEN < <(
  aws sts assume-role \
    --profile hacktricks-training \
    --role-arn arn:aws:iam::228478051196:role/ChackBotAdministratorRole \
    --role-session-name ht-managed-flink-read-only \
    --policy "$read_policy" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
)

printf 'DESCRIBE_MINIMUM_PERMISSION_PROPERTIES\n'
AWS_ACCESS_KEY_ID="$READ_ACCESS" AWS_SECRET_ACCESS_KEY="$READ_SECRET" AWS_SESSION_TOKEN="$READ_TOKEN" \
  aws kinesisanalyticsv2 describe-application --application-name "$app_name" \
  --query 'ApplicationDetail.ApplicationConfigurationDescription.EnvironmentPropertyDescriptions.PropertyGroupDescriptions'

printf 'LIST_VERSIONS_MINIMUM_PERMISSION\n'
AWS_ACCESS_KEY_ID="$READ_ACCESS" AWS_SECRET_ACCESS_KEY="$READ_SECRET" AWS_SESSION_TOKEN="$READ_TOKEN" \
  aws kinesisanalyticsv2 list-application-versions --application-name "$app_name"

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
update_policy="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"kinesisanalytics:UpdateApplication\",\"kinesisanalytics:DescribeApplication\"],\"Resource\":\"${app_arn}\"},{\"Effect\":\"Deny\",\"Action\":[\"s3:GetObject\",\"iam:PassRole\"],\"Resource\":\"*\"}]}"
read -r UPDATE_ACCESS UPDATE_SECRET UPDATE_TOKEN < <(
  aws sts assume-role \
    --profile hacktricks-training \
    --role-arn arn:aws:iam::228478051196:role/ChackBotAdministratorRole \
    --role-session-name ht-managed-flink-update-only \
    --policy "$update_policy" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
)

printf 'UPDATE_CODE_WITHOUT_PASSROLE_OR_S3_READ\n'
AWS_ACCESS_KEY_ID="$UPDATE_ACCESS" AWS_SECRET_ACCESS_KEY="$UPDATE_SECRET" AWS_SESSION_TOKEN="$UPDATE_TOKEN" \
  aws kinesisanalyticsv2 update-application \
  --application-name "$app_name" \
  --current-application-version-id "$version" \
  --application-configuration-update "{\"ApplicationCodeConfigurationUpdate\":{\"CodeContentUpdate\":{\"S3ContentLocationUpdate\":{\"BucketARNUpdate\":\"arn:aws:s3:::${bucket}\",\"FileKeyUpdate\":\"replacement.jar\"}}}}" \
  --query 'ApplicationDetail.{Version:ApplicationVersionId,Status:ApplicationStatus,Code:ApplicationConfigurationDescription.ApplicationCodeConfigurationDescription.CodeContentDescription.S3ApplicationCodeLocationDescription}'

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
printf 'UPDATE_PROPERTIES_WITHOUT_PASSROLE\n'
AWS_ACCESS_KEY_ID="$UPDATE_ACCESS" AWS_SECRET_ACCESS_KEY="$UPDATE_SECRET" AWS_SESSION_TOKEN="$UPDATE_TOKEN" \
  aws kinesisanalyticsv2 update-application \
  --application-name "$app_name" \
  --current-application-version-id "$version" \
  --application-configuration-update '{"EnvironmentPropertyUpdates":{"PropertyGroups":[{"PropertyGroupId":"secrets","PropertyMap":{"api.password":"HT-MF-REPLACED-MARKER","endpoint":"attacker.internal.example:443"}}]}}' \
  --query 'ApplicationDetail.{Version:ApplicationVersionId,Status:ApplicationStatus,Properties:ApplicationConfigurationDescription.EnvironmentPropertyDescriptions.PropertyGroupDescriptions}'

printf 'DESCRIBE_HISTORICAL_VERSION_WITH_OLD_SECRET\n'
AWS_ACCESS_KEY_ID="$READ_ACCESS" AWS_SECRET_ACCESS_KEY="$READ_SECRET" AWS_SESSION_TOKEN="$READ_TOKEN" \
  aws kinesisanalyticsv2 describe-application-version \
  --application-name "$app_name" --application-version-id 1 \
  --query 'ApplicationVersionDetail.{Version:ApplicationVersionId,Code:ApplicationConfigurationDescription.ApplicationCodeConfigurationDescription.CodeContentDescription.S3ApplicationCodeLocationDescription,Properties:ApplicationConfigurationDescription.EnvironmentPropertyDescriptions.PropertyGroupDescriptions}'

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
rollback_policy="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"kinesisanalytics:RollbackApplication\",\"kinesisanalytics:DescribeApplication\"],\"Resource\":\"${app_arn}\"},{\"Effect\":\"Deny\",\"Action\":\"iam:PassRole\",\"Resource\":\"*\"}]}"
read -r ROLLBACK_ACCESS ROLLBACK_SECRET ROLLBACK_TOKEN < <(
  aws sts assume-role \
    --profile hacktricks-training \
    --role-arn arn:aws:iam::228478051196:role/ChackBotAdministratorRole \
    --role-session-name ht-managed-flink-rollback-only \
    --policy "$rollback_policy" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
)
printf 'ROLLBACK_WITHOUT_PASSROLE\n'
set +e
AWS_ACCESS_KEY_ID="$ROLLBACK_ACCESS" AWS_SECRET_ACCESS_KEY="$ROLLBACK_SECRET" AWS_SESSION_TOKEN="$ROLLBACK_TOKEN" \
  aws kinesisanalyticsv2 rollback-application \
  --application-name "$app_name" --current-application-version-id "$version" 2>&1
rollback_rc=$?
set -e
printf 'ROLLBACK_RC=%s (READY applications cannot be rolled back)\n' "$rollback_rc"

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
aux_policy="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"kinesisanalytics:AddApplicationCloudWatchLoggingOption\",\"kinesisanalytics:AddApplicationVpcConfiguration\",\"kinesisanalytics:DescribeApplication\"],\"Resource\":\"${app_arn}\"},{\"Effect\":\"Deny\",\"Action\":[\"iam:PassRole\",\"logs:*\",\"ec2:*\"],\"Resource\":\"*\"}]}"
read -r AUX_ACCESS AUX_SECRET AUX_TOKEN < <(
  aws sts assume-role \
    --profile hacktricks-training \
    --role-arn arn:aws:iam::228478051196:role/ChackBotAdministratorRole \
    --role-session-name ht-managed-flink-aux-only \
    --policy "$aux_policy" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text
)

printf 'ADD_LOGGING_WITHOUT_PASSROLE_OR_LOGS_PERMISSIONS\n'
AWS_ACCESS_KEY_ID="$AUX_ACCESS" AWS_SECRET_ACCESS_KEY="$AUX_SECRET" AWS_SESSION_TOKEN="$AUX_TOKEN" \
  aws kinesisanalyticsv2 add-application-cloud-watch-logging-option \
  --application-name "$app_name" --current-application-version-id "$version" \
  --cloud-watch-logging-option "LogStreamARN=${log_stream_arn}" \
  --query '{Version:ApplicationVersionId,Logs:CloudWatchLoggingOptionDescriptions,OperationId:OperationId}'

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
printf 'ADD_VPC_WITHOUT_PASSROLE_OR_EC2_PERMISSIONS\n'
AWS_ACCESS_KEY_ID="$AUX_ACCESS" AWS_SECRET_ACCESS_KEY="$AUX_SECRET" AWS_SESSION_TOKEN="$AUX_TOKEN" \
  aws kinesisanalyticsv2 add-application-vpc-configuration \
  --application-name "$app_name" --current-application-version-id "$version" \
  --vpc-configuration "SubnetIds=${subnet_id},SecurityGroupIds=${security_group_id}" \
  --query '{Version:ApplicationVersionId,Vpc:VpcConfigurationDescription,OperationId:OperationId}'

version="$(aws kinesisanalyticsv2 describe-application --application-name "$app_name" --query 'ApplicationDetail.ApplicationVersionId' --output text)"
printf 'EXPLICIT_ROLE_UPDATE_WITH_PASSROLE_DENIED\n'
set +e
AWS_ACCESS_KEY_ID="$UPDATE_ACCESS" AWS_SECRET_ACCESS_KEY="$UPDATE_SECRET" AWS_SESSION_TOKEN="$UPDATE_TOKEN" \
  aws kinesisanalyticsv2 update-application \
  --application-name "$app_name" \
  --current-application-version-id "$version" \
  --service-execution-role-update "$role_arn" 2>&1
role_update_rc=$?
set -e
printf 'ROLE_UPDATE_RC=%s\n' "$role_update_rc"

printf 'FINAL_APP_STATE\n'
aws kinesisanalyticsv2 describe-application --application-name "$app_name" \
  --query 'ApplicationDetail.{Name:ApplicationName,Status:ApplicationStatus,Version:ApplicationVersionId,Role:ServiceExecutionRole,Code:ApplicationConfigurationDescription.ApplicationCodeConfigurationDescription.CodeContentDescription.S3ApplicationCodeLocationDescription,Properties:ApplicationConfigurationDescription.EnvironmentPropertyDescriptions.PropertyGroupDescriptions}'

printf 'CLOUDTRAIL_RECENT_EVENTS\n'
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue="$app_name" \
  --max-results 50 \
  --query 'Events[].{EventName:EventName,Username:Username,EventTime:EventTime}'
