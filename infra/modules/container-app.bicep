@description('Container App name')
param name string

@description('Location for Container App')
param location string = resourceGroup().location

@description('Environment name for tagging')
param environmentName string

@description('Container App Environment ID')
param containerAppEnvironmentId string

@description('User Assigned Managed Identity ID')
param managedIdentityId string

@description('Container Registry ID')
param containerRegistryId string

@description('AI Foundry Project connection string')
@secure()
param aiFoundryProjectConnectionString string

@description('AI Search endpoint')
param aiSearchEndpoint string

@description('Storage Account name')
param storageAccountName string

// Extract container registry name from resource ID
var containerRegistryName = last(split(containerRegistryId, '/'))

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: {
    'azd-env-name': environmentName
    'azd-service-name': 'software-architecture-recommender'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: managedIdentityId
        }
      ]
      secrets: [
        {
          name: 'ai-project-connection-string'
          value: aiFoundryProjectConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'software-architecture-recommender'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'AZURE_AI_PROJECT_CONNECTION_STRING'
              secretRef: 'ai-project-connection-string'
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: 'https://${containerRegistryName}.openai.azure.com/'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: 'gpt-4'
            }
            {
              name: 'AZURE_AI_SEARCH_ENDPOINT'
              value: aiSearchEndpoint
            }
            {
              name: 'AZURE_AI_SEARCH_INDEX_NAME'
              value: 'cw-architectures-index'
            }
            {
              name: 'AZURE_BLOB_STORAGE_ACCOUNT_NAME'
              value: storageAccountName
            }
            {
              name: 'AZURE_BLOB_CONTAINER_NAME'
              value: 'documents'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 10
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '30'
              }
            }
          }
        ]
      }
    }
  }
}

output id string = containerApp.id
output name string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output imageName string = '${containerRegistryName}.azurecr.io/software-architecture-recommender'
