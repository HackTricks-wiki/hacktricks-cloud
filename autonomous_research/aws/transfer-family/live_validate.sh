#!/usr/bin/env bash
set -Eeuo pipefail

# Disposable, us-east-1-only validation. The script refuses to use any profile
# other than the explicitly supplied research profile and only deletes names it
# generated itself with the ht-transfer-audit prefix.
export AWS_PROFILE="${AWS_PROFILE:-ht-admin}"
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_DEFAULT_OUTPUT=json
export AWS_PAGER=''

[[ "$AWS_PROFILE" == "ht-admin" ]] || { echo "Refusing profile: $AWS_PROFILE" >&2; exit 2; }

RUN_ID="${RUN_ID:-$(date -u +%Y%m%d%H%M%S)-$RANDOM}"
CONNECTOR_ONLY="${CONNECTOR_ONLY:-0}"
PREFIX="ht-transfer-audit-$RUN_ID"
BUCKET="$PREFIX"
TRANSFER_ROLE="$PREFIX-transfer-role"
LAMBDA_ROLE="$PREFIX-lambda-role"
FUNCTION_NAME="$PREFIX-idp"
SECRET_NAME="aws/transfer/$PREFIX"
TAG_KEY="HackTricksResearch"
TAG_VALUE="$RUN_ID"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(mktemp -d)"
START_EPOCH="$(date -u +%s)"
START_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

SERVER_ID=''
CONNECTOR_ID=''
WORKFLOW_ID=''
SECRET_ARN=''
FUNCTION_ARN=''

assert_owned_name() {
  [[ "$1" == ht-transfer-audit-* ]] || {
    echo "Cleanup target is outside the generated prefix: $1" >&2
    return 1
  }
}

cleanup() {
  local rc=$?
  set +e
  echo "cleanup-begin rc=$rc"

  if [[ -n "$CONNECTOR_ID" ]]; then
    aws transfer delete-connector --connector-id "$CONNECTOR_ID" >/dev/null
    aws logs delete-log-group --log-group-name "/aws/transfer/$CONNECTOR_ID" >/dev/null 2>&1
  fi

  if [[ -n "$SERVER_ID" ]]; then
    aws transfer delete-user --server-id "$SERVER_ID" --user-name audit-user >/dev/null 2>&1
    aws transfer stop-server --server-id "$SERVER_ID" >/dev/null 2>&1
    for _ in {1..40}; do
      [[ "$(aws transfer describe-server --server-id "$SERVER_ID" --query 'Server.State' --output text 2>/dev/null)" == "OFFLINE" ]] && break
      sleep 5
    done
    aws transfer delete-server --server-id "$SERVER_ID" >/dev/null 2>&1
  fi

  if [[ -n "$WORKFLOW_ID" ]]; then
    aws transfer delete-workflow --workflow-id "$WORKFLOW_ID" >/dev/null 2>&1
  fi

  if [[ -n "$SECRET_ARN" ]]; then
    aws secretsmanager delete-secret --secret-id "$SECRET_ARN" --force-delete-without-recovery >/dev/null
  fi

  if [[ -n "$FUNCTION_ARN" ]]; then
    assert_owned_name "$FUNCTION_NAME" && aws lambda delete-function --function-name "$FUNCTION_NAME" >/dev/null
    aws logs delete-log-group --log-group-name "/aws/lambda/$FUNCTION_NAME" >/dev/null 2>&1
  fi

  assert_owned_name "$TRANSFER_ROLE" && aws iam delete-role-policy --role-name "$TRANSFER_ROLE" --policy-name research >/dev/null 2>&1
  assert_owned_name "$TRANSFER_ROLE" && aws iam delete-role --role-name "$TRANSFER_ROLE" >/dev/null 2>&1
  assert_owned_name "$LAMBDA_ROLE" && aws iam delete-role-policy --role-name "$LAMBDA_ROLE" --policy-name research >/dev/null 2>&1
  assert_owned_name "$LAMBDA_ROLE" && aws iam delete-role --role-name "$LAMBDA_ROLE" >/dev/null 2>&1

  if assert_owned_name "$BUCKET"; then
    aws s3 rm "s3://$BUCKET" --recursive >/dev/null 2>&1
    aws s3api delete-bucket --bucket "$BUCKET" >/dev/null 2>&1
  fi

  rm -rf -- "$WORK_DIR"
  echo "cleanup-end"
  return "$rc"
}
trap cleanup EXIT

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
CALLER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
[[ "$CALLER_ARN" == arn:aws:sts::"$ACCOUNT_ID":assumed-role/ChackBotAdministratorRole/* ]] || {
  echo "Unexpected caller: $CALLER_ARN" >&2
  exit 2
}

echo "run-id=$RUN_ID caller=$CALLER_ARN"

aws s3api create-bucket --bucket "$BUCKET" >/dev/null
aws s3api put-bucket-tagging --bucket "$BUCKET" --tagging "TagSet=[{Key=$TAG_KEY,Value=$TAG_VALUE}]"
aws s3api put-object --bucket "$BUCKET" --key remote/victim.txt --body "$SCRIPT_DIR/fixture-object.txt" >/dev/null
aws s3api put-object --bucket "$BUCKET" --key local/to-send.txt --body "$SCRIPT_DIR/fixture-object.txt" >/dev/null

TRANSFER_TRUST="$(jq -nc --arg account "$ACCOUNT_ID" '{Version:"2012-10-17",Statement:[{Effect:"Allow",Principal:{Service:"transfer.amazonaws.com"},Action:"sts:AssumeRole",Condition:{StringEquals:{"aws:SourceAccount":$account},ArnLike:{"aws:SourceArn":("arn:aws:transfer:us-east-1:"+$account+":*")}}}]}')"
LAMBDA_TRUST='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam create-role --role-name "$TRANSFER_ROLE" --assume-role-policy-document "$TRANSFER_TRUST" --tags "Key=$TAG_KEY,Value=$TAG_VALUE" >/dev/null
TRANSFER_ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$TRANSFER_ROLE"
TRANSFER_POLICY="$(jq -nc --arg bucket "$BUCKET" --arg secret "arn:aws:secretsmanager:us-east-1:$ACCOUNT_ID:secret:aws/transfer/$PREFIX*" '{Version:"2012-10-17",Statement:[{Effect:"Allow",Action:["s3:ListBucket","s3:GetBucketLocation"],Resource:("arn:aws:s3:::"+$bucket)},{Effect:"Allow",Action:["s3:GetObject","s3:GetObjectVersion","s3:PutObject","s3:DeleteObject","s3:GetObjectTagging","s3:PutObjectTagging"],Resource:("arn:aws:s3:::"+$bucket+"/*")},{Effect:"Allow",Action:"secretsmanager:GetSecretValue",Resource:$secret},{Effect:"Allow",Action:["logs:CreateLogGroup","logs:CreateLogStream","logs:DescribeLogStreams","logs:PutLogEvents"],Resource:"arn:aws:logs:us-east-1:*:log-group:/aws/transfer/*"}]}')"
aws iam put-role-policy --role-name "$TRANSFER_ROLE" --policy-name research --policy-document "$TRANSFER_POLICY"

ssh-keygen -q -t rsa -b 3072 -N '' -C "$PREFIX-user" -f "$WORK_DIR/user_key"
ssh-keygen -q -t rsa -b 3072 -N '' -C "$PREFIX-host" -f "$WORK_DIR/host_key"
USER_PUBLIC_KEY="$(<"$WORK_DIR/user_key.pub")"

if [[ "$CONNECTOR_ONLY" == 1 ]]; then
  SERVER_ID="$(aws transfer create-server \
    --domain S3 \
    --endpoint-type PUBLIC \
    --host-key "$(<"$WORK_DIR/host_key")" \
    --identity-provider-type SERVICE_MANAGED \
    --protocols SFTP \
    --tags "Key=$TAG_KEY,Value=$TAG_VALUE" \
    --query ServerId --output text)"
else
  aws iam create-role --role-name "$LAMBDA_ROLE" --assume-role-policy-document "$LAMBDA_TRUST" --tags "Key=$TAG_KEY,Value=$TAG_VALUE" >/dev/null
  LAMBDA_ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$LAMBDA_ROLE"
  LAMBDA_POLICY="$(jq -nc --arg account "$ACCOUNT_ID" '{Version:"2012-10-17",Statement:[{Effect:"Allow",Action:["logs:CreateLogGroup"],Resource:("arn:aws:logs:us-east-1:"+$account+":*")},{Effect:"Allow",Action:["logs:CreateLogStream","logs:PutLogEvents"],Resource:("arn:aws:logs:us-east-1:"+$account+":log-group:/aws/lambda/ht-transfer-audit-*:*")}]}')"
  aws iam put-role-policy --role-name "$LAMBDA_ROLE" --policy-name research --policy-document "$LAMBDA_POLICY"

  (cd "$SCRIPT_DIR/lambda_idp" && zip -q "$WORK_DIR/idp.zip" index.mjs)
  for _ in {1..12}; do
    if FUNCTION_ARN="$(aws lambda create-function \
      --function-name "$FUNCTION_NAME" \
      --runtime nodejs22.x \
      --handler index.handler \
      --role "$LAMBDA_ROLE_ARN" \
      --zip-file "fileb://$WORK_DIR/idp.zip" \
      --environment "Variables={TRANSFER_USER_ROLE=$TRANSFER_ROLE_ARN,TRANSFER_BUCKET=$BUCKET,TRANSFER_USER_PUBLIC_KEY=\"$USER_PUBLIC_KEY\",TRANSFER_TEST_PASSWORD=Correct-Transfer-Audit-Password}" \
      --tags "$TAG_KEY=$TAG_VALUE" \
      --query FunctionArn --output text 2>/dev/null)"; then
      break
    fi
    sleep 5
  done
  [[ -n "$FUNCTION_ARN" && "$FUNCTION_ARN" != None ]] || { echo "Lambda creation failed" >&2; exit 1; }
  aws lambda add-permission --function-name "$FUNCTION_NAME" --statement-id transfer-audit --action lambda:InvokeFunction --principal transfer.amazonaws.com --source-account "$ACCOUNT_ID" >/dev/null

  SERVER_ID="$(aws transfer create-server \
    --domain S3 \
    --endpoint-type PUBLIC \
    --host-key "$(<"$WORK_DIR/host_key")" \
    --identity-provider-type AWS_LAMBDA \
    --identity-provider-details "$(jq -nc --arg fn "$FUNCTION_ARN" '{Function:$fn,SftpAuthenticationMethods:"PUBLIC_KEY_OR_PASSWORD"}')" \
    --protocols SFTP \
    --tags "Key=$TAG_KEY,Value=$TAG_VALUE" \
    --query ServerId --output text)"
fi
echo "server-id=$SERVER_ID"

for _ in {1..40}; do
  [[ "$(aws transfer describe-server --server-id "$SERVER_ID" --query 'Server.State' --output text)" == "ONLINE" ]] && break
  sleep 5
done

if [[ "$CONNECTOR_ONLY" != 1 ]]; then
  echo 'test-idp-no-password'
  aws transfer test-identity-provider --server-id "$SERVER_ID" --server-protocol SFTP --source-ip 127.0.0.1 --user-name audit-user
  echo 'test-idp-wrong-password'
  aws transfer test-identity-provider --server-id "$SERVER_ID" --server-protocol SFTP --source-ip 127.0.0.1 --user-name audit-user --user-password Wrong-Password
  echo 'test-idp-correct-password'
  aws transfer test-identity-provider --server-id "$SERVER_ID" --server-protocol SFTP --source-ip 127.0.0.1 --user-name audit-user --user-password Correct-Transfer-Audit-Password

  aws transfer stop-server --server-id "$SERVER_ID"
  for _ in {1..40}; do
    [[ "$(aws transfer describe-server --server-id "$SERVER_ID" --query 'Server.State' --output text)" == "OFFLINE" ]] && break
    sleep 5
  done
  aws transfer update-server --server-id "$SERVER_ID" --identity-provider-type SERVICE_MANAGED >/dev/null
  aws transfer start-server --server-id "$SERVER_ID"
  for _ in {1..40}; do
    [[ "$(aws transfer describe-server --server-id "$SERVER_ID" --query 'Server.State' --output text)" == "ONLINE" ]] && break
    sleep 5
  done
fi

aws transfer create-user \
  --server-id "$SERVER_ID" \
  --user-name audit-user \
  --role "$TRANSFER_ROLE_ARN" \
  --home-directory-type LOGICAL \
  --home-directory-mappings "$(jq -nc --arg target "/$BUCKET/remote" '[{Entry:"/",Target:$target}]')" \
  --tags "Key=$TAG_KEY,Value=$TAG_VALUE" >/dev/null
SSH_KEY_ID="$(aws transfer import-ssh-public-key --server-id "$SERVER_ID" --user-name audit-user --ssh-public-key-body "$USER_PUBLIC_KEY" --query SshPublicKeyId --output text)"
echo "imported-ssh-key-id=$SSH_KEY_ID"

ENDPOINT="$SERVER_ID.server.transfer.us-east-1.amazonaws.com"
if [[ "$CONNECTOR_ONLY" != 1 ]]; then
  for _ in {1..30}; do
    ssh-keyscan -T 3 -t rsa "$ENDPOINT" >"$WORK_DIR/keyscan" 2>/dev/null && [[ -s "$WORK_DIR/keyscan" ]] && break
    sleep 5
  done
  echo 'sftp-key-injection-access'
  sftp -q -oBatchMode=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i "$WORK_DIR/user_key" "audit-user@$ENDPOINT" <<<'ls -l'
fi

if [[ "$CONNECTOR_ONLY" != 1 ]]; then
  WORKFLOW_ID="$(aws transfer create-workflow \
    --description "$PREFIX copy validation" \
    --steps "$(jq -nc --arg bucket "$BUCKET" '[{Type:"COPY",CopyStepDetails:{Name:"copy-upload",DestinationFileLocation:{S3FileLocation:{Bucket:$bucket,Key:"workflow-copy/"}},OverwriteExisting:"TRUE",SourceFileLocation:"${original.file}"}}]')" \
    --tags "Key=$TAG_KEY,Value=$TAG_VALUE" \
    --query WorkflowId --output text)"
  aws transfer update-server --server-id "$SERVER_ID" --workflow-details "$(jq -nc --arg workflow "$WORKFLOW_ID" --arg role "$TRANSFER_ROLE_ARN" '{OnUpload:[{WorkflowId:$workflow,ExecutionRole:$role}]}')" >/dev/null
  sftp -q -oBatchMode=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i "$WORK_DIR/user_key" "audit-user@$ENDPOINT" <<EOF
put $SCRIPT_DIR/fixture-object.txt workflow-trigger.txt
EOF
  for _ in {1..30}; do
    aws s3api head-object --bucket "$BUCKET" --key workflow-copy/workflow-trigger.txt >/dev/null 2>&1 && break
    sleep 3
  done
  aws s3api head-object --bucket "$BUCKET" --key workflow-copy/workflow-trigger.txt --query '{Size:ContentLength,Modified:LastModified}'
fi

SECRET_STRING="$(jq -n --arg username audit-user --rawfile privateKey "$WORK_DIR/user_key" '{Username:$username,PrivateKey:$privateKey}')"
SECRET_ARN="$(aws secretsmanager create-secret --name "$SECRET_NAME" --secret-string "$SECRET_STRING" --tags "Key=$TAG_KEY,Value=$TAG_VALUE" --query ARN --output text)"
HOST_PUBLIC_KEY="$(awk '{print $1, $2}' "$WORK_DIR/host_key.pub")"

CONNECTOR_ID="$(aws transfer create-connector \
  --url "sftp://$ENDPOINT" \
  --access-role "$TRANSFER_ROLE_ARN" \
  --logging-role "$TRANSFER_ROLE_ARN" \
  --sftp-config "$(jq -nc --arg secret "$SECRET_ARN" --arg host "$HOST_PUBLIC_KEY" '{UserSecretId:$secret,TrustedHostKeys:[$host],MaxConcurrentConnections:1}')" \
  --tags "Key=$TAG_KEY,Value=$TAG_VALUE" \
  --query ConnectorId --output text)"
echo "connector-id=$CONNECTOR_ID"
for _ in {1..20}; do
  CONNECTION_STATUS="$(aws transfer test-connection --connector-id "$CONNECTOR_ID" --query Status --output text 2>/dev/null || true)"
  [[ "$CONNECTION_STATUS" == OK ]] && break
  sleep 5
done
echo "connector-status=$CONNECTION_STATUS"

LISTING_ID="$(aws transfer start-directory-listing --connector-id "$CONNECTOR_ID" --remote-directory-path / --output-directory-path "/$BUCKET/listings" --query ListingId --output text)"
echo "directory-listing-id=$LISTING_ID"

SEND_ID="$(aws transfer start-file-transfer --connector-id "$CONNECTOR_ID" --send-file-paths "/$BUCKET/local/to-send.txt" --remote-directory-path / --query TransferId --output text)"
echo "send-transfer-id=$SEND_ID"
for _ in {1..30}; do
  SEND_STATUS="$(aws transfer list-file-transfer-results --connector-id "$CONNECTOR_ID" --transfer-id "$SEND_ID" --query 'FileTransferResults[0].StatusCode' --output text 2>/dev/null || true)"
  [[ "$SEND_STATUS" == COMPLETED || "$SEND_STATUS" == FAILED ]] && break
  sleep 3
done
aws transfer list-file-transfer-results --connector-id "$CONNECTOR_ID" --transfer-id "$SEND_ID"

RETRIEVE_ID="$(aws transfer start-file-transfer --connector-id "$CONNECTOR_ID" --retrieve-file-paths /victim.txt --local-directory-path "/$BUCKET/retrieved" --query TransferId --output text)"
echo "retrieve-transfer-id=$RETRIEVE_ID"
for _ in {1..30}; do
  RETRIEVE_STATUS="$(aws transfer list-file-transfer-results --connector-id "$CONNECTOR_ID" --transfer-id "$RETRIEVE_ID" --query 'FileTransferResults[0].StatusCode' --output text 2>/dev/null || true)"
  [[ "$RETRIEVE_STATUS" == COMPLETED || "$RETRIEVE_STATUS" == FAILED ]] && break
  sleep 3
done
aws transfer list-file-transfer-results --connector-id "$CONNECTOR_ID" --transfer-id "$RETRIEVE_ID"

MOVE_ID="$(aws transfer start-remote-move --connector-id "$CONNECTOR_ID" --source-path /to-send.txt --target-path /moved.txt --query MoveId --output text)"
echo "remote-move-id=$MOVE_ID"
sleep 5
DELETE_ID="$(aws transfer start-remote-delete --connector-id "$CONNECTOR_ID" --delete-path /moved.txt --query DeleteId --output text)"
echo "remote-delete-id=$DELETE_ID"
sleep 5

echo 'connector-cloudwatch-events'
aws logs filter-log-events --log-group-name "/aws/transfer/$CONNECTOR_ID" --start-time "$((START_EPOCH * 1000))" --query 'events[].message' --output json || true

echo 'cloudtrail-transfer-events'
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventSource,AttributeValue=transfer.amazonaws.com \
  --start-time "$START_TIME" \
  --query 'Events[].{Name:EventName,Time:EventTime,User:Username,Resources:Resources}'

echo 'validation-complete; cleanup follows'
