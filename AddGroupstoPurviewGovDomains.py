import os, csv, sys, time, re, requests, argparse

from typing import Dict, List, Optional

from azure.identity import ClientSecretCredential



# ======= CONFIG =======

CSV_PATH = r"users1.csv"    # <-- change this

DRY_RUN = True                             # set False to apply

SLEEP_SECONDS = 0.0

TIMEOUT = 30

RETRY = 2



# Auth via env vars (same as your working script)

TENANT_ID  = "1234"

CLIENT_ID  = "1234"

CLIENT_SECRET = "1234"

ACCOUNT_NAME  = "1234"  # e.g. contoso-pv



# Use the SAME base model you used in your working script

# Option A: provide account name and we’ll build https://<name>.purview.azure.com





# Option B (preferred for private/explicit hosts): set a full base URL and we’ll use it as-is

# e.g. PURVIEW_BASE_URL=https://pvdew-dap-datacatalog-prd-uks-01.purview.azure.com

BASE_URL_OVERRIDE = "1234"



SCOPE = "https://purview.azure.net/.default"

# ======================



GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")



def die(msg, code=1):

   print(f"ERROR: {msg}", file=sys.stderr); sys.exit(code)



def is_guid(s: str) -> bool:

   return bool(GUID_RE.match((s or "").strip()))



def get_base() -> str:

   if BASE_URL_OVERRIDE:

       return BASE_URL_OVERRIDE.rstrip("/")

   if not ACCOUNT_NAME:

       die("Set PURVIEW_BASE_URL or ACCOUNT_NAME.")

   # Construct default base URL from the account name. For private hosts,
   # set PURVIEW_BASE_URL in the environment or pass --base-url.
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



def headers(cred: ClientSecretCredential) -> Dict[str,str]:

   tok = cred.get_token(SCOPE).token

   return {"Authorization": f"Bearer {tok}", "Accept": "application/json", "Content-Type": "application/json"}



def http(session: requests.Session, method: str, url: str, hdrs: Dict[str,str], **kw):

   for attempt in range(RETRY+1):

       r = session.request(method, url, headers=hdrs, timeout=TIMEOUT, **kw)

       if r.status_code in (429,500,502,503,504) and attempt < RETRY:

           time.sleep(2*(attempt+1)); continue

       return r



def read_csv_rows(path: str) -> List[Dict[str,str]]:

   required = ["governance domain name","governance domain id","entra id group id","role name"]

   rows: List[Dict[str,str]] = []

   with open(path, newline="", encoding="utf-8-sig") as f:

       reader = csv.DictReader(f)

       if not reader.fieldnames:

           die("CSV has no headers.")

       norm = {h:(h or "").strip().lower() for h in reader.fieldnames}

       rev = {}; [rev.setdefault(v,k) for k,v in norm.items()]

       missing = [h for h in required if h not in rev]

       if missing: die(f"CSV missing header(s): {', '.join(missing)}. Found: {', '.join(reader.fieldnames)}")

       for row in reader:

           rows.append({

               "domain_name": row[rev["governance domain name"]].strip(),

               "domain_id":   row[rev["governance domain id"]].strip(),

               "group_id":    row[rev["entra id group id"]].strip(),

               "role_name":   row[rev["role name"]].strip(),

           })

   return rows



# ---- UC helpers ----

def list_domains(base, session, cred):

   r = http(session, "GET", f"{base}/ucgovernance/api/governanceDomains", headers(cred))

   if r.status_code == 404:

       die("GovernanceDomains endpoint returned 404. UC not enabled on this account or wrong base URL.")

   r.raise_for_status()

   return r.json() if r.text else []



def list_domain_roles(base, session, cred, domain_id):

   r = http(session, "GET", f"{base}/ucgovernance/api/governanceDomains/{domain_id}/roles", headers(cred))

   if r.status_code == 404:

       raise RuntimeError(f"Domain not found: {domain_id}")

   r.raise_for_status()

   return r.json() if r.text else []



def get_role(base, session, cred, domain_id, role_id):

   r = http(session, "GET", f"{base}/ucgovernance/api/governanceDomains/{domain_id}/roles/{role_id}", headers(cred))

   r.raise_for_status()

   return r.json()



def update_role(base, session, cred, domain_id, role_id, body):

   r = http(session, "PUT", f"{base}/ucgovernance/api/governanceDomains/{domain_id}/roles/{role_id}", headers(cred), json=body)

   r.raise_for_status()

   return r.json() if r.text else {}



def resolve_domain_id_by_name(base, session, cred, name) -> Optional[str]:

   for d in list_domains(base, session, cred):

       if (d.get("displayName") or "").strip().lower() == (name or "").strip().lower():

           return d.get("id")

   return None



def resolve_role_id_by_name(base, session, cred, domain_id, role_name) -> str:

   for r in list_domain_roles(base, session, cred, domain_id):

       if (r.get("displayName") or "").strip().lower() == role_name.strip().lower():

           return r.get("id")

   raise ValueError(f"Role '{role_name}' not found on domain {domain_id}")



def ensure_group_in_role(base, session, cred, domain_id, role_id, group_id, dry_run: bool):

   role = get_role(base, session, cred, domain_id, role_id)

   members = role.get("members", []) or []

   if any(m.get("id") == group_id for m in members):

       return "already-present"

   role["members"] = members + [{"id": group_id, "type": "Group"}]

   if dry_run: return "would-add"

   update_role(base, session, cred, domain_id, role["id"], role)

   return "added"



def main():

   if not os.path.exists(CSV_PATH): die(f"CSV not found: {CSV_PATH}")

   base = get_base()

   cred = credential()

   session = requests.Session()



   rows = read_csv_rows(CSV_PATH)

   if not rows: die("CSV has no data rows.")



   print(f"Base: {base}")

   print(f"CSV: {CSV_PATH}")

   print(f"DRY_RUN: {DRY_RUN}\n")



   ok = changed = skipped = errs = 0



   # Light connectivity sanity (also proves UC enabled)

   try:

       doms = list_domains(base, session, cred)

       if not doms:

           print("No governance domains visible to this app. Check UC permissions.", file=sys.stderr)

   except Exception as e:

       die(f"Cannot list governance domains: {e}")



   for i, r in enumerate(rows, 1):

       name = r["domain_name"]; dom_id = r["domain_id"]; role_name = r["role_name"]; group = r["group_id"]

       print(f"[{i}/{len(rows)}] DomainName='{name}' DomainId='{dom_id}' Role='{role_name}' Group='{group}'")



       if not is_guid(group):

           print(f"  → FAIL: group id must be GUID. Got: {group}", file=sys.stderr); errs += 1; continue



       # Validate/resolve domain id

       resolved = dom_id

       try:

           list_domain_roles(base, session, cred, resolved)

       except Exception:

           by_name = resolve_domain_id_by_name(base, session, cred, name)

           if not by_name:

               print("  → FAIL: domain not found by id or name. Check account or permissions.", file=sys.stderr)

               errs += 1; continue

           resolved = by_name

           print(f"    Resolved domain id: {resolved}")



       try:

           role_id = resolve_role_id_by_name(base, session, cred, resolved, role_name)

           outcome = ensure_group_in_role(base, session, cred, resolved, role_id, group, DRY_RUN)

           if outcome == "already-present":

               print("  → SKIP: already present"); skipped += 1

           elif outcome == "would-add":

               print("  → DRY-RUN: would add"); ok += 1

           else:

               print("  → OK: added"); ok += 1; changed += 1

           if SLEEP_SECONDS: time.sleep(SLEEP_SECONDS)

       except requests.HTTPError as he:

           body = getattr(he, "response", None)

           print(f"  → FAIL (HTTP {body.status_code if body else '??'}): {body.text if body else he}", file=sys.stderr)

           errs += 1

       except Exception as ex:

           print(f"  → FAIL: {ex}", file=sys.stderr); errs += 1



   print("\nSummary:")

   print(f"  processed: {len(rows)}")

   print(f"  success:   {ok}")

   print(f"  changed:   {changed}")

   print(f"  skipped:   {skipped}")

   print(f"  errors:    {errs}")



if __name__ == "__main__":

   main()