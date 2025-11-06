import csv
from unifiedcatalogpy.client import UnifiedCatalogClient
from azure.identity import ClientSecretCredential
# Initialize the credential
credential1 = ClientSecretCredential(
    tenant_id="1234",
    client_id="1234",
    client_secret="1234"
)
# Initialize the Unified Catalog Client
_client = UnifiedCatalogClient(
    account_id="1234",
    credential=credential1
)


# Read the CSV and create glossary terms
with open("FinalcsvB1.csv", mode="r", encoding="ISO-8859-1") as file:
    reader = csv.DictReader(file)
    for row in reader:
        term_data = {}
        # Required fields
        if row["name"]:
            term_data["name"] = row["name"]
        if row["description"]:
            term_data["description"] = row["description"]
        if row["status"]:
            term_data["status"] = row["status"]
        if row["governance_domain_id"]:
            term_data["governance_domain_id"] = row["governance_domain_id"]
        # Optional acronyms
        if row["acronyms"]:
            acronyms = [ac.strip() for ac in row["acronyms"].split(",") if ac.strip()]
            if acronyms:
                term_data["acronyms"] = acronyms
        # Owners
        owners = []
        if row["owners1"]:
            owners.append({"id": row["owners1"]})
        if row["owners2"]:
            owners.append({"id": row["owners2"]})
        if owners:
            term_data["owners"] = owners
        # Create the glossary term
        
        term = _client.create_term(**term_data)
        # Print the created term
      
        #print(term)
 