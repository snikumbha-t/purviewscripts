# Import the library
from unifiedcatalogpy.client import UnifiedCatalogClient
 
from azure.identity import DefaultAzureCredential
 
from azure.identity import ClientSecretCredential
 
credential1 = ClientSecretCredential(
        tenant_id="1234", client_id="1234", client_secret="1234"
      )
# purview_name = "1234"
_client = UnifiedCatalogClient(account_id="1234", credential=credential1)
 
# Create the Unified Catalog Client
 
# Interact with the client
 
 
###############################
# Create new glossary term
terms = [
  {
    "name": "s",
    "description": "Costs 2022.",
    "status": "Published",
    "governance_domain_id": "f07c33e77dcb73",
    "owners": [
      {"id": "75ac54ffe-edbcf6729619"},
      {"id": "f28186e1a85"}
    ]
  },
  {
    "name": "2-1Forecast",
    "description": "2-14 Dr i .e. \"4\" for 4 Daast.",
    "status": "Published",
    "governance_domain_id": "bb925e-8e49-a7e60e849a11",
    "owners": [
      {"id": "ae6d3f2d-131f-47049e4"},
      {"id": "9e0d76b945c27e9d"}
    ]
  }
]

 
# Show the new glossary term

for term_data in terms:
    term = _client.delete_relationship(**term_data)
    print(term)
