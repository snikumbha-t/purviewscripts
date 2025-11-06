import os
import requests
import csv
from azure.identity import ClientSecretCredential

# ===== CONFIG =====
TENANT_ID = "1234"
CLIENT_ID = "1234"
CLIENT_SECRET = "1234"
ACCOUNT_NAME = "1234"
SCOPE = "https://purview.azure.net/.default"
OUTPUT_FILE = "glossary_terms.csv"

# ===== AUTH =====
cred = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
token = cred.get_token(SCOPE).token
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

BASE_URL = f"https://{ACCOUNT_NAME}.purview.azure.com/catalog/api/atlas/v2"

# ===== STEP 1: Get all glossaries =====
glossary_url = f"{BASE_URL}/glossary"
glossary_resp = requests.get(glossary_url, headers=headers)
glossary_resp.raise_for_status()
glossaries = glossary_resp.json()

# ===== STEP 2: For each glossary, get all terms with pagination =====
all_terms = []
for glossary in glossaries:
    glossary_guid = glossary.get("guid")
    glossary_name = glossary.get("name") or glossary.get("displayName") or "Unknown Glossary"
    offset = 0
    limit = 100
    while True:
        terms_url = f"{BASE_URL}/glossary/{glossary_guid}/terms?limit={limit}&offset={offset}"
        resp = requests.get(terms_url, headers=headers)
        resp.raise_for_status()
        terms = resp.json()
        if not terms:
            break
        for term in terms:
            term_name = term.get("name") or term.get("displayText") or "Unnamed Term"
            term_guid = term.get("guid", "")
            all_terms.append([glossary_name, term_name, term_guid, glossary_guid])
        offset += limit

# ===== STEP 3: Write to CSV =====
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Glossary Name", "Term Name", "Term GUID", "Glossary GUID"])
    writer.writerows(all_terms)

print(f"✅ Exported {len(glossaries)} glossaries and {len(all_terms)} terms to {OUTPUT_FILE}")
