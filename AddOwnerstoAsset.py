import requests
from azure.identity import ClientSecretCredential

# === Configuration ===
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"


# Asset metadata
asset_guid = "d3c8ce39-bf4b-490d-91be-4df6f6f60000"
type_name = "databricks_table"
qualified_name = "databricks://2e7f178b-2b46-4694-bb18-1296aabed5ea/catalogs/dap_conform_prd_02/schemas/conformed_restricted/tables/__materialization_mat_3023c796_da90_45b8_b4fd_705f302ba410_enappsys_gb_da_border_price_1"
name = "__materialization_mat_3023c796_da90_45b8_b4fd_705f302ba410_enappsys_gb_da_border_price_1"

# Owners to add (Azure AD object IDs)
owners_to_add = [
    "eff63f94-0ddc-4944-a973-9a59ca56a8e7",
    "4397e7a2-cd46-409d-9882-2cb99dceaaf2"
]

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

# Endpoint to update entity
entity_update_url = f"https://{purview_account_name}.purview.azure.com/datamap/api/atlas/v2/entity"

# Payload to update owner attribute
entity_payload = {
    "entity": {
        "guid": asset_guid,
        "typeName": type_name,
        "attributes": {
            "qualifiedName": qualified_name,
            "name": name,
            "owner": ",".join(owners_to_add)
        }
    },
    "referredEntities": {}
}

# Send the update request
response = requests.post(entity_update_url, headers=headers, json=entity_payload)

# Check response
if response.status_code == 200:
    print("✅ Owners updated successfully.")
else:
    print(f"❌ Failed to update owners. Status code: {response.status_code}")
    print(response.text)