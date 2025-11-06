# Import the library
import os
from unifiedcatalogpy.client import UnifiedCatalogClient
 
from azure.identity import ClientSecretCredential
 
credential1 = ClientSecretCredential(
                tenant_id="1234", client_id="1234", client_secret="1234"
            )
# purview_name = "pview-dap-datacatalog-prd-uks-01"
_client = UnifiedCatalogClient(account_id="1234", credential=credential1)
 
# Create the Unified Catalog Client
 
# Interact with the client
domains = _client.get_governance_domains()
###############################
# Create new glossary term

 
# Show the new glossary term
print(domains)