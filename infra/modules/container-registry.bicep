@description('Container Registry name')
param name string

@description('Location for Container Registry')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Whether to use existing registry')
param useExisting bool = false

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = if (!useExisting) {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
  }
}

resource existingContainerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = if (useExisting) {
  name: name
}

output id string = useExisting ? existingContainerRegistry.id : containerRegistry.id
output name string = useExisting ? existingContainerRegistry.name : containerRegistry.name
output loginServer string = useExisting
  ? existingContainerRegistry.properties.loginServer
  : containerRegistry.properties.loginServer
