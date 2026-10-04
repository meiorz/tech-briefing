param(
  [Parameter(Mandatory)]
  [ValidatePattern('^[^@\s]+@[^@\s]+\.[^@\s]+$')]
  [string]$RecipientAddress,

  [string]$SenderAddress = "DoNotReply@601f7fef-0b4b-4d38-b74d-9f6f1310b629.azurecomm.net",
  [string]$ResourceGroup = "rg-tech-briefing",
  [string]$Location = "westus3"
)
$ErrorActionPreference = "Stop"

if ($RecipientAddress -like "your-address@*") {
  throw "RecipientAddress is still the placeholder; pass your real address."
}

az account show --query id -o tsv | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Not logged in to Azure. Run: az login" }

$params = @(
  "senderAddress=$SenderAddress"
  "recipientAddress=$RecipientAddress"
  "location=$Location"
)
# A new custom role definition can take a moment to replicate before it can be
# assigned (RoleDefinitionDoesNotExist), so retry once after a pause.
$outputs = $null
foreach ($attempt in 1..2) {
  $json = az deployment group create -g $ResourceGroup -f "$PSScriptRoot\main.bicep" -p $params --query "properties.outputs" -o json
  if ($LASTEXITCODE -eq 0) { $outputs = $json | ConvertFrom-Json; break }
  if ($attempt -eq 1) { Write-Host "Deployment failed; retrying in 30s (role replication)..."; Start-Sleep 30 }
}
if (-not $outputs) { throw "Deployment failed." }
$outputs

# Earlier versions granted the broad built-in role; Incremental deployments never remove it.
$legacy = az role assignment list --assignee $outputs.principalId.value --scope $outputs.acsId.value `
  --role "Communication and Email Service Owner" --query "[].id" -o tsv
if ($legacy) {
  Write-Host "Removing legacy 'Communication and Email Service Owner' assignment from the app identity"
  az role assignment delete --ids $legacy
  if ($LASTEXITCODE -ne 0) { throw "Could not remove the legacy role assignment." }
}
