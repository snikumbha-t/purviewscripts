# uc_probe.py

# Lists Unified Catalog governance domains (and optionally their roles)

# Env: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, PURVIEW_ACCOUNT_NAME



import os, sys, time

import requests

from azure.identity import ClientSecretCredential




TENANT  = "1234"

CLIENT  = "1234"
SECRET = "1234"

ACC = "1234"  # e.g. contoso-pv



LIST_ROLES = True  # set False if you only want domains

TIMEOUT = 30



if not all([TENANT, CLIENT, SECRET, ACC]):

   print("Missing one of: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, PURVIEW_ACCOUNT_NAME", file=sys.stderr)

   sys.exit(1)



BASES = [

   f"https://{ACC}.purview.azure.com",

   f"https://{ACC}-api.purview-service.microsoft.com"  # fallback

]

SCOPE = "https://purview.azure.net/.default"



cred = ClientSecretCredential(TENANT, CLIENT, SECRET)

def headers():

   token = cred.get_token(SCOPE).token

   return {"Authorization": f"Bearer {token}", "Accept": "application/json"}



def get(path):

   last = None

   for base in BASES:

       url = f"{base}{path}"

       r = requests.get(url, headers=headers(), timeout=TIMEOUT)

       if r.status_code == 404:

           last = r

           continue

       return r, base

   return last, BASES[-1]



print(f"Trying bases: {', '.join(BASES)}")

r, used = get("/ucgovernance/api/governanceDomains")

if r is None:

   print("No response from server.", file=sys.stderr); sys.exit(1)



if r.status_code == 404:

   print("404 on governanceDomains endpoint. Either UC governance isn’t enabled on this account, "

         "or the account name is wrong.", file=sys.stderr)

   sys.exit(2)



r.raise_for_status()

domains = r.json() if r.text else []

print(f"Using base: {used}")

print(f"Found {len(domains)} governance domains.\n")



if not domains:

   print("No domains visible to this app. Check account name and app permissions in UC.", file=sys.stderr)

   sys.exit(3)



for d in domains:

   print(f"- {d.get('displayName')} ({d.get('id')})")



if LIST_ROLES:

   print("\nDomain roles:")

   for d in domains:

       dom_id = d.get("id")

       rr, used = get(f"/ucgovernance/api/governanceDomains/{dom_id}/roles")

       if rr.status_code == 404:

           print(f"  {d.get('displayName')} -> 404 roles (endpoint mismatch or no access)")

           continue

       rr.raise_for_status()

       roles = rr.json() if rr.text else []

       print(f"  {d.get('displayName')}: {[r.get('displayName') for r in roles]}")