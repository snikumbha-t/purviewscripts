import os
import requests
from azure.identity import ClientSecretCredential

# ===== CONFIGURATION =====
TENANT_ID = "1234"
CLIENT_ID = "1234"
CLIENT_SECRET = "1234"
ACCOUNT_NAME = "1234"
SCOPE = "https://purview.azure.net/.default"
API_VERSION = "2023-09-01"

# ===== INPUTS =====
ASSET_GUID = "4f89eb8b-4cf5-4d7c-bcfb-6bf6f6f60000"
TARGET_COLUMN = "DIVISION"
TERM_GUIDS = [
    "d7463577-4be6-4dc4-aaba-328b219599d0",
    "b5863907-23c4-4763-adb6-652b39af7e1f"
]

# ===== AUTHENTICATION =====
def get_auth_headers():
    cred = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    token = cred.get_token(SCOPE).token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

# ===== FETCH ASSET DETAILS =====
def fetch_asset_details(asset_guid, headers):
    url = f"https://{ACCOUNT_NAME}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{asset_guid}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# ===== FIND COLUMNS =====
def find_columns(data, referred_entities):
    columns = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "columns" and isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        ref = referred_entities.get(item)
                        if ref and ref.get("typeName") == "column":
                            name = ref.get("attributes", {}).get("name", "Unnamed")
                            guid = ref.get("guid", item)
                            columns.append((name, guid))
                    elif isinstance(item, dict):
                        name = item.get("name") or item.get("displayText") or "Unnamed"
                        guid = item.get("guid") or item.get("id") or "Unknown GUID"
                        columns.append((name, guid))
            elif key == "typeName" and value == "column":
                name = data.get("attributes", {}).get("name", "Unnamed")
                guid = data.get("guid", "Unknown GUID")
                columns.append((name, guid))
            else:
                columns.extend(find_columns(value, referred_entities))
    elif isinstance(data, list):
        for item in data:
            columns.extend(find_columns(item, referred_entities))
    return columns

# ===== CHECK IF TERM IS ALREADY ASSIGNED =====
def is_term_already_assigned(term_guid, entity_guid, headers):
    url = f"https://{ACCOUNT_NAME}.purview.azure.com/datamap/api/atlas/v2/glossary/terms/{term_guid}?api-version={API_VERSION}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"⚠️ Could not verify existing assignments for term {term_guid}. Status: {resp.status_code}")
        return False
    term_data = resp.json()
    assigned_entities = term_data.get("assignedEntities", [])
    return any(e.get("guid") == entity_guid for e in assigned_entities)

# ===== ASSIGN GLOSSARY TERM TO ENTITY =====
def assign_term_to_entity(term_guid, entity_guid, headers):
    url = f"https://{ACCOUNT_NAME}.purview.azure.com/datamap/api/atlas/v2/glossary/terms/{term_guid}/assignedEntities?api-version={API_VERSION}"
    body = [
        {
            "guid": entity_guid,
            "typeName": "column"
        }
    ]
    resp = requests.post(url, headers=headers, json=body)
    return resp

# ===== MAIN EXECUTION =====
def main():
    headers = get_auth_headers()
    print("🔄 Fetching asset details...")
    entity_json = fetch_asset_details(ASSET_GUID, headers)
    referred_entities = entity_json.get("referredEntities", {})

    print("🔍 Searching for columns...")
    all_columns = find_columns(entity_json, referred_entities)

    if not all_columns:
        print("❌ No columns found in this asset.")
        return

    print("📋 Columns found:")
    for name, guid in all_columns:
        print(f"- {name} (GUID: {guid})")

    target_guid = next((guid for name, guid in all_columns if name.strip().lower() == TARGET_COLUMN.strip().lower()), None)

    if not target_guid:
        print(f"❌ Column '{TARGET_COLUMN}' not found.")
        return

    print(f"✅ Found column '{TARGET_COLUMN}' with GUID: {target_guid}")
    print("🔄 Assigning glossary terms...")

    for term_guid in TERM_GUIDS:
        print(f"🔄 Checking if term {term_guid} is already assigned...")
        if is_term_already_assigned(term_guid, target_guid, headers):
            print(f"⚠️ Term {term_guid} is already assigned to column '{TARGET_COLUMN}'")
            continue

        print(f"🔄 Assigning term {term_guid} to column '{TARGET_COLUMN}'...")
        resp = assign_term_to_entity(term_guid, target_guid, headers)
        if resp.status_code == 200:
            print(f"✅ Successfully assigned term {term_guid}")
        elif resp.status_code == 204:
            print(f"⚠️ Term {term_guid} may already be assigned or no content returned.")
        else:
            print(f"❌ Failed to assign term {term_guid}. Status: {resp.status_code}")
            print(resp.text)

if __name__ == "__main__":
    main()