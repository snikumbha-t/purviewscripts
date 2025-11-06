import os
import requests
from azure.identity import ClientSecretCredential

# ===== CONFIG =====
TENANT_ID = "1234"
CLIENT_ID = "1234"
CLIENT_SECRET = "1234"
ACCOUNT_NAME = "1234"
SCOPE = "https://purview.azure.net/.default"
BASE_URL = f"https://{ACCOUNT_NAME}.purview.azure.com"

API_VERSIONS = [
    "2024-09-01-preview",
    "2024-05-01-preview",
    "2023-09-01-preview"
]

# ===== AUTH =====
cred = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
token = cred.get_token(SCOPE).token
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

print(f"Testing UC Governance API connectivity for account: {ACCOUNT_NAME}\n")

for version in API_VERSIONS:
    url = f"{BASE_URL}/ucgovernance/api/governanceDomains?api-version={version}"
    print(f"Trying API version: {version}")
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            print(f"✅ SUCCESS with {version}")
            domains = resp.json()
            print(f"Found {len(domains)} governance domains:")
            for d in domains:
                print(f" - {d.get('displayName')} (ID: {d.get('id')})")
            break
        elif resp.status_code == 404:
            print(f"❌ 404: Endpoint not available for {version}")
        else:
            print(f"❌ HTTP {resp.status_code}: {resp.text[:200]}...")
    except Exception as ex:
        print(f"❌ ERROR: {ex}")
    print("-" * 50)
else:
    print("\nNo API version succeeded. UC Governance API might not be enabled for this account.")