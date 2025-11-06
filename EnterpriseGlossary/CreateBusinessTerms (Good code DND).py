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
  "name": " ",
  "description": " ",
  "status": "Published",
  "governance_domain_id": "727a5374",
  "owners": [
    {
      "id": "75ac5478"
    },
    {
      "id": "5f9ff29c"
    }
  ]
}
]

 


 
# Show the new glossary term

for term_data in terms:
    term = _client.create_term(**term_data)
    print(term)
