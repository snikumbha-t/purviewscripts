import requests

# Azure AD and Purview configuration
import os
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
asset_guid = "f7e047de-02-98f6f6f60000"

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

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 1: Get asset by GUID
asset_url = f"https://{purview_account_name}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{asset_guid}"
response = requests.get(asset_url, headers=headers)

def get_collection_hierarchy(collection_id):
    hierarchy = []
    while collection_id:
        url = f"https://{purview_account_name}.purview.azure.com/account/collections/{collection_id}?api-version=2019-11-01-preview"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to retrieve collection {collection_id}. Status code: {resp.status_code}")
            break
        data = resp.json()
        name = data.get("friendlyName") or data.get("name")
        hierarchy.insert(0, name)
        collection_id = data.get("parentCollectionId")  # Move up the chain
    # Add Purview account as root
    hierarchy.insert(0, purview_account_name)
    return " > ".join(hierarchy)

if response.status_code == 200:
    asset = response.json()
    asset_name = asset.get("entity", {}).get("attributes", {}).get("name") or asset.get("entity", {}).get("attributes", {}).get("qualifiedName")
    print(f"Asset name: {asset_name}")

    collection_id = asset.get("entity", {}).get("collectionId")
    if collection_id:
        hierarchy = get_collection_hierarchy(collection_id)
        print(f"Collection hierarchy: {hierarchy}")
    else:
        print("Collection ID not found in asset metadata.")
else:
    print(f"Failed to retrieve asset. Status code: {response.status_code}")
    print(response.text)