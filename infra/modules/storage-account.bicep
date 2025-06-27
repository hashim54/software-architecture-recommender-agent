@description('Storage Account name')
param name string

@description('Location for Storage Account')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Principal ID for managed identity role assignment')
param principalId string

@description('Whether to use existing storage account')
param useExisting bool = false

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = if (!useExisting) {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource existingStorageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = if (useExisting) {
  name: name
}

// Create blob container for documents
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (!useExisting) {
  name: '${storageAccount.name}/default/documents'
  properties: {
    publicAccess: 'None'
  }
}

// Grant Storage Blob Data Contributor role to managed identity for new storage account
resource storageBlobDataContributorRoleNew 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!useExisting) {
  name: guid(storageAccount.id, principalId, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// Grant Storage Blob Data Contributor role to managed identity for existing storage account
resource storageBlobDataContributorRoleExisting 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useExisting) {
  name: guid(existingStorageAccount.id, principalId, 'Storage Blob Data Contributor')
  scope: existingStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output id string = useExisting ? existingStorageAccount.id : storageAccount.id
output name string = useExisting ? existingStorageAccount.name : storageAccount.name
output primaryEndpoints object = useExisting
  ? existingStorageAccount.properties.primaryEndpoints
  : storageAccount.properties.primaryEndpoints
