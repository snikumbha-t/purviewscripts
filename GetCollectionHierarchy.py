import requests
from collections import defaultdict

# === CONFIGURATION ===
tenant_id = "1234"
client_id = "1234"
client_secret = "1234"
purview_account_name = "1234"

# === AUTHENTICATION ===
def get_access_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://purview.azure.net/.default"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# === LIST ALL COLLECTIONS ===
def list_all_collections(account_name, token):
    url = f"https://{account_name}.purview.azure.com/account/collections?api-version=2019-11-01-preview"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

# === BUILD HIERARCHY ===
def build_hierarchy(collections):
    tree = defaultdict(list)
    names = {}
    for col in collections:
        name = col.get("name")
        friendly_name = col.get("friendlyName", "")
        parent = col.get("parentCollectionName", None)
        tree[parent].append(name)
        names[name] = friendly_name
    return tree, names
# === PRINT HIERARCHY ===
def print_hierarchy(tree, names, node=None, level=0):
    children = tree.get(node, [])
    for child in children:
        print("  " * level + f"- {child} (Friendly: {names.get(child, '')})")
        print_hierarchy(tree, names, child, level + 1)

# === MAIN ===
if __name__ == "__main__":
    token = get_access_token(tenant_id, client_id, client_secret)
    collections = list_all_collections(purview_account_name, token)
    tree, names = build_hierarchy(collections)

    print("\nPurview Collection Hierarchy:")
    print_hierarchy(tree, names)
