# Bash script to enumerate KMS keys and information about them
#!/bin/bash

# Function to print in red
print_red() {
    printf "\e[91m%s\e[0m" "$1"
}

# Function to print policy details
print_policy_details() {
    local policy_name=$1
    local policy_document=$2

    echo -e "\n\tPolicy details for: \"$policy_name\""
    # Iterate over each statement in the policy document
    for i in $(jq -c '.Statement[]' <<< "$policy_document"); do
        # Extract action, resource, effect, and principal from the statement
        action=$(jq -r '.Action | if type == "array" then "[" + join(", ") + "]" else . end' <<< "$i")
        resource=$(jq -r '.Resource | if type == "array" then "[" + join(", ") + "]" else . end' <<< "$i")
        effect=$(jq -r '.Effect | if type == "array" then "[" + join(", ") + "]" else . end' <<< "$i")
        principal=$(jq -r '.Principal.AWS | if type == "array" then "[" + join(", ") + "]" else . end' <<< "$i")

        # Print the details
        echo -e "\n\t\t- Action: $action"
        echo -e "\t\t- Resource: $resource"
        echo -e "\t\t- Effect: $effect"
        echo -e "\t\t- Principal: $principal"
    done
}

# Run the AWS CLI command to list KMS keys and extract IDs
keys=$(aws kms list-keys --query 'Keys[].KeyId' | jq -r '.[]')

# Iterate over each key
for key in $keys; do

    # Flag to track if Access Denied is encountered
    access_denied=false

    # Retrieve key policies and check for AccessDeniedException
    policies=$(aws kms list-key-policies --key-id $key --query 'PolicyNames[]' 2>&1)

    if echo "$policies" | grep -q "AccessDeniedException"; then
        access_denied=true
        echo -n "Key ID: $key - "
        print_red "Access Denied!"
    else
        # Print key description information
        key_info=$(aws kms describe-key --key-id $key --query 'KeyMetadata.{Manager: KeyManager, Enabled: Enabled, Description: Description, KeyState: KeyState}')
        echo "Key ID: $key"
        echo "$key_info" | jq -r '"\n\tBasic Info:\n\n\t\t- Managed By: \(.Manager)\n\t\t- Enabled: \(.Enabled)\n\t\t- Description: \(.Description)\n\t\t- KeyState: \(.KeyState)"'
        
        # Retrieve policy details and print output
        for policy in $(echo "$policies" | jq -r '.[]'); do
            policy_document=$(aws kms get-key-policy --key-id $key --policy-name $policy --query 'Policy' | jq -r '.')
            print_policy_details "$policy" "$policy_document"
        done
    fi
    echo ""
done