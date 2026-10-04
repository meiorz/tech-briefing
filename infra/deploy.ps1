$rg = "rg-tech-briefing"
$acsRoleId = az role definition list --name "Communication and Email Service Owner" --query "[0].name" -o tsv
$params = @(
  "acsRoleId=$acsRoleId"
  "senderAddress=DoNotReply@601f7fef-0b4b-4d38-b74d-9f6f1310b629.azurecomm.net"
  "recipientAddress=your-address@gmail.com"
  "location=westus3"
)
az deployment group create -g $rg -f "$PSScriptRoot\main.bicep" -p $params --query "properties.outputs" -o json
