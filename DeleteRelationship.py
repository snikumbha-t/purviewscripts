import requests
# Azure AD and Purview configuration
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
data_product_id = "2d88c0a5-6f4a-44d4-8e54-2c6e8ef809fc"
entity_type = "DataAsset"
entity_id = "8e5d6b37-2ac2-480f-9cad-87908ba496b7"
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

# Step 2: Remove relationship
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
delete_url = f"https://{purview_account_name}.purview.azure.com/datagovernance/catalog/dataProducts/{data_product_id}/relationships?api-version={api_version}&entityType={entity_type}&entityId={entity_id}"
delete_response = requests.delete(delete_url, headers=headers)

# Step 3: Output result
if delete_response.status_code == 200:
    print(f"Relationship removed successfully for entity ID: {entity_id}")
else:
    print(f"Failed to remove relationship. Status code: {delete_response.status_code}")
    print(delete_response.text)