# add_groups_to_roles_single.py

# One file: defines UnifiedCatalogRoles and runs the CSV processor.

# Auth: client ID/secret (env vars). No Graph. CSV must include group objectId.



import os, csv, sys, time, re, requests

from typing import Dict, Any, List, Optional

from azure.identity import ClientSecretCredential



# ======= CONFIG =======

CSV_PATH = r"Users1.csv"   # <-- set your CSV path

DRY_RUN = True                             # set False to apply

SLEEP_SECONDS = 0.0

TIMEOUT = 30

RETRY = 2




TENANT_ID  = "1234"

CLIENT_ID  = "1234"

CLIENT_SECRET = "1234"



# Either set PURVIEW_BASE_URL (full host) or PURVIEW_ACCOUNT_NAME (we build https://<name>.purview.azure.com)

BASE_URL = os.environ.get("PURVIEW_BASE_URL")

ACCOUNT_NAME = "1234"


SCOPE = "https://purview.azure.net/.default"

GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")



def die(msg, code=1):

   print(f"ERROR: {msg}", file=sys.stderr); sys.exit(code)



def is_guid(s: str) -> bool:

   return bool(GUID_RE.match((s or "").strip()))



def get_base() -> str:

   if BASE_URL:

       return BASE_URL.rstrip("/")

   if not ACCOUNT_NAME:

       die("Set PURVIEW_BASE_URL or PURVIEW_ACCOUNT_NAME.")

   return f"https://{ACCOUNT_NAME}.purview.azure.com"



def credential() -> ClientSecretCredential:

   missing = [k for k,v in {

       "AZURE_TENANT_ID": TENANT_ID,

       "AZURE_CLIENT_ID": CLIENT_ID,

       "AZURE_CLIENT_SECRET": CLIENT_SECRET

   }.items() if not v]

   if missing:

       die(f"Missing env vars: {', '.join(missing)}")

   return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)



def token_getter_factory(cred: ClientSecretCredential):

   def _get():

       return cred.get_token(SCOPE).token

   return _get



class UnifiedCatalogRoles:

   def __init__(self, account_base_url: str, token_getter):

       self.base = account_base_url.rstrip("/")

       self._token = token_getter

       self._session = requests.Session()



   def _headers(self):

       return {

           "Authorization": f"Bearer {self._token()}",

           "Accept": "application/json",

           "Content-Type": "application/json"

       }



   def _http(self, method: str, url: str, **kw):

       for attempt in range(RETRY+1):

           r = self._session.request(method, url, headers=self._headers(), timeout=TIMEOUT, **kw)

           if r.status_code in (429,500,502,503,504) and attempt < RETRY:

               time.sleep(2*(attempt+1)); continue

           return r



   def list_domains(self):

       r = self._http("GET", f"{self.base}/ucgovernance/api/governanceDomains")

       return r



   def list_roles(self, domain_id: str):

       r = self._http("GET", f"{self.base}/ucgovernance/api/governanceDomains/{domain_id}/roles")

       return r



   def get_role(self, domain_id: str, role_id: str):

       r = self._http("GET", f"{self.base}/ucgovernance/api/governanceDomains/{domain_id}/roles/{role_id}")

       r.raise_for_status()

       return r.json()



   def update_role(self, domain_id: str, role_id: str, body: dict):

       r = self._http("PUT", f"{self.base}/ucgovernance/api/governanceDomains/{domain_id}/roles/{role_id}", json=body)

       r.raise_for_status()

       return r.json() if r.text else {}



   def add_group_to_role(self, domain_id: str, role_display_name: str, group_object_id: str):

       # list roles

       lr = self.list_roles(domain_id)

       if lr.status_code == 404:

           raise RuntimeError(f"Domain not found or UC governance API not enabled. HTTP 404 at {self.base}")

       lr.raise_for_status()

       roles = lr.json() if lr.text else []

       role = next((r for r in roles if (r.get('displayName') or '').strip().lower() == role_display_name.strip().lower()), None)

       if not role:

           raise ValueError(f"Role '{role_display_name}' not found on domain {domain_id}")

       # get & update

       full = self.get_role(domain_id, role['id'])

       members = full.get('members', []) or []

       if any(m.get('id') == group_object_id for m in members):

           return 'already-present'

       full['members'] = members + [{"id": group_object_id, "type": "Group"}]

       if DRY_RUN:

           return 'would-add'

       self.update_role(domain_id, role['id'], full)

       return 'added'



def read_csv_rows(path: str) -> List[Dict[str,str]]:

   required = ["governance domain name","governance domain id","entra id group id","role name"]

   rows: List[Dict[str,str]] = []

   with open(path, newline="", encoding="utf-8-sig") as f:

       reader = csv.DictReader(f)

       if not reader.fieldnames: die("CSV has no headers.")

       norm = {h:(h or "").strip().lower() for h in reader.fieldnames}

       rev = {}; [rev.setdefault(v,k) for k,v in norm.items()]

       miss = [h for h in required if h not in rev]

       if miss: die(f"CSV missing header(s): {', '.join(miss)}. Found: {', '.join(reader.fieldnames)}")

       for row in reader:

           rows.append({

               "domain_name": row[rev["governance domain name"]].strip(),

               "domain_id":   row[rev["governance domain id"]].strip(),

               "group_id":    row[rev["entra id group id"]].strip(),

               "role_name":   row[rev["role name"]].strip(),

           })

   return rows



def main():

   if not os.path.exists(CSV_PATH): die(f"CSV not found: {CSV_PATH}")

   base = get_base()

   cred = credential()

   token_getter = token_getter_factory(cred)

   roles = UnifiedCatalogRoles(base, token_getter)



   # prove UC governance API exists

   probe = roles.list_domains()

   if probe.status_code == 404:

       die("GovernanceDomains endpoint returned 404. UC governance API is not enabled for this account or wrong base URL.")

   probe.raise_for_status()



   items = read_csv_rows(CSV_PATH)

   if not items: die("CSV has no data rows.")



   print(f"Base: {base}")

   print(f"CSV: {CSV_PATH}")

   print(f"DRY_RUN: {DRY_RUN}\n")



   ok = changed = skipped = errs = 0

   for i, r in enumerate(items, 1):

       name = r["domain_name"]; dom_id = r["domain_id"]; role_name = r["role_name"]; group = r["group_id"]

       print(f"[{i}/{len(items)}] DomainName='{name}' DomainId='{dom_id}' Role='{role_name}' Group='{group}'")

       if not is_guid(group):

           print(f"  → FAIL: group id must be GUID. Got: {group}", file=sys.stderr); errs += 1; continue

       try:

           outcome = roles.add_group_to_role(dom_id, role_name, group)

           if outcome == "already-present":

               print("  → SKIP: already present"); skipped += 1

           elif outcome == "would-add":

               print("  → DRY-RUN: would add"); ok += 1

           else:

               print("  → OK: added"); ok += 1; changed += 1

           if SLEEP_SECONDS: time.sleep(SLEEP_SECONDS)

       except requests.HTTPError as he:

           body = getattr(he, "response", None)

           print(f"  → FAIL (HTTP {body.status_code if body else '??'}): {body.text if body else he}", file=sys.stderr); errs += 1

       except Exception as ex:

           print(f"  → FAIL: {ex}", file=sys.stderr); errs += 1



   print("\nSummary:")

   print(f"  processed: {len(items)}")

   print(f"  success:   {ok}")

   print(f"  changed:   {changed}")

   print(f"  skipped:   {skipped}")

   print(f"  errors:    {errs}")



if __name__ == "__main__":

   main()

