from azure.identity import ClientSecretCredential
from azure.purview.catalog import PurviewCatalogClient
import requests

# Replace these with environment variables
TENANT_ID = "1234"
CLIENT_ID = "1234"
CLIENT_SECRET = "1234"
PURVIEW_ACCOUNT_NAME = "1234"
PURVIEW_ENDPOINT = f"https://{PURVIEW_ACCOUNT_NAME}.purview.azure.com"

# Authenticate
credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
token = credential.get_token("https://purview.azure.net/.default").token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

def list_governance_domains():
    url = f"{PURVIEW_ENDPOINT}/catalog/api/governanceDomains"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch governance domains: {response.status_code}")
        return []
    domains = response.json().get("value", [])
    if not domains:
        print("[INFO] No governance domains found.")
    return domains

def get_domain_roles(domain_id):
    url = f"{PURVIEW_ENDPOINT}/catalog/api/governanceDomains/{domain_id}/roles"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch roles for domain {domain_id}: {response.status_code}")
        return []
    roles = response.json().get("value", [])
    if not roles:
        print(f"[INFO] No roles found for domain {domain_id}.")
    return roles

def find_user_domains(user_object_id):
    accessible_domains = []
    domains = list_governance_domains()
    if not domains:
        print("[INFO] No domains to check.")
        return accessible_domains
    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name")
        print(f"[DEBUG] Checking domain: {domain_name} (ID: {domain_id})")

        roles = get_domain_roles(domain_id)
        if not roles:
            continue

        found = False
        for role in roles:
            principals = role.get("principals", [])
            if not principals:
                print(f"[INFO] No principals found in role '{role.get('name')}' for domain '{domain_name}'.")
                continue

            for principal in principals:
                if principal.get("objectId") == user_object_id:
                    print(f"[SUCCESS] Found access for user {user_object_id} in domain '{domain_name}' via role '{role.get('name')}'.")
                    accessible_domains.append(domain_name)
                    found = True
                    break
            if found:
                break

        if not found:
            print(f"[INFO] User {user_object_id} has no access in domain '{domain_name}'.")

    return accessible_domains

if __name__ == "__main__":
    user_id = input("Enter User Object ID: ").strip()
    domains = find_user_domains(user_id)
    print(f"\nUser {user_id} has access to the following governance domains:")
    if domains:
        for d in domains:
            print(f"- {d}")
    else:
        print("[INFO] No governance domain access found for this user.")