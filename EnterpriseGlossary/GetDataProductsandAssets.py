import requests

# Azure AD and Purview configuration
import os
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
data_product_id = "388bcf52-6632-4b55-9724-518258b8d9b9"
api_version = "2025-09-15-preview"

# Step 1: Get Azure AD token
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
token_data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://purview.azure.net/.default"
}
token_response = requests.post(token_url, data=token_data)
access_token = token_response.json().get("access_token")

# Step 2: Get DataProduct details
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
data_product_url = f"https://{purview_account_name}.purview.azure.com/datagovernance/catalog/dataProducts/{data_product_id}?api-version={api_version}"
dp_response = requests.get(data_product_url, headers=headers)

if dp_response.status_code == 200:
    data_product = dp_response.json()
    print("DataProduct retrieved successfully:")
    print(data_product)

    # Step 3: Get associated DataAssets
    entity_type = "DataAsset"
    relationships_url = f"https://{purview_account_name}.purview.azure.com/datagovernance/catalog/dataProducts/{data_product_id}/relationships?api-version={api_version}&entityType={entity_type}"
    rel_response = requests.get(relationships_url, headers=headers)

    if rel_response.status_code == 200:
        relationships = rel_response.json()
        print("\nAssociated DataAssets:")
        for rel in relationships.get("value", []):
            print(f"- ID: {rel.get('entityId')}, Type: {rel.get('entityType')}")
    else:
        print(f"Failed to retrieve relationships. Status code: {rel_response.status_code}")
        print(rel_response.text)
else:
    print(f"Failed to retrieve DataProduct. Status code: {dp_response.status_code}")
    print(dp_response.text)