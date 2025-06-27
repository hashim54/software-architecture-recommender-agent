targetScope = 'resourceGroup'

@description('The environment name. Used for resource naming.')
param environmentName string

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Resource token for unique naming')
param resourceToken string = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))

@description('Existing Azure AI Foundry Hub ID (optional)')
param existingAiFoundryHubId string = ''

@description('Existing Azure AI Foundry Project ID (optional)')
param existingAiFoundryProjectId string = ''

@description('Existing Azure AI Search service name (optional)')
param existingAiSearchName string = ''

@description('Existing Azure Storage Account name (optional)')
param existingStorageAccountName string = ''

@description('Existing Container Registry name (optional)')
param existingContainerRegistryName string = ''

// Add azd-env-name tag to resource group
resource rgTags 'Microsoft.Resources/tags@2022-09-01' = {
  name: 'default'
  properties: {
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Variables for resource naming
var prefix = 'arc'
var suffix = take(resourceToken, 8) // Limit suffix to 8 characters

// Log Analytics Workspace
module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'logAnalytics'
  params: {
    name: '${prefix}-logs-${suffix}'
    location: location
    environmentName: environmentName
  }
}

// Application Insights
module applicationInsights 'modules/application-insights.bicep' = {
  name: 'applicationInsights'
  params: {
    name: '${prefix}-ai-${suffix}'
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
    environmentName: environmentName
  }
}

// Key Vault
module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  params: {
    name: '${prefix}kv${suffix}'
    location: location
    environmentName: environmentName
  }
}

// Container Registry
module containerRegistry 'modules/container-registry.bicep' = {
  name: 'containerRegistry'
  params: {
    name: empty(existingContainerRegistryName) ? '${prefix}cr${suffix}' : existingContainerRegistryName
    location: location
    environmentName: environmentName
    useExisting: !empty(existingContainerRegistryName)
  }
}

// User Assigned Managed Identity
module managedIdentity 'modules/managed-identity.bicep' = {
  name: 'managedIdentity'
  params: {
    name: '${prefix}-id-${suffix}'
    location: location
    environmentName: environmentName
  }
}

// Storage Account
module storageAccount 'modules/storage-account.bicep' = {
  name: 'storageAccount'
  params: {
    name: empty(existingStorageAccountName) ? 'st${suffix}' : existingStorageAccountName
    location: location
    environmentName: environmentName
    principalId: managedIdentity.outputs.principalId
    useExisting: !empty(existingStorageAccountName)
  }
}

// Azure AI Search
module aiSearch 'modules/ai-search.bicep' = {
  name: 'aiSearch'
  params: {
    name: empty(existingAiSearchName) ? '${prefix}-srch-${suffix}' : existingAiSearchName
    location: location
    environmentName: environmentName
    principalId: managedIdentity.outputs.principalId
    useExisting: !empty(existingAiSearchName)
  }
}

// Azure AI Foundry Hub
module aiFoundryHub 'modules/ai-foundry-hub.bicep' = {
  name: 'aiFoundryHub'
  params: {
    name: empty(existingAiFoundryHubId) ? '${prefix}-hub-${suffix}' : existingAiFoundryHubId
    location: location
    environmentName: environmentName
    keyVaultId: keyVault.outputs.id
    storageAccountId: storageAccount.outputs.id
    applicationInsightsId: applicationInsights.outputs.id
    containerRegistryId: containerRegistry.outputs.id
    useExisting: !empty(existingAiFoundryHubId)
  }
}

// Azure AI Foundry Project
module aiFoundryProject 'modules/ai-foundry-project.bicep' = {
  name: 'aiFoundryProject'
  params: {
    name: empty(existingAiFoundryProjectId) ? '${prefix}-project-${suffix}' : existingAiFoundryProjectId
    location: location
    environmentName: environmentName
    aiFoundryHubId: aiFoundryHub.outputs.id
    useExisting: !empty(existingAiFoundryProjectId)
  }
}

// Container App Environment
module containerAppEnvironment 'modules/container-app-environment.bicep' = {
  name: 'containerAppEnvironment'
  params: {
    name: '${prefix}-env-${suffix}'
    location: location
    environmentName: environmentName
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
    applicationInsightsConnectionString: applicationInsights.outputs.connectionString
  }
}

// Container App
module containerApp 'modules/container-app.bicep' = {
  name: 'containerApp'
  params: {
    name: '${prefix}-app-${suffix}'
    location: location
    environmentName: environmentName
    containerAppEnvironmentId: containerAppEnvironment.outputs.id
    managedIdentityId: managedIdentity.outputs.id
    containerRegistryId: containerRegistry.outputs.id
    aiFoundryProjectConnectionString: aiFoundryProject.outputs.connectionString
    aiSearchEndpoint: aiSearch.outputs.endpoint
    storageAccountName: storageAccount.outputs.name
  }
}

// Grant Container Registry pull permissions to managed identity
module acrPermissions 'modules/acr-permissions.bicep' = {
  name: 'acrPermissions'
  params: {
    containerRegistryName: containerRegistry.outputs.name
    principalId: managedIdentity.outputs.principalId
  }
}

// Outputs
output RESOURCE_GROUP_ID string = resourceGroup().id
output AZURE_AI_PROJECT_CONNECTION_STRING string = aiFoundryProject.outputs.connectionString
output AZURE_OPENAI_ENDPOINT string = aiFoundryHub.outputs.openAiEndpoint
output AZURE_OPENAI_DEPLOYMENT_NAME string = 'gpt-4'
output AZURE_AI_SEARCH_ENDPOINT string = aiSearch.outputs.endpoint
output AZURE_AI_SEARCH_INDEX_NAME string = 'cw-architectures-index'
output AZURE_BLOB_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_BLOB_CONTAINER_NAME string = 'documents'
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = containerAppEnvironment.outputs.name
output AZURE_CONTAINER_APP_NAME string = containerApp.outputs.name
output AZURE_CONTAINER_APP_FQDN string = containerApp.outputs.fqdn
output SERVICE_API_ENDPOINTS string = 'https://${containerApp.outputs.fqdn}'
