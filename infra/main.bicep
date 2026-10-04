@description('Region for all resources')
param location string = resourceGroup().location

@description('Existing Communication Services resource in this resource group')
param acsName string = 'acs-briefing-meiorz'

@description('GUID of the "Communication and Email Service Owner" role')
param acsRoleId string

param senderAddress string
param recipientAddress string

var token = uniqueString(resourceGroup().id)
var storageName = 'st${token}'
var deployContainer = 'app-package'
var storageSuffix = environment().suffixes.storage

// Built-in role definition IDs (identical in every Azure tenant)
var storageRoleIds = [
  'b7e6dc6d-f1e8-4753-8033-0f276bb0955b' // Storage Blob Data Owner
  '974c5e8b-45b9-4653-ba55-5f855dd0fb88' // Storage Queue Data Contributor
  '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3' // Storage Table Data Contributor
]
var metricsPublisherRoleId = '3913510d-42f4-4e42-8a64-420c390055eb' // Monitoring Metrics Publisher

// ---------- Storage (host state + seenitems table + deployment package) ----------
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowSharedKeyAccess: false      // no keys: identity only
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource packageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: deployContainer
}

resource tableService 'Microsoft.Storage/storageAccounts/tableServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource seenTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: 'seenitems'
}

// ---------- Monitoring ----------
resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-briefing-${token}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: 1 }   // hard cap protects your credit
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-briefing-${token}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
    DisableLocalAuth: true           // Entra ID only, no ingestion key
  }
}

// ---------- Existing ACS resource ----------
resource acs 'Microsoft.Communication/communicationServices@2023-04-01' existing = {
  name: acsName
}

// ---------- Flex Consumption Function App ----------
resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: 'plan-briefing-${token}'
  location: location
  kind: 'functionapp'
  sku: { name: 'FC1', tier: 'FlexConsumption' }
  properties: { reserved: true }     // Linux
}

resource app 'Microsoft.Web/sites@2024-04-01' = {
  name: 'func-briefing-${token}'
  location: location
  kind: 'functionapp,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: 'https://${storage.name}.blob.${storageSuffix}/${deployContainer}'
          authentication: { type: 'SystemAssignedIdentity' }
        }
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 40
        instanceMemoryMB: 512
      }
      runtime: { name: 'python', version: '3.12' }
    }
    siteConfig: {
      appSettings: [
        { name: 'AzureWebJobsStorage__credential', value: 'managedidentity' }
        { name: 'AzureWebJobsStorage__blobServiceUri', value: 'https://${storage.name}.blob.${storageSuffix}' }
        { name: 'AzureWebJobsStorage__queueServiceUri', value: 'https://${storage.name}.queue.${storageSuffix}' }
        { name: 'AzureWebJobsStorage__tableServiceUri', value: 'https://${storage.name}.table.${storageSuffix}' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
        { name: 'APPLICATIONINSIGHTS_AUTHENTICATION_STRING', value: 'Authorization=AAD' }
        { name: 'BRIEFING_TABLES_ENDPOINT', value: 'https://${storage.name}.table.${storageSuffix}' }
        { name: 'ACS_ENDPOINT', value: 'https://${acs.properties.hostName}' }
        { name: 'BRIEFING_SENDER', value: senderAddress }
        { name: 'BRIEFING_RECIPIENT', value: recipientAddress }
      ]
    }
  }
}

// ---------- Role assignments for the app's managed identity ----------
resource storageRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for roleId in storageRoleIds: {
  name: guid(storage.id, app.id, roleId)
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleId)
    principalId: app.identity.principalId
    principalType: 'ServicePrincipal'
  }
}]

resource metricsRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appInsights.id, app.id, metricsPublisherRoleId)
  scope: appInsights
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleId)
    principalId: app.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource acsRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acs.id, app.id, acsRoleId)
  scope: acs
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acsRoleId)
    principalId: app.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output functionAppName string = app.name
output storageAccountName string = storage.name