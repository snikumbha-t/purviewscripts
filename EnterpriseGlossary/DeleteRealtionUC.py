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
#relation = _client.delete_relationship(
   # entity_type= "DataProduct",
   # entity_id= "81b4b707-33ef-496e-b4f3-6bf6f6f60000",
   # target_entity_id= "388bcf52-6632-4b55-9724-518258b8d9b9",
   # relationship_type= "Related"
#)

deleted = _client.get_data_product_by_id("388bcf52-6632-4b55-9724-518258b8d9b9")
 
# Show the new glossary term
print(deleted)
