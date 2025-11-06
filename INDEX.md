Repository index — key scripts

This project contains many small scripts for working with an Azure Purview
(Unified Catalog) instance. Below is a short index of important scripts and
what they do. Several scripts use the `unifiedcatalogpy` client to interact
with the Purview service.

Top-level scripts
-----------------
- `add_groups_to_roles.py` — adds groups to roles (sanitized)
- `AddGroupstoPurviewGovDomains.py` — helper for adding groups to governance domains
- `AddOwnerstoAsset.py` — add owners to an asset
- `CreateGlossaryLoop.py` — loop over CSV to create glossary entries
- `DeleteAssociatedDataAssets.py` — delete associated assets
- `DeleteRelationship.py` — delete relationships between entities
- `FinalAddUserstoGovDomains.py` — final script to add users to governance domains
- `tetsconnectivity.py` — connectivity/probe script

EnterpriseGlossary/ (important)
--------------------------------
- `CreateBusinessTerms.py` — create business (glossary) terms (uses unifiedcatalogpy)
- `CreateDataProducts.py` — create data products (redacted)
- `GetDataProductsandAssets.py` — retrieve products and related assets
- `FindAssetID.py` — lookup asset IDs
- `GetGovDomains.py` — export/import governance domains
- `UpdateGlossaryTermofAssetCSV.py` — batch update glossary terms on assets

Notes
-----
- Many scripts call into `unifiedcatalogpy.client.UnifiedCatalogClient`.
  Ensure `unifiedcatalogpy` (or `azure-purview-catalog` where applicable)
  and `azure-identity` are installed in your virtual environment.
- Credentials in this repository have been intentionally replaced with the
  placeholder string "1234". Replace them securely before running any
  script against a real service.
- CSV files have been sanitized (data rows removed) in this copy. If you
  need to re-populate them for local testing, do so carefully and keep
  sensitive data out of version control.

If you'd like, I can expand this index with one-line descriptions for
all scripts and add usage examples for each.
