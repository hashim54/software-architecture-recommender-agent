@description('Azure AI Foundry Hub name')
param name string

@description('Location for Azure AI Foundry Hub')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Key Vault resource ID')
param keyVaultId string

@description('Storage Account resource ID')
param storageAccountId string

@description('Application Insights resource ID')
param applicationInsightsId string

@description('Container Registry resource ID')
param containerRegistryId string

@description('Whether to use existing hub')
param useExisting bool = false

resource aiFoundryHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = if (!useExisting) {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  kind: 'Hub'
  properties: {
    friendlyName: '${name} Hub'
    description: 'Azure AI Foundry Hub for software architecture recommendations'
    keyVault: keyVaultId
    storageAccount: storageAccountId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    publicNetworkAccess: 'Enabled'
    hbiWorkspace: false
    v1LegacyMode: false
  }
}

resource existingAiFoundryHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' existing = if (useExisting) {
  name: name
}

output id string = useExisting ? existingAiFoundryHub.id : aiFoundryHub.id
output name string = useExisting ? existingAiFoundryHub.name : aiFoundryHub.name
output openAiEndpoint string = useExisting
  ? 'https://${existingAiFoundryHub.name}.openai.azure.com/'
  : 'https://${aiFoundryHub.name}.openai.azure.com/'
