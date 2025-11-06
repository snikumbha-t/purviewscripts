import requests
from azure.identity import ClientSecretCredential

# Credentials
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"
query_text = "__materialization_mat_3023c796_da90_45b8_b4fd_705f302ba410_enappsys_da_market_price_data_1"

# Auth
credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
token = credential.get_token("https://purview.azure.net/.default").token

# Request
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
search_url = f"https://{purview_account_name}.purview.azure.com/api/atlas/v2/search/basic"
params = {
    "limit": 1,
    "offset": 0,
    "query": query_text
}

# Call API
response = requests.get(search_url, headers=headers, params=params)

# Handle errors
if response.status_code == 403:
    print("❌ Forbidden: Check your role assignments in Purview.")
elif response.status_code == 404:
    print("❌ Not Found: Asset may not exist or query format may be incorrect.")
else:
    response.raise_for_status()
    data = response.json()
    if "entities" in data and data["entities"]:
        guid = data["entities"][0]["guid"]
        print(f"✅ Asset GUID: {guid}")
    else:
        print("⚠️ No matching asset found.")