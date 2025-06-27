@description('Azure AI Search service name')
param name string

@description('Location for Azure AI Search')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Principal ID for managed identity role assignment')
param principalId string

@description('Whether to use existing search service')
param useExisting bool = false

resource aiSearchService 'Microsoft.Search/searchServices@2023-11-01' = if (!useExisting) {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    semanticSearch: 'free'
  }
}

resource existingAiSearchService 'Microsoft.Search/searchServices@2023-11-01' existing = if (useExisting) {
  name: name
}

// Grant Search Service Contributor role to managed identity for new service
resource searchServiceContributorRoleNew 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!useExisting) {
  name: guid(aiSearchService.id, principalId, 'Search Service Contributor')
  scope: aiSearchService
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    ) // Search Service Contributor
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// Grant Search Service Contributor role to managed identity for existing service
resource searchServiceContributorRoleExisting 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useExisting) {
  name: guid(existingAiSearchService.id, principalId, 'Search Service Contributor')
  scope: existingAiSearchService
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    ) // Search Service Contributor
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output id string = useExisting ? existingAiSearchService.id : aiSearchService.id
output name string = useExisting ? existingAiSearchService.name : aiSearchService.name
output endpoint string = useExisting
  ? 'https://${existingAiSearchService.name}.search.windows.net'
  : 'https://${aiSearchService.name}.search.windows.net'
