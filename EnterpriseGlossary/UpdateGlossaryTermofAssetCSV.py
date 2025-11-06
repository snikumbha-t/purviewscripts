import os
import csv
import requests
from azure.identity import ClientSecretCredential

# ===== CONFIGURATION =====
TENANT_ID = "1234"
CLIENT_ID = "1234"
CLIENT_SECRET = "1234"
ACCOUNT_NAME = "1234"
SCOPE = "https://purview.azure.net/.default"
API_VERSION = "2023-09-01"
CSV_FILE = "glossayupdatev2.csv"
LOG_FILE = "assignment_log.csv"

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
    if resp.status_code == 404:
        return None
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
        return False
    term_data = resp.json()
    assigned_entities = term_data.get("assignedEntities", [])
    return any(e.get("guid") == entity_guid for e in assigned_entities)

# ===== ASSIGN GLOSSARY TERM TO ENTITY =====
def assign_term_to_entity(term_guid, entity_guid, headers):
    url = f"https://{ACCOUNT_NAME}.purview.azure.com/datamap/api/atlas/v2/glossary/terms/{term_guid}/assignedEntities?api-version={API_VERSION}"
    body = [{"guid": entity_guid, "typeName": "column"}]
    return requests.post(url, headers=headers, json=body)

# ===== MAIN EXECUTION =====
def main():
    headers = get_auth_headers()
    success = skipped = failed = 0

    with open(LOG_FILE, "w", newline='', encoding='utf-8') as log_f:
        log_writer = csv.writer(log_f)
        log_writer.writerow(["asset_guid", "target_column", "term_guid", "status", "message"])

        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                asset_guid = row["asset_guid"].strip()
                target_column = row["target_column"].strip()
                term_guids_raw = row["TERM_GUIDS"].strip().replace('"', '')
                term_guids = [t.strip() for t in term_guids_raw.split(",") if t.strip()]

                entity_json = fetch_asset_details(asset_guid, headers)
                if not entity_json:
                    msg = f"Asset {asset_guid} not found (404)"
                    print(f"❌ {msg}")
                    for term_guid in term_guids:
                        log_writer.writerow([asset_guid, target_column, term_guid, "FAILED", msg])
                    failed += len(term_guids)
                    continue

                referred_entities = entity_json.get("referredEntities", {})
                all_columns = find_columns(entity_json, referred_entities)
                target_guid = next((guid for name, guid in all_columns if name.strip().lower() == target_column.lower()), None)

                if not target_guid:
                    msg = f"Column '{target_column}' not found"
                    print(f"❌ {msg}")
                    for term_guid in term_guids:
                        log_writer.writerow([asset_guid, target_column, term_guid, "FAILED", msg])
                    failed += len(term_guids)
                    continue

                for term_guid in term_guids:
                    if is_term_already_assigned(term_guid, target_guid, headers):
                        msg = "Already assigned"
                        print(f"⚠️ {msg}: {term_guid}")
                        log_writer.writerow([asset_guid, target_column, term_guid, "SKIPPED", msg])
                        skipped += 1
                        continue

                    resp = assign_term_to_entity(term_guid, target_guid, headers)
                    if resp.status_code == 200:
                        msg = "Assigned successfully"
                        print(f"✅ {msg}: {term_guid}")
                        log_writer.writerow([asset_guid, target_column, term_guid, "SUCCESS", msg])
                        success += 1
                    elif resp.status_code == 204:
                        msg = "No content (possibly already assigned)"
                        print(f"⚠️ {msg}: {term_guid}")
                        log_writer.writerow([asset_guid, target_column, term_guid, "SKIPPED", msg])
                        skipped += 1
                    else:
                        msg = f"Failed with status {resp.status_code}"
                        print(f"❌ {msg}: {term_guid}")
                        log_writer.writerow([asset_guid, target_column, term_guid, "FAILED", msg])
                        failed += 1

    print("\n📊 Summary:")
    print(f"✅ Success: {success}")
    print(f"⚠️ Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"Log file saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()