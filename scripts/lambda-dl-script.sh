#!/bin/bash

# Define the AWS profile
PROFILE='blackbox1'

FUNCTION_NAMES=$(aws lambda list-functions --profile $PROFILE | jq -r '.Functions[] | select(.FunctionName | test("blackbox")) | .FunctionName')

# Loop through the function names to get their code URL and download the code
for FUNCTION_NAME in $FUNCTION_NAMES; do
    echo "Processing $FUNCTION_NAME..."

    # Get the URL to download the function's code
    FUNCTION_URL=$(aws lambda get-function --function-name "$FUNCTION_NAME" --profile $PROFILE | jq -r '.Code.Location')

    # Check if the URL is valid
    if [ ! -z "$FUNCTION_URL" ]; then
        # Use wget to download the function code package
        echo "Downloading code for $FUNCTION_NAME..."
        wget -O "${FUNCTION_NAME}.zip" "$FUNCTION_URL"
    else
        echo "Failed to obtain download URL for $FUNCTION_NAME"
    fi
done

echo "Download completed for all targeted Lambda functions."
