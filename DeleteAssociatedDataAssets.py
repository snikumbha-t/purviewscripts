import requests

# Azure AD and Purview configuration
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
data_product_id = "388bcf52-6632-4b55-9724-518258b8d9b9"
api_version = "2025-09-15-preview"
entity_type = "DataAsset"

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

# Step 2: Get associated DataAssets
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
relationships_url = f"https://{purview_account_name}.purview.azure.com/datagovernance/catalog/dataProducts/{data_product_id}/relationships?api-version={api_version}&entityType={entity_type}"
rel_response = requests.get(relationships_url, headers=headers)

if rel_response.status_code == 200:
    relationships = rel_response.json().get("value", [])
    print(f"\n Found {len(relationships)} associated DataAssets.\n")

    for rel in relationships:
        asset_id = rel.get("entityId")

        # Step 3: Check if asset exists
        asset_url = f"https://{purview_account_name}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{asset_id}"
        asset_response = requests.get(asset_url, headers=headers)

        if asset_response.status_code == 200:
            asset = asset_response.json()
            asset_name = asset.get("entity", {}).get("attributes", {}).get("name", "Unknown")
            print(f"Asset Name: {asset_name}")
            print(f"Asset GUID: {asset_id}")
            confirm = input(" Do you want to delete this asset? (Yes/No): ").strip().lower()

            if confirm == "yes":
                delete_url = f"https://{purview_account_name}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{asset_id}"
                delete_response = requests.delete(delete_url, headers=headers)

                if delete_response.status_code == 200:
                    print(f" Asset deleted: {asset_name} ({asset_id})\n")
                else:
                    print(f" Failed to delete asset: {asset_name} ({asset_id})")
                    print(delete_response.text)
            else:
                print(f"⏭ Skipped deletion for asset: {asset_name} ({asset_id})\n")
        else:
            print(f" Asset not found or already deleted: GUID {asset_id}")
            print(asset_response.text)
else:
    print(f" Failed to retrieve relationships. Status code: {rel_response.status_code}")
    print(rel_response.text)