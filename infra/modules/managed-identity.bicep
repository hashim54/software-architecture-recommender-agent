@description('Managed Identity name')
param name string

@description('Location for Managed Identity')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
  }
}

output id string = managedIdentity.id
output principalId string = managedIdentity.properties.principalId
output clientId string = managedIdentity.properties.clientId
