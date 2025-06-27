@description('Container App Environment name')
param name string

@description('Location for Container App Environment')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

@description('Application Insights connection string')
@secure()
param applicationInsightsConnectionString string

// Extract workspace ID and get shared key separately
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    daprAIConnectionString: applicationInsightsConnectionString
    vnetConfiguration: {
      internal: false
    }
    zoneRedundant: false
  }
}

output id string = containerAppEnvironment.id
output name string = containerAppEnvironment.name
output defaultDomain string = containerAppEnvironment.properties.defaultDomain
