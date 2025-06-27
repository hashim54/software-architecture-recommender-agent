@description('Application Insights name')
param name string

@description('Location for Application Insights')
param location string = resourceGroup().location

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

@description('Environment name for tagging')
param environmentName string

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

output id string = applicationInsights.id
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
output connectionString string = applicationInsights.properties.ConnectionString
