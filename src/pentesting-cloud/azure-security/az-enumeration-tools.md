# Az - Enumeration Tools

{{#include ../../banners/hacktricks-training.md}}

## Install PowerShell in Linux

> [!TIP]
> In linux you will need to install PowerShell Core:

```bash
sudo apt-get update
sudo apt-get install -y wget apt-transport-https software-properties-common

# Ubuntu 20.04
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb

# Update repos
sudo apt-get update
sudo add-apt-repository universe

# Install & start powershell
sudo apt-get install -y powershell
pwsh

# Az cli
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

## Install PowerShell in MacOS

Instructions from the [**documentation**](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-macos?view=powershell-7.4):

1. Install `brew` if not installed yet:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install the latest stable release of PowerShell:

```sh
brew install powershell/tap/powershell
```

3. Run PowerShell:

```sh
pwsh
```

4. Update:

```sh
brew update
brew upgrade powershell
```

## Main Enumeration Tools

### az cli

[**Azure Command-Line Interface (CLI)**](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) is a cross-platform tool written in Python for managing and administering (most) Azure and Entra ID resources. It connects to Azure and executes administrative commands via the command line or scripts.

Follow this link for the [**installation instructions¡**](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli#install).

Commands in Azure CLI are structured using a pattern of: `az <service> <action> <parameters>`

#### Debug | MitM az cli

Using the parameter **`--debug`** it's possible to see all the requests the tool **`az`** is sending:

```bash
az account management-group list --output table --debug
```

In order to do a **MitM** to the tool and **check all the requests** it's sending manually you can do:

{{#tabs }}
{{#tab name="Bash" }}

```bash
export ADAL_PYTHON_SSL_NO_VERIFY=1
export AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1
export HTTPS_PROXY="http://127.0.0.1:8080"
export HTTP_PROXY="http://127.0.0.1:8080"

# If this is not enough
# Download the certificate from Burp and convert it into .pem format
# And export the following env variable
openssl x509 -in ~/Downloads/cacert.der -inform DER -out ~/Downloads/cacert.pem -outform PEM
export REQUESTS_CA_BUNDLE=/Users/user/Downloads/cacert.pem
```

{{#endtab }}

{{#tab name="CMD" }}

```bash
set ADAL_PYTHON_SSL_NO_VERIFY=1
set AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1
set HTTPS_PROXY="http://127.0.0.1:8080"
set HTTP_PROXY="http://127.0.0.1:8080"

# If this is not enough
# Download the certificate from Burp and convert it into .pem format
# And export the following env variable
openssl x509 -in cacert.der -inform DER -out cacert.pem -outform PEM
set REQUESTS_CA_BUNDLE=C:\Users\user\Downloads\cacert.pem
```

{{#endtab }}

{{#tab name="PS" }}

```bash
$env:ADAL_PYTHON_SSL_NO_VERIFY=1
$env:AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1
$env:HTTPS_PROXY="http://127.0.0.1:8080"
$env:HTTP_PROXY="http://127.0.0.1:8080"
```

{{#endtab }}
{{#endtabs }}

<details>
<summary><strong>Fixing “CA cert does not include key usage extension”</strong></summary>

### Why the error happens

When Azure CLI authenticates, it makes HTTPS requests (via MSAL → Requests → OpenSSL). If you’re intercepting TLS with Burp, Burp generates “on the fly” certificates for sites like `login.microsoftonline.com` and signs them with Burp’s CA.

On newer stacks (Python 3.13 + OpenSSL 3), CA validation is stricter:

- A CA certificate must include **Basic Constraints: `CA:TRUE`** and a **Key Usage** extension permitting certificate signing (**`keyCertSign`**, and typically **`cRLSign`**).

Burp’s default CA (PortSwigger CA) is old and typically lacks the Key Usage extension, so OpenSSL rejects it even if you “trust it”.

That produces errors like:

- `CA cert does not include key usage extension`
- `CERTIFICATE_VERIFY_FAILED`
- `self-signed certificate in certificate chain`

So you must:

1. Create a modern CA (with proper Key Usage).
2. Make Burp use it to sign intercepted certs.
3. Trust that CA in macOS.
4. Point Azure CLI / Requests to that CA bundle.

### Step-by-step: working configuration

#### 0) Prereqs

- Burp running locally (proxy at `127.0.0.1:8080`)
- Azure CLI installed (Homebrew)
- You can `sudo` (to trust the CA in the system keychain)

#### 1) Create a standards-compliant Burp CA (PEM + KEY)

Create an OpenSSL config file that explicitly sets CA extensions:

```bash
mkdir -p ~/burp-ca && cd ~/burp-ca

cat > burp-ca.cnf <<'EOF'
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
x509_extensions    = v3_ca

[ dn ]
C  = US
O  = Burp Custom CA
CN = Burp Custom Root CA

[ v3_ca ]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF
```

Generate the CA certificate + private key:

```bash
openssl req -x509 -new -nodes \
  -days 3650 \
  -keyout burp-ca.key \
  -out burp-ca.pem \
  -config burp-ca.cnf
```

Sanity check (you MUST see Key Usage):

```bash
openssl x509 -in burp-ca.pem -noout -text | egrep -A3 "Basic Constraints|Key Usage"
```

Expected to include something like:

- `CA:TRUE`
- `Key Usage: ... Certificate Sign, CRL Sign`

#### 2) Convert to PKCS#12 (Burp import format)

Burp needs certificate + private key, easiest as PKCS#12:

```bash
openssl pkcs12 -export \
  -out burp-ca.p12 \
  -inkey burp-ca.key \
  -in burp-ca.pem \
  -name "Burp Custom Root CA"
```

You’ll be prompted for an export password (set one; Burp will ask for it).

#### 3) Import the CA into Burp and restart Burp

In Burp:

- Proxy → Options
- Find Import / export CA certificate
- Click Import CA certificate
- Choose PKCS#12
- Select `burp-ca.p12`
- Enter the password
- Restart Burp completely (important)

Why restart? Burp may keep using the old CA until restart.

#### 4) Trust the new CA in macOS system keychain

This allows system apps and many TLS stacks to trust the CA.

```bash
sudo security add-trusted-cert \
  -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/burp-ca/burp-ca.pem
```

(If you prefer GUI: Keychain Access → System → Certificates → import → set “Always Trust”.)

#### 5) Configure proxy env vars

```bash
export HTTPS_PROXY="http://127.0.0.1:8080"
export HTTP_PROXY="http://127.0.0.1:8080"
```

#### 6) Configure Requests/Azure CLI to trust your Burp CA

Azure CLI uses Python Requests internally; set both of these:

```bash
export REQUESTS_CA_BUNDLE="$HOME/burp-ca/burp-ca.pem"
export SSL_CERT_FILE="$HOME/burp-ca/burp-ca.pem"
```

Notes:

- `REQUESTS_CA_BUNDLE` is used by Requests.
- `SSL_CERT_FILE` helps for other TLS consumers and edge cases.
- You typically do not need the old `ADAL_PYTHON_SSL_NO_VERIFY` / `AZURE_CLI_DISABLE_CONNECTION_VERIFICATION` once the CA is correct.

#### 7) Verify Burp is actually signing with your new CA (critical check)

This confirms your interception chain is correct:

```bash
openssl s_client -connect login.microsoftonline.com:443 \
  -proxy 127.0.0.1:8080 </dev/null 2>/dev/null \
  | openssl x509 -noout -issuer
```

Expected issuer contains your CA name, e.g.:

`O=Burp Custom CA, CN=Burp Custom Root CA`

If you still see PortSwigger CA, Burp is not using your imported CA → re-check import and restart.

#### 8) Verify Python Requests works through Burp

```bash
python3 - <<'EOF'
import requests
requests.get("https://login.microsoftonline.com")
print("OK")
EOF
```

Expected: `OK`

#### 9) Azure CLI test

```bash
az account get-access-token --resource=https://management.azure.com/
```

If you’re already logged in, it should return JSON with an `accessToken`.

</details>

### Az PowerShell

Azure PowerShell is a module with cmdlets for managing Azure resources directly from the PowerShell command line.

Follow this link for the [**installation instructions**](https://learn.microsoft.com/en-us/powershell/azure/install-azure-powershell).

Commands in Azure PowerShell AZ Module are structured like: `<Action>-Az<Service> <parameters>`

#### Debug | MitM Az PowerShell

Using the parameter **`-Debug`** it's possible to see all the requests the tool is sending:

```bash
Get-AzResourceGroup -Debug
```

In order to do a **MitM** to the tool and **check all the requests** it's sending manually you can set the env variables `HTTPS_PROXY` and `HTTP_PROXY` according to the [**docs**](https://learn.microsoft.com/en-us/powershell/azure/az-powershell-proxy).

### Microsoft Graph PowerShell

Microsoft Graph PowerShell is a cross-platform SDK that enables access to all Microsoft Graph APIs, including services like SharePoint, Exchange, and Outlook, using a single endpoint. It supports PowerShell 7+, modern authentication via MSAL, external identities, and advanced queries. With a focus on least privilege access, it ensures secure operations and receives regular updates to align with the latest Microsoft Graph API features.

Follow this link for the [**installation instructions**](https://learn.microsoft.com/en-us/powershell/microsoftgraph/installation).

Commands in Microsoft Graph PowerShell are structured like: `<Action>-Mg<Service> <parameters>`

#### Debug Microsoft Graph PowerShell

Using the parameter **`-Debug`** it's possible to see all the requests the tool is sending:

```bash
Get-MgUser -Debug
```

### ~~**AzureAD Powershell**~~

The Azure Active Directory (AD) module, now **deprecated**, is part of Azure PowerShell for managing Azure AD resources. It provides cmdlets for tasks like managing users, groups, and application registrations in Entra ID.

> [!TIP]
> This is replaced by Microsoft Graph PowerShell

Follow this link for the [**installation instructions**](https://www.powershellgallery.com/packages/AzureAD).


## Automated Recon & Compliance Tools

### [turbot azure plugins](https://github.com/orgs/turbot/repositories?q=mod-azure)

Turbot with steampipe and powerpipe allows to gather information from Azure and Entra ID and perform compliance checks and find misconfigurations. The currently most recommended Azure modules to run are:

- [https://github.com/turbot/steampipe-mod-azure-compliance](https://github.com/turbot/steampipe-mod-azure-compliance)
- [https://github.com/turbot/steampipe-mod-azure-insights](https://github.com/turbot/steampipe-mod-azure-insights)
- [https://github.com/turbot/steampipe-mod-azuread-insights](https://github.com/turbot/steampipe-mod-azuread-insights)

```bash
# Install
brew install turbot/tap/powerpipe
brew install turbot/tap/steampipe
steampipe plugin install azure
steampipe plugin install azuread

# Config creds via env vars or az cli default creds will be used
export AZURE_ENVIRONMENT="AZUREPUBLICCLOUD"
export AZURE_TENANT_ID="<tenant-id>"
export AZURE_SUBSCRIPTION_ID="<subscription-id>"
export AZURE_CLIENT_ID="<client-id>"
export AZURE_CLIENT_SECRET="<secret>"

# Run steampipe-mod-azure-insights
cd /tmp
mkdir dashboards
cd dashboards
powerpipe mod init
powerpipe mod install github.com/turbot/steampipe-mod-azure-insights
steampipe service start
powerpipe server
# Go to http://localhost:9033 in a browser
```

### [Prowler](https://github.com/prowler-cloud/prowler)

Prowler is an Open Source security tool to perform AWS, Azure, Google Cloud and Kubernetes security best practices assessments, audits, incident response, continuous monitoring, hardening  and forensics readiness.

It basically would allow us to run hundreds of checks against an Azure environment to find security misconfigurations and gather the results in json (and other text format) or check them in the web.

```bash
# Create a application with Reader role and set the tenant ID, client ID and secret in prowler so it access the app

# Launch web with docker-compose
export DOCKER_DEFAULT_PLATFORM=linux/amd64
curl -LO https://raw.githubusercontent.com/prowler-cloud/prowler/refs/heads/master/docker-compose.yml
curl -LO https://raw.githubusercontent.com/prowler-cloud/prowler/refs/heads/master/.env
## If using an old docker-compose version, change the "env_file" params to: env_file: ".env"
docker compose up -d
# Access the web and configure the access to run a scan from it

# Prowler cli
python3 -m pip install prowler --break-system-packages
docker run --rm toniblyx/prowler:v4-latest azure --list-checks
docker run --rm toniblyx/prowler:v4-latest azure --list-services
docker run --rm toniblyx/prowler:v4-latest azure --list-compliance
docker run --rm -e "AZURE_CLIENT_ID=<client-id>" -e "AZURE_TENANT_ID=<tenant-id>" -e "AZURE_CLIENT_SECRET=<secret>" toniblyx/prowler:v4-latest azure --sp-env-auth
## It also support other authentication types, check: prowler azure --help
```

### [Monkey365](https://github.com/silverhack/monkey365)

It allows to perform Azure subscriptions and Microsoft Entra ID security configuration reviews automatically.

The HTML reports are stored inside the `./monkey-reports` directory inside the github repository folder.

```bash
git clone https://github.com/silverhack/monkey365
Get-ChildItem -Recurse monkey365 | Unblock-File
cd monkey365
Import-Module ./monkey365
mkdir /tmp/monkey365-scan
cd /tmp/monkey365-scan

Get-Help Invoke-Monkey365
Get-Help Invoke-Monkey365 -Detailed

# Scan with user creds (browser will be run)
Invoke-Monkey365 -TenantId <tenant-id> -Instance Azure -Collect All -ExportTo HTML              

# Scan with App creds
$SecureClientSecret = ConvertTo-SecureString "<secret>" -AsPlainText -Force     
Invoke-Monkey365 -TenantId <tenant-id> -ClientId <client-id> -ClientSecret $SecureClientSecret -Instance Azure -Collect All -ExportTo HTML              
```

### [ScoutSuite](https://github.com/nccgroup/ScoutSuite)

Scout Suite gathers configuration data for manual inspection and highlights risk areas. It's a multi-cloud security-auditing tool, which enables security posture assessment of cloud environments.

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install scoutsuite
scout --help

# Use --cli flag to use az cli credentials
# Use --user-account to have scout prompt for user credentials
# Use --user-account-browser to launch a browser to login
# Use --service-principal to have scout prompt for app credentials

python scout.py azure --cli
```


### [Azure-MG-Sub-Governance-Reporting](https://github.com/JulianHayward/Azure-MG-Sub-Governance-Reporting)

It's a powershell script that helps you to **visualize all the resources and permissions inside a Management Group and the Entra ID** tenant and find security misconfigurations.

It works using the Az PowerShell module, so any authentication supported by this tool is supported by the tool.

```bash
import-module Az
.\AzGovVizParallel.ps1 -ManagementGroupId <management-group-id> [-SubscriptionIdWhitelist <subscription-id>] 
```


## Automated Post-Exploitation tools

### [**ROADRecon**](https://github.com/dirkjanm/ROADtools)

The enumeration of ROADRecon offers information about the configuration of Entra ID, like users, groups, roles, conditional access policies...

```bash
cd ROADTools
pipenv shell
# Login with user creds
roadrecon auth -u test@corp.onmicrosoft.com -p "Welcome2022!"
# Login with app creds
roadrecon auth --as-app --client "<client-id>" --password "<secret>" --tenant "<tenant-id>"
roadrecon gather
roadrecon gui
```

### [**AzureHound**](https://github.com/BloodHoundAD/AzureHound)

AzureHound is the BloodHound collector for Microsoft Entra ID and Azure. It is a single static Go binary for Windows/Linux/macOS that talks directly to:
- Microsoft Graph (Entra ID directory, M365) and
- Azure Resource Manager (ARM) control plane (subscriptions, resource groups, compute, storage, key vault, app services, AKS, etc.)

Key traits
- Runs from anywhere on the public internet against tenant APIs (no internal network access required)
- Outputs JSON for BloodHound CE ingestion to visualize attack paths across identities and cloud resources
- Default User-Agent observed: azurehound/v2.x.x

Authentication options
- Username + password: -u <upn> -p <password>
- Refresh token: --refresh-token <rt>
- JSON Web Token (access token): --jwt <jwt>
- Service principal secret: -a <appId> -s <secret>
- Service principal certificate: -a <appId> --cert <cert.pem> --key <key.pem> [--keypass <pass>]

Examples
```bash
# Full tenant collection to file using different auth flows
## User creds
azurehound list -u "<user>@<tenant>" -p "<pass>" -t "<tenant-id|domain>" -o ./output.json

## Use an access token (JWT) from az cli for Graph
JWT=$(az account get-access-token --resource https://graph.microsoft.com -o tsv --query accessToken)
azurehound list --jwt "$JWT" -t "<tenant-id>" -o ./output.json

## Use a refresh token (e.g., from device code flow)
azurehound list --refresh-token "<refresh_token>" -t "<tenant-id>" -o ./output.json

## Service principal secret
azurehound list -a "<client-id>" -s "<secret>" -t "<tenant-id>" -o ./output.json

## Service principal certificate
azurehound list -a "<client-id>" --cert "/path/cert.pem" --key "/path/key.pem" -t "<tenant-id>" -o ./output.json

# Targeted discovery
azurehound list users -t "<tenant-id>" -o users.json
azurehound list groups -t "<tenant-id>" -o groups.json
azurehound list roles -t "<tenant-id>" -o roles.json
azurehound list role-assignments -t "<tenant-id>" -o role-assignments.json

# Azure resources via ARM
azurehound list subscriptions -t "<tenant-id>" -o subs.json
azurehound list resource-groups -t "<tenant-id>" -o rgs.json
azurehound list virtual-machines -t "<tenant-id>" -o vms.json
azurehound list key-vaults -t "<tenant-id>" -o kv.json
azurehound list storage-accounts -t "<tenant-id>" -o sa.json
azurehound list storage-containers -t "<tenant-id>" -o containers.json
azurehound list web-apps -t "<tenant-id>" -o webapps.json
azurehound list function-apps -t "<tenant-id>" -o funcapps.json
```

What gets queried
- Graph endpoints (examples):
  - /v1.0/organization, /v1.0/users, /v1.0/groups, /v1.0/roleManagement/directory/roleDefinitions, directoryRoles, owners/members
- ARM endpoints (examples):
  - management.azure.com/subscriptions/.../providers/Microsoft.Storage/storageAccounts
  - .../Microsoft.KeyVault/vaults, .../Microsoft.Compute/virtualMachines, .../Microsoft.Web/sites, .../Microsoft.ContainerService/managedClusters

Preflight behavior and endpoints
- Each azurehound list <object> typically performs these test calls before enumeration:
  1) Identity platform: login.microsoftonline.com
  2) Graph: GET https://graph.microsoft.com/v1.0/organization
  3) ARM: GET https://management.azure.com/subscriptions?api-version=...
- Cloud environment base URLs differ for Government/China/Germany. See constants/environments.go in the repo.

ARM-heavy objects (less visible in Activity/Resource logs)
- The following list targets predominantly use ARM control plane reads: automation-accounts, container-registries, function-apps, key-vaults, logic-apps, managed-clusters, management-groups, resource-groups, storage-accounts, storage-containers, virtual-machines, vm-scale-sets, web-apps.
- These GET/list operations are typically not written to Activity Logs; data-plane reads (e.g., *.blob.core.windows.net, *.vault.azure.net) are covered by Diagnostic Settings at the resource level.

OPSEC and logging notes
- Microsoft Graph Activity Logs are not enabled by default; enable and export to SIEM to gain visibility of Graph calls. Expect the Graph preflight GET /v1.0/organization with UA azurehound/v2.x.x.
- Entra ID non-interactive sign-in logs record the identity platform auth (login.microsoftonline.com) used by AzureHound.
- ARM control-plane read/list operations are not recorded in Activity Logs; many azurehound list operations against resources won’t appear there. Only data-plane logging (via Diagnostic Settings) will capture reads to service endpoints.
- Defender XDR GraphApiAuditEvents (preview) can expose Graph calls and token identifiers but may lack UserAgent and have limited retention.

Tip: When enumerating for privilege paths, dump users, groups, roles, and role assignments, then ingest in BloodHound and use prebuilt cypher queries to surface Global Administrator/Privileged Role Administrator and transitive escalation via nested groups and RBAC assignments.

Launch the BloodHound web with `curl -L https://ghst.ly/getbhce | docker compose -f - up` and import the `output.json` file. Then, in the EXPLORE tab, in the CYPHER section you can see a folder icon that contains pre-built queries.

### [**MicroBurst**](https://github.com/NetSPI/MicroBurst)

MicroBurst includes functions and scripts that support Azure Services discovery, weak configuration auditing, and post exploitation actions such as credential dumping. It is intended to be used during penetration tests where Azure is in use.

```bash
Import-Module .\MicroBurst.psm1
Import-Module .\Get-AzureDomainInfo.ps1
Get-AzureDomainInfo -folder MicroBurst -Verbose
```

### [**PowerZure**](https://github.com/hausec/PowerZure)

PowerZure was created out of the need for a framework that can both perform reconnaissance and exploitation of Azure, EntraID, and the associated resources.

It uses the **Az PowerShell** module, so any authentication supported by this tool is supported by the tool.

```bash
# Login
Import-Module Az
Connect-AzAccount

# Clone and import PowerZure
git clone https://github.com/hausec/PowerZure
cd PowerZure
ipmo ./Powerzure.psd1
Invoke-Powerzure -h # Check all the options

# Info Gathering (read)
Get-AzureCurrentUser # Get current user
Get-AzureTarget # What can you access to
Get-AzureUser -All # Get all users
Get-AzureSQLDB -All # Get all SQL DBs
Get-AzureAppOwner # Owners of apps in Entra
Show-AzureStorageContent -All # List containers, shared and tables
Show-AzureKeyVaultContent -All # List all contents in key vaults


# Operational (write)
Set-AzureUserPassword -Password <password> -Username <username> # Change password
Set-AzureElevatedPrivileges # Get permissions from Global Administrator in EntraID to User Access Administrator in Azure RBAC.
New-AzureBackdoor -Username <username> -Password <password>
Invoke-AzureRunCommand -Command <command> -VMName <vmname>
[...]
```

### [**GraphRunner**](https://github.com/dafthack/GraphRunner/wiki/Invoke%E2%80%90GraphRunner)

GraphRunner is a post-exploitation toolset for interacting with the Microsoft Graph API. It provides various tools for performing reconnaissance, persistence, and pillaging of data from a Microsoft Entra ID (Azure AD) account.

```bash
#A good place to start is to authenticate with the Get-GraphTokens module. This module will launch a device-code login, allowing you to authenticate the session from a browser session. Access and refresh tokens will be written to the global $tokens variable. To use them with other GraphRunner modules use the Tokens flag (Example. Invoke-DumpApps -Tokens $tokens)
Import-Module .\GraphRunner.ps1
Get-GraphTokens

#This module gathers information about the tenant including the primary contact info, directory sync settings, and user settings such as if users have the ability to create apps, create groups, or consent to apps.
Invoke-GraphRecon -Tokens $tokens -PermissionEnum

#A module to dump conditional access policies from a tenant.
Invoke-GraphRecon -Tokens $tokens -PermissionEnum

#A module to dump conditional access policies from a tenant.
Invoke-DumpCAPS -Tokens $tokens -ResolveGuids

#This module helps identify malicious app registrations. It will dump a list of Azure app registrations from the tenant including permission scopes and users that have consented to the apps. Additionally, it will list external apps that are not owned by the current tenant or by Microsoft's main app tenant. This is a good way to find third-party external apps that users may have consented to.
Invoke-DumpApps -Tokens $tokens

#Gather the full list of users from the directory.
Get-AzureADUsers -Tokens $tokens -OutFile users.txt

#Create a list of security groups along with their members.
Get-SecurityGroups -AccessToken $tokens.access_token

#Gets groups that may be able to be modified by the current user
Get-UpdatableGroups -Tokens $tokens

#Finds dynamic groups and displays membership rules
Get-DynamicGroups -Tokens $tokens

#Gets a list of SharePoint site URLs visible to the current user
Get-SharePointSiteURLs -Tokens $tokens

#This module attempts to locate mailboxes in a tenant that have allowed other users to read them. By providing a userlist the module will attempt to access the inbox of each user and display if it was successful. The access token needs to be scoped to Mail.Read.Shared or Mail.ReadWrite.Shared for this to work.
Invoke-GraphOpenInboxFinder -Tokens $tokens -Userlist users.txt

#This module attempts to gather a tenant ID associated with a domain.
Get-TenantID -Domain

#Runs Invoke-GraphRecon, Get-AzureADUsers, Get-SecurityGroups, Invoke-DumpCAPS, Invoke-DumpApps, and then uses the default_detectors.json file to search with Invoke-SearchMailbox, Invoke-SearchSharePointAndOneDrive, and Invoke-SearchTeams.
Invoke-GraphRunner -Tokens $tokens
```

### [Stormspotter](https://github.com/Azure/Stormspotter)

Stormspotter creates an “attack graph” of the resources in an Azure subscription. It enables red teams and pentesters to visualize the attack surface and pivot opportunities within a tenant, and supercharges your defenders to quickly orient and prioritize incident response work.

**Unfortunately, it looks unmantained**.

```bash
# Start Backend
cd stormspotter\backend\
pipenv shell
python ssbackend.pyz

# Start Front-end
cd stormspotter\frontend\dist\spa\
quasar.cmd serve -p 9091 --history

# Run Stormcollector
cd stormspotter\stormcollector\
pipenv shell
az login -u test@corp.onmicrosoft.com -p Welcome2022!
python stormspotter\stormcollector\sscollector.pyz cli
# This will generate a .zip file to upload in the frontend (127.0.0.1:9091)
```

## References
- [Cloud Discovery With AzureHound (Unit 42)](https://unit42.paloaltonetworks.com/threat-actor-misuse-of-azurehound/)
- [AzureHound repository](https://github.com/SpecterOps/AzureHound)
- [BloodHound repository](https://github.com/SpecterOps/BloodHound)
- [AzureHound Community Edition Flags](https://bloodhound.specterops.io/collect-data/ce-collection/azurehound-flags)
- [AzureHound constants/environments.go](https://github.com/SpecterOps/AzureHound/blob/main/constants/environments.go)
- [AzureHound client/storage_accounts.go](https://github.com/SpecterOps/AzureHound/blob/main/client/storage_accounts.go)
- [AzureHound client/roles.go](https://github.com/SpecterOps/AzureHound/blob/main/client/roles.go)

{{#include ../../banners/hacktricks-training.md}}

