# add_groups_to_roles.py
import os, csv, sys
from azure.identity import ClientSecretCredential
from unifiedcatalogpy.client import UnifiedCatalogClient
from uc_roles_ext import UnifiedCatalogRoles
 
# env: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
TENANT  = "1234"

CLIENT  = "1234"
SECRET = "1234"

ACCOUNT_ID = "1234"  # e.g. contoso-pv

 
# IMPORTANT: unifiedcatalogpy expects Purview **account_id** (the bit before -api in the Atlas endpoint)
# Example: https://<account_id>-api.purview-service.microsoft.com/catalog  => account_id is <account_id>

 
# If your estate resolves the public host, this builds: https://<account_id>.purview.azure.com
BASE_URL = f"https://{ACCOUNT_ID}.purview.azure.com"
 
CSV_PATH = r"users1.csv"   # governance domain name,id,entra id group id,role name
DRY_RUN = True
 
if not all([TENANT, CLIENT, SECRET, ACCOUNT_ID]):
   print("Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and ACCOUNT_ID", file=sys.stderr); sys.exit(1)
 
cred = ClientSecretCredential(TENANT, CLIENT, SECRET)
 
def token_getter():
   return cred.get_token("https://purview.azure.net/.default").token
 
# unifiedcatalogpy client (kept for other features you may use)
uc = UnifiedCatalogClient(account_id=ACCOUNT_ID, credential=cred)
 
# roles helper (raw endpoints for roles)
roles = UnifiedCatalogRoles(BASE_URL, token_getter)
 
def rows(csv_path):
   with open(csv_path, newline="", encoding="utf-8-sig") as f:
       import csv
       reader = csv.DictReader(f)
       for r in reader:
           yield {
               "domain_name": r.get("governance domain name","").strip(),
               "domain_id":   r.get("governance domain id","").strip(),
               "group_id":    r.get("entra id group id","").strip(),
               "role_name":   r.get("role name","").strip(),
           }
 
for r in rows(CSV_PATH):
   dom = r["domain_id"] or r["domain_name"]
   role = r["role_name"]
   gid  = r["group_id"]
   print(f"Domain={dom} | Role={role} | Group={gid}")
   if DRY_RUN:
       print("  → DRY-RUN: would add (skipping network write)")
       continue
   # Assumes you pass the domain **id** (GUID). If you only have the name, resolve it first via uc.get_governance_domains().
   outcome = roles.add_group_to_role(domain_id=r["domain_id"], role_display_name=role, group_object_id=gid)
   print(f"  → {outcome}")
 
 