
import requests

# Azure AD and Purview configuration
import os
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
asset_guid = "f7e047de-924b-4503-8502-98f6f6f60000"

# Get Azure AD token
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
token_data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://purview.azure.net/.default"
}
token_response = requests.post(token_url, data=token_data)
access_token = token_response.json().get("access_token")

# Get asset by GUID
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
asset_url = f"https://{purview_account_name}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{asset_guid}"
response = requests.get(asset_url, headers=headers)

# Output result
if response.status_code == 200:
    asset = response.json()
    print("Asset retrieved successfully:")
    print(asset)
else:
    print(f"Failed to retrieve asset. Status code: {response.status_code}")
    print(response.text)