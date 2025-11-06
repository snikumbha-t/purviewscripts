# uc_roles_ext.py

# Lightweight extension for unifiedcatalogpy to manage governance-domain roles.



from typing import Any, Dict, List, Optional

import requests



UC_ROLES_BASE = "/ucgovernance/api/governanceDomains"



class UnifiedCatalogRoles:

   def __init__(self, account_base_url: str, token_getter):

       """

       account_base_url: e.g. https://<account>.purview.azure.com

       token_getter: a callable that returns a bearer token string (from the same credential you use for unifiedcatalogpy)

       """

       self.base = account_base_url.rstrip("/")

       self._token = token_getter

       self._session = requests.Session()



   def _headers(self) -> Dict[str, str]:

       return {

           "Authorization": f"Bearer {self._token()}",

           "Accept": "application/json",

           "Content-Type": "application/json"

       }



   def list_roles(self, domain_id: str) -> List[Dict[str, Any]]:

       url = f"{self.base}{UC_ROLES_BASE}/{domain_id}/roles"

       r = self._session.get(url, headers=self._headers(), timeout=30)

       r.raise_for_status()

       return r.json() if r.text else []



   def get_role(self, domain_id: str, role_id: str) -> Dict[str, Any]:

       url = f"{self.base}{UC_ROLES_BASE}/{domain_id}/roles/{role_id}"

       r = self._session.get(url, headers=self._headers(), timeout=30)

       r.raise_for_status()

       return r.json()



   def update_role(self, domain_id: str, role_id: str, body: Dict[str, Any]) -> Dict[str, Any]:

       url = f"{self.base}{UC_ROLES_BASE}/{domain_id}/roles/{role_id}"

       r = self._session.put(url, headers=self._headers(), json=body, timeout=30)

       r.raise_for_status()

       return r.json() if r.text else {}



   def add_group_to_role(self, domain_id: str, role_display_name: str, group_object_id: str) -> str:

       roles = self.list_roles(domain_id)

       role = next((r for r in roles if (r.get("displayName") or "").strip().lower() == role_display_name.strip().lower()), None)

       if not role:

           raise ValueError(f"Role '{role_display_name}' not found on domain {domain_id}")



       role_id = role["id"]

       full = self.get_role(domain_id, role_id)

       members = full.get("members", []) or []

       if any(m.get("id") == group_object_id for m in members):

           return "already-present"

       full["members"] = members + [{"id": group_object_id, "type": "Group"}]

       self.update_role(domain_id, role_id, full)

       return "added"