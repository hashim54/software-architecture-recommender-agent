@description('Azure AI Foundry Project name')
param name string

@description('Location for Azure AI Foundry Project')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('AI Foundry Hub resource ID')
param aiFoundryHubId string

@description('Whether to use existing project')
param useExisting bool = false

resource aiFoundryProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = if (!useExisting) {
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
  kind: 'Project'
  properties: {
    friendlyName: '${name} Project'
    description: 'Azure AI Foundry Project for software architecture recommendations'
    hubResourceId: aiFoundryHubId
    publicNetworkAccess: 'Enabled'
    hbiWorkspace: false
    v1LegacyMode: false
  }
}

resource existingAiFoundryProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' existing = if (useExisting) {
  name: name
}

output id string = useExisting ? existingAiFoundryProject.id : aiFoundryProject.id
output name string = useExisting ? existingAiFoundryProject.name : aiFoundryProject.name
output connectionString string = useExisting
  ? 'https://${existingAiFoundryProject.name}.api.azureml.ms/api/projects/${existingAiFoundryProject.name}'
  : 'https://${aiFoundryProject.name}.api.azureml.ms/api/projects/${aiFoundryProject.name}'
