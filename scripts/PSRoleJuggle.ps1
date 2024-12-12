# PowerShell script to check for role juggling possibilities using AWS CLI

# Check for AWS CLI installation
if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed. Please install it and configure it with 'aws configure'."
    exit
}

# Function to list IAM roles
function List-IAMRoles {
    aws iam list-roles --query "Roles[*].{RoleName:RoleName, Arn:Arn}" --output json
}

# Initialize error count
$errorCount = 0

# List all roles
$roles = List-IAMRoles | ConvertFrom-Json

# Attempt to assume each role
foreach ($role in $roles) {
    $sessionName = "RoleJugglingTest-" + (Get-Date -Format FileDateTime)
    try {
        $credentials = aws sts assume-role --role-arn $role.Arn --role-session-name $sessionName --query "Credentials" --output json 2>$null | ConvertFrom-Json
        if ($credentials) {
            Write-Host "Successfully assumed role: $($role.RoleName)"
            Write-Host "Access Key: $($credentials.AccessKeyId)"
            Write-Host "Secret Access Key: $($credentials.SecretAccessKey)"
            Write-Host "Session Token: $($credentials.SessionToken)"
            Write-Host "Expiration: $($credentials.Expiration)"

            # Set temporary credentials to assume the next role
            $env:AWS_ACCESS_KEY_ID = $credentials.AccessKeyId
            $env:AWS_SECRET_ACCESS_KEY = $credentials.SecretAccessKey
            $env:AWS_SESSION_TOKEN = $credentials.SessionToken

            # Try to assume another role using the temporary credentials
            foreach ($nextRole in $roles) {
                if ($nextRole.Arn -ne $role.Arn) {
                    $nextSessionName = "RoleJugglingTest-" + (Get-Date -Format FileDateTime)
                    try {
                        $nextCredentials = aws sts assume-role --role-arn $nextRole.Arn --role-session-name $nextSessionName --query "Credentials" --output json 2>$null | ConvertFrom-Json
                        if ($nextCredentials) {
                            Write-Host "Also successfully assumed role: $($nextRole.RoleName) from $($role.RoleName)"
                            Write-Host "Access Key: $($nextCredentials.AccessKeyId)"
                            Write-Host "Secret Access Key: $($nextCredentials.SecretAccessKey)"
                            Write-Host "Session Token: $($nextCredentials.SessionToken)"
                            Write-Host "Expiration: $($nextCredentials.Expiration)"
                        }
                    } catch {
                        $errorCount++
                    }
                }
            }

            # Reset environment variables
            Remove-Item Env:\AWS_ACCESS_KEY_ID
            Remove-Item Env:\AWS_SECRET_ACCESS_KEY
            Remove-Item Env:\AWS_SESSION_TOKEN
        } else {
            $errorCount++
        }
    } catch {
        $errorCount++
    }
}

# Output the number of errors if any
if ($errorCount -gt 0) {
    Write-Host "$errorCount error(s) occurred during role assumption attempts."
} else {
    Write-Host "No errors occurred. All roles checked successfully."
}

Write-Host "Role juggling check complete."
