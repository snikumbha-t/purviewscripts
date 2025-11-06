import requests
from azure.identity import ClientSecretCredential

# === Configuration ===
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"

asset_guid = "d3c8ce39-bf4b-490d-91be-4df6f6f60000"

# === Authentication ===
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)
token = credential.get_token("https://purview.azure.net/.default").token

# === API Request ===
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Endpoint to retrieve full metadata
metadata_url = f"https://{purview_account_name}.purview.azure.com/datamap/api/atlas/v2/entity/guid/{asset_guid}"

# Send the request
response = requests.get(metadata_url, headers=headers)

# Check response
if response.status_code == 200:
    metadata = response.json()
    entity = metadata.get("entity", {})
    attributes = entity.get("attributes", {})
    print("✅ Asset Metadata Retrieved Successfully")
    print(f"Type Name: {entity.get('typeName')}")
    print(f"Qualified Name: {attributes.get('qualifiedName')}")
    print(f"Name: {attributes.get('name')}")
    print(f"Owner: {attributes.get('owner')}")
else:
    print(f"❌ Failed to retrieve metadata. Status code: {response.status_code}")
    print(response.text)